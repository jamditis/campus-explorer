"""Build viewer/paths.json, the walkable path network the viewer routes on.

Reads OpenStreetMap for the area the campus tiles cover (the same OSM API calls and cache as
build_places.py), keeps the ways a person can walk (footways, paths, steps, crossings, pedestrian
areas and, at a cost, streets), joins them into one graph clipped to the campus, and finds the
building entrances. Ground heights for the slope check come from the USGS 3DEP 1 m bare-earth DEM
(the public 3DEPElevation image service). Standard library only.

Usage:
    python3 tools/places/build_paths.py --cache /some/dir/outside/the/repo
    python3 tools/places/build_paths.py --cache DIR --offline   # use cached responses only

Output (three.js metres, the frame of places.json):
    nodes      flat [x0, z0, x1, z1, ...], 0.1 m
    edges      [[a, b, flags, grade], ...]  flags: 1 steps, 2 steep, 4 street, 8 crossing
               grade: steepest 20 m stretch along the edge (end to end when shorter), percent,
               rounded; 0 on bridges; -1 where the DEM gave no height (unknown)
    entrances  [{"osm": "way/..", "node": i, "mapped": bool}, ...] for every building in places.json
               that the graph reaches; mapped is false where no entrance is in OSM and the point is
               a footway dead end or path point at the outline, else the nearest path (UNVERIFIED)

Housing (AGENTS.md rule 16): indoor ways and corridors are dropped everywhere, so routes end at a
building's entrance and never go inside.

Data (c) OpenStreetMap contributors, ODbL 1.0. Heights: USGS 3DEP, public domain.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_places as bp  # noqa: E402

DEM = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/getSamples"
FOOT = {"footway", "path", "pedestrian", "steps", "cycleway", "living_street", "track", "bridleway"}
STREET = {
    "residential",
    "service",
    "unclassified",
    "tertiary",
    "secondary",
    "primary",
    "road",
    "tertiary_link",
    "secondary_link",
    "primary_link",
}
NO = {"no", "private"}
SIMPLIFY_M = 0.6  # shape points closer than this to the straight run are dropped
STEEP_PCT = 8.33  # 1:12, the steepest ramp the ADA standards allow
GRADE_STEP_M = 10.0  # heights are sampled this far apart along each path
GRADE_RUN_M = 20.0  # slope is measured over stretches this long
SHORT_RUN_M = 2.0  # shorter edges count as level
MIN_PIECE_M = 60.0  # disconnected pieces shorter than this in total are dropped
ENTRANCE_REACH_M = 25.0  # how far from a building outline a path may be to count as its way in
DOOR_M = 6.0  # a path dead end this close to a building outline is taken as a door (UNVERIFIED)
WALL_M = 3.0  # any path point this close to the outline is taken as a way in too (UNVERIFIED)
SAMPLE_BATCH = 400


def walkable(tags: dict) -> int | None:
    """Edge flags for a way a person may walk on, or None."""
    hw = tags.get("highway")
    if (
        tags.get("indoor") == "yes"
        or hw == "corridor"
        or tags.get("level", "0") not in ("0", "0;1", "-1;0")
    ):
        return None
    if tags.get("foot") in NO or (
        tags.get("access") in NO and tags.get("foot") not in ("yes", "designated")
    ):
        return None
    if hw in FOOT:
        if hw == "cycleway" and tags.get("foot") not in ("yes", "designated"):
            return None
        flags = 1 if hw == "steps" else 0
    elif hw in STREET:
        if tags.get("sidewalk") == "no" and hw in ("primary", "secondary"):
            return None
        flags = 4
    else:
        return None
    if tags.get("footway") == "crossing" or tags.get("crossing"):
        flags |= 8
    incline = tags.get("incline", "").rstrip("%")
    try:
        if abs(float(incline)) > STEEP_PCT:
            flags |= 2
    except ValueError:
        if incline in ("up", "down") and hw != "steps":
            flags |= 2
    return flags


def build_graph(data: bp.OsmData, tiles: list):
    """Ways split at shared nodes into edges: {(a, b): (flags, [node ids])}, OSM node ids."""
    uses: dict[int, int] = {}
    kept = []
    for wid, nds in data.ways.items():
        flags = walkable(data.way_tags.get(wid, {}))
        if flags is None or len(nds) < 2 or any(n not in data.nodes for n in nds):
            continue
        kept.append((wid, flags, nds))
        for i, n in enumerate(nds):
            uses[n] = uses.get(n, 0) + (2 if i in (0, len(nds) - 1) else 1)
    joints = {n for n, c in uses.items() if c > 1}
    joints |= {
        n for n in data.node_tags if "entrance" in data.node_tags[n] or "door" in data.node_tags[n]
    }
    edges = {}
    way_of = {}
    for wid, flags, nds in kept:
        run = [nds[0]]
        for n in nds[1:]:
            run.append(n)
            if n in joints or n == nds[-1]:
                a, b = run[0], run[-1]
                if a != b:
                    key = (a, b) if a < b else (b, a)
                    shape = run if a < b else run[::-1]
                    old = edges.get(key)
                    if old is None or (old[0] & 4 and not flags & 4):
                        edges[key] = (flags, shape)
                        way_of[key] = wid
                run = [n]
    # clip: both ends on the campus tiles (with build_places' margin)
    local = {n: bp.to_local(*data.nodes[n]) for e in edges.values() for n in e[1]}
    reach = bp.TILE_HALF + bp.MARGIN
    near = {
        n: any(abs(x - cx) <= reach and abs(z - cz) <= reach for cx, cz in tiles)
        for n, (x, z) in local.items()
    }
    edges = {k: v for k, v in edges.items() if near[k[0]] and near[k[1]]}
    return edges, local, way_of


def inside(p, ring) -> bool:
    """Even-odd point in polygon."""
    x, z = p
    hit = False
    for (x0, z0), (x1, z1) in zip(ring, ring[1:] + ring[:1], strict=False):
        if (z0 > z) != (z1 > z) and x < x0 + (z - z0) * (x1 - x0) / (z1 - z0):
            hit = not hit
    return hit


def crosses(a, b, c, d) -> bool:
    """True when segments ab and cd cross inside both (touching at an end does not count)."""

    def side(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    d1, d2, d3, d4 = side(c, d, a), side(c, d, b), side(a, b, c), side(a, b, d)
    return d1 * d2 < 0 and d3 * d4 < 0


def drop_indoors(edges: dict, local: dict, data: bp.OsmData, way_of: dict) -> dict:
    """Drop edges that run inside a building outline, unless OSM maps them as a passage through it.
    Routes end at a building's entrance (and AGENTS.md rule 16 bars any route inside housing)."""
    rings = []
    for wid, tags in data.way_tags.items():
        nds = data.ways[wid]
        if "building" in tags and len(nds) > 3 and all(n in data.nodes for n in nds):
            ring = [bp.to_local(*data.nodes[n]) for n in nds]
            xs, zs = [q[0] for q in ring], [q[1] for q in ring]
            rings.append((min(xs), max(xs), min(zs), max(zs), ring))
    kept = {}
    for key, (flags, shape) in edges.items():
        tags = data.way_tags.get(way_of[key], {})
        if tags.get("tunnel") == "building_passage" or tags.get("covered") == "yes":
            kept[key] = (flags, shape)
            continue
        pts = [local[n] for n in shape]
        segs = list(zip(pts, pts[1:], strict=False))
        if not any(enters(a, b, ring, box) for a, b in segs for *box, ring in rings):
            kept[key] = (flags, shape)
    return kept


def enters(a, b, ring, box) -> bool:
    """True when segment ab runs inside a building outline: its middle is inside, or it crosses
    a wall."""
    x0, x1, z0, z1 = box
    if max(a[0], b[0]) < x0 or min(a[0], b[0]) > x1 or max(a[1], b[1]) < z0 or min(a[1], b[1]) > z1:
        return False
    if inside(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), ring):
        return True
    return any(crosses(a, b, c, d) for c, d in zip(ring, ring[1:] + ring[:1], strict=False))


def simplify(points: list[tuple[float, float]], tol: float) -> list[int]:
    """Douglas-Peucker: indices of points kept (always the two ends)."""
    if len(points) < 3:
        return list(range(len(points)))
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        i, j = stack.pop()
        (x0, z0), (x1, z1) = points[i], points[j]
        dx, dz = x1 - x0, z1 - z0
        length = math.hypot(dx, dz) or 1e-9
        best, at = -1.0, -1
        for k in range(i + 1, j):
            x, z = points[k]
            d = abs(dz * (x - x0) - dx * (z - z0)) / length
            if d > best:
                best, at = d, k
        if best > tol:
            keep.add(at)
            stack += [(i, at), (at, j)]
    return sorted(keep)


def drop_small_pieces(edges: dict, local: dict) -> dict:
    """Keep connected pieces whose total length is at least MIN_PIECE_M."""
    adj: dict[int, list] = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    piece: dict[int, int] = {}
    for start in adj:
        if start in piece:
            continue
        piece[start] = start
        todo = [start]
        while todo:
            for m in adj[todo.pop()]:
                if m not in piece:
                    piece[m] = start
                    todo.append(m)
    length: dict[int, float] = {}
    for (a, _b), (_f, shape) in edges.items():
        pts = [local[n] for n in shape]
        length[piece[a]] = length.get(piece[a], 0) + sum(
            math.dist(p, q) for p, q in zip(pts, pts[1:], strict=False)
        )
    return {k: v for k, v in edges.items() if length[piece[k[0]]] >= MIN_PIECE_M}


class Heights:
    """Bare-earth heights from the 3DEP 1 m DEM, sampled in batches and cached outside the repo."""

    def __init__(self, cache: Path, offline: bool):
        self.cache, self.offline, self.last = cache, offline, 0.0
        cache.mkdir(parents=True, exist_ok=True)

    def sample(self, points: list[tuple[float, float]]) -> list[float | None]:
        out: list[float | None] = []
        for i in range(0, len(points), SAMPLE_BATCH):
            out += self._batch(points[i : i + SAMPLE_BATCH])
        return out

    def _batch(self, pts):
        lonlat = [[round(lon, 7), round(lat, 7)] for lat, lon in pts]
        geometry = json.dumps(
            {"points": lonlat, "spatialReference": {"wkid": 4326}}, separators=(",", ":")
        )
        file = self.cache / f"dem_{hashlib.sha256(geometry.encode()).hexdigest()[:20]}.json"
        if file.exists():
            body = file.read_bytes()
        elif self.offline:
            raise SystemExit("offline and DEM samples not cached")
        else:
            wait = 1.0 - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            form = urllib.parse.urlencode(
                {
                    "geometry": geometry,
                    "geometryType": "esriGeometryMultipoint",
                    "returnFirstValueOnly": "true",
                    "f": "json",
                }
            ).encode()
            body = b"{}"
            for attempt in range(3):
                req = urllib.request.Request(DEM, data=form, headers={"User-Agent": bp.USER_AGENT})
                try:
                    with urllib.request.urlopen(req, timeout=120) as resp:
                        body = resp.read()
                except (urllib.error.URLError, TimeoutError) as err:
                    print(f"DEM request failed ({err}), retrying", file=sys.stderr)
                    body = b"{}"
                self.last = time.monotonic()
                if self._complete(body, len(pts)):
                    file.write_bytes(body)  # only a full answer is cached
                    break
                time.sleep(2 * (attempt + 1))
            print(f"sampled {len(pts)} heights", file=sys.stderr)
        values: list[float | None] = [None] * len(pts)
        for s in json.loads(body).get("samples", []):
            try:
                values[s["locationId"]] = float(s["value"])
            except (KeyError, TypeError, ValueError):
                pass
        return values

    @staticmethod
    def _complete(body: bytes, n: int) -> bool:
        """A DEM answer with a numeric height for every point (no ArcGIS error object)."""
        try:
            got = json.loads(body)
            ok = {
                s["locationId"]
                for s in got.get("samples", [])
                if float(s["value"]) == float(s["value"])
            }
        except (ValueError, KeyError, TypeError):
            return False
        return "error" not in got and ok == set(range(n))


def resample(pts: list[tuple[float, float]], step: float) -> list[tuple[float, float]]:
    """Points every `step` metres along a polyline, ends included."""
    out = [pts[0]]
    carry = 0.0
    for p, q in zip(pts, pts[1:], strict=False):
        seg = math.dist(p, q)
        d = step - carry
        while d < seg:
            t = d / seg
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
            d += step
        carry = (carry + seg) % step
    if out[-1] != pts[-1]:
        out.append(pts[-1])
    return out


def steepest(samples: list[tuple[float, float]], heights: list[float | None]) -> float | None:
    """Steepest grade in percent over any GRADE_RUN_M of path; an edge shorter than that is
    measured end to end (down to SHORT_RUN_M). The window keeps one noisy DEM cell (a wall, a
    kerb) from marking a level path steep. None when the heights needed are missing: unknown."""
    along = [0.0]
    for p, q in zip(samples, samples[1:], strict=False):
        along.append(along[-1] + math.dist(p, q))
    if along[-1] < GRADE_RUN_M:
        if along[-1] < SHORT_RUN_M:
            return 0.0  # too short to have a slope worth routing around
        if heights[0] is None or heights[-1] is None:
            return None
        return abs(heights[-1] - heights[0]) / along[-1] * 100
    best, measured = 0.0, False
    j = 0
    for i in range(len(samples)):
        while j < len(samples) - 1 and along[j] - along[i] < GRADE_RUN_M:
            j += 1
        if along[j] - along[i] < GRADE_RUN_M or heights[i] is None or heights[j] is None:
            continue
        best = max(best, abs(heights[j] - heights[i]) / (along[j] - along[i]) * 100)
        measured = True
    return best if measured else None


def outline(data: bp.OsmData, osm: str) -> list[tuple[float, float]] | None:
    """Local outline of a building way, or the outer rings of a relation joined, or None."""
    kind, oid = osm.split("/")
    oid = int(oid)
    if kind == "way" and oid in data.ways:
        nds = data.ways[oid]
    elif kind == "relation" and oid in data.relations:
        outers = [
            data.ways[r]
            for t, r, role in data.relations[oid]
            if t == "way" and role == "outer" and r in data.ways
        ]
        nds = [n for ring in bp.join_rings(outers) for n in ring]
    else:
        return None
    if any(n not in data.nodes for n in nds) or len(nds) < 3:
        return None
    return [bp.to_local(*data.nodes[n]) for n in nds]


def point_segment(p, a, b) -> float:
    ax, az = a
    dx, dz = b[0] - ax, b[1] - az
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - az) * dz) / ((dx * dx + dz * dz) or 1e-9)))
    return math.hypot(p[0] - ax - t * dx, p[1] - az - t * dz)


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path(tempfile.gettempdir()) / "places-osm-cache",
        help="directory for raw OSM and DEM responses (keep it outside the repository)",
    )
    parser.add_argument("--offline", action="store_true", help="use cached responses only")
    parser.add_argument("--out", type=Path, default=repo / "viewer" / "paths.json")
    args = parser.parse_args(argv)

    tiles = bp.load_tiles(repo)
    fetcher = bp.Fetcher(args.cache, args.offline)
    data = bp.OsmData()
    bp.fetch_area(fetcher, data, bp.fetch_bbox(tiles))
    places = json.loads((repo / "viewer" / "places.json").read_text())["places"]
    buildings = [p for p in places if p["kind"] == "building"]
    bp.complete_relations(
        fetcher,
        data,
        [int(p["osm"].split("/")[1]) for p in buildings if p["osm"].startswith("relation/")],
    )

    edges, local, way_of = build_graph(data, tiles)
    edges = drop_small_pieces(drop_indoors(edges, local, data, way_of), local)

    # simplify each edge's shape; the kept shape points become graph nodes of their own
    index: dict[int, int] = {}
    nodes: list[tuple[float, float]] = []

    def node(n: int) -> int:
        if n not in index:
            index[n] = len(nodes)
            nodes.append(local[n])
        return index[n]

    chains = []
    for key, (flags, shape) in sorted(edges.items()):
        pts = [local[n] for n in shape]
        tags = data.way_tags.get(way_of[key], {})
        # the DEM is bare earth: under a bridge or over a tunnel it is not the walking surface
        lifted = tags.get("bridge", "no") != "no" or tags.get("tunnel", "no") != "no"
        chains.append((flags, [shape[i] for i in simplify(pts, SIMPLIFY_M)], pts, lifted))

    heights = Heights(args.cache, args.offline)
    samples = [resample(pts, GRADE_STEP_M) for _f, _keep, pts, _lifted in chains]
    flat = [bp.from_local(x, z) for s in samples for x, z in s]
    values = heights.sample(flat)
    out_edges = []
    at = 0
    for (flags, keep, _pts, lifted), s in zip(chains, samples, strict=False):
        h = values[at : at + len(s)]
        at += len(s)
        grade = 0.0 if lifted else steepest(s, h)
        if grade is not None and grade > STEEP_PCT and not flags & 1:
            flags |= 2
        ids = [node(n) for n in keep]
        # the grade applies to the whole OSM edge; each simplified piece carries it
        for a, b in zip(ids, ids[1:], strict=False):
            out_edges.append([a, b, flags, -1 if grade is None else round(grade)])

    # entrances: OSM entrance nodes on each building's outline, else the nearest graph node to it
    degree = [0] * len(nodes)
    for a, b, _f, _g in out_edges:
        degree[a] += 1
        degree[b] += 1
    entrances = []
    entrance_nodes = {
        n for n, t in data.node_tags.items() if ("entrance" in t or "door" in t) and n in index
    }
    for b in sorted(buildings, key=lambda p: p["osm"]):
        ring = outline(data, b["osm"])
        if ring is None:
            continue
        segs = list(zip(ring, ring[1:] + ring[:1], strict=False))
        mapped = [
            n for n in entrance_nodes if min(point_segment(local[n], a, c) for a, c in segs) < 0.5
        ]
        if mapped:
            entrances += [
                {"osm": b["osm"], "node": index[n], "mapped": True} for n in sorted(mapped)
            ]
            continue
        # a footway that stops at the wall is most likely a way in: every such dead end within
        # DOOR_M of the outline, and every path point that touches the wall (WALL_M); with none,
        # the nearest graph node within ENTRANCE_REACH_M
        best, dist, ends = None, ENTRANCE_REACH_M, []
        for i, p in enumerate(nodes):
            if abs(p[0] - b["x"]) > b["r"] + dist or abs(p[1] - b["z"]) > b["r"] + dist:
                continue
            d = min(point_segment(p, a, c) for a, c in segs)
            if d < (DOOR_M if degree[i] == 1 else WALL_M):
                ends.append(i)
            if d < dist:
                best, dist = i, d
        for i in ends or ([best] if best is not None else []):
            entrances.append({"osm": b["osm"], "node": i, "mapped": False})

    fetched = sorted(fetcher.fetched_dates)
    out = {
        "source": "OpenStreetMap (API 0.6 map calls); heights USGS 3DEP 1 m DEM",
        "licence": "Data (c) OpenStreetMap contributors, ODbL 1.0; 3DEP public domain",
        "fetched": fetched[-1] if fetched else dt.date.today().isoformat(),
        "frame": bp.FRAME,
        "flags": {"steps": 1, "steep": 2, "street": 4, "crossing": 8},
        "steep_pct": STEEP_PCT,
        "nodes": [round(v, 1) for p in nodes for v in p],
        "edges": out_edges,
        "entrances": entrances,
    }
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    mapped = sum(e["mapped"] for e in entrances)
    print(
        f"{len(nodes)} nodes, {len(out_edges)} edges, "
        f"{len(entrances)} entrances ({mapped} mapped) -> {args.out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
