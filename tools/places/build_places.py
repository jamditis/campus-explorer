"""Build viewer/places.json, the named places the viewer labels and offers in search.

Reads the tile centres from models/main/manifest.json (the whole campus is one scene),
fetches OpenStreetMap data for the area they cover from the OSM API 0.6, keeps named
buildings, car parks, sports grounds, stations and landmarks, and projects each one
into the viewer's three.js frame with the same Transverse Mercator maths as
viewer/geo.js. Standard library only.

Usage:
    python3 tools/places/build_places.py --cache /some/dir/outside/the/repo
    python3 tools/places/build_places.py --cache DIR --offline   # use cached responses only

Data (c) OpenStreetMap contributors, ODbL 1.0.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = "https://api.openstreetmap.org/api/0.6"
USER_AGENT = "places-builder/1.0"
TILE_HALF = 80.0  # each tile covers a 160 m square around its centre
MARGIN = 40.0  # extra metres fetched around the tiles
DEDUPE_RADIUS = 30.0
KEEP_TAGS = (
    "building", "building:levels", "height", "amenity", "leisure", "railway", "tourism",
    "historic", "sport", "operator", "start_date", "alt_name", "short_name", "wikidata",
)
FRAME = "three.js metres; x east, -z grid north; origin EPSG:6527 E575880 N738340 ftUS"

# --- Projection: EPSG:6527, a port of viewer/geo.js (Krüger series, sixth order) ---------

M_PER_FTUS = 1200 / 3937
E0_FTUS = 575880
N0_FTUS = 738340
DEG = math.pi / 180
_A = 6378137.0
_F = 1 / 298.257222101
_K0 = 0.9999
_LAT0 = (38 + 50 / 60) * DEG
_LON0 = -74.5 * DEG
_FE = 150000.0
_E2 = _F * (2 - _F)
_ECC = math.sqrt(_E2)
_N = _F / (2 - _F)
_RECT_A = _A / (1 + _N) * (1 + _N**2 / 4 + _N**4 / 64 + _N**6 / 256)



# Names the university uses where OpenStreetMap has an older or other one. The owner works in the
# first: it is the College of Communication and Media (2026-11-20), mapped as "School of ...".
NAMES = {"way/1188721159": "College of Communication and Media"}


def place_name(osm_type, oid, tags):
    """The name shown for a place: the university's own where NAMES has one, else OSM's."""
    return NAMES.get(f"{osm_type}/{oid}", tags["name"].strip())


def _series(rows: list[list[float]]) -> list[float]:
    return [sum(c * _N ** (i + 1) for i, c in enumerate(row)) for row in rows]


_ALPHA = _series([
    [1 / 2, -2 / 3, 5 / 16, 41 / 180, -127 / 288, 7891 / 37800],
    [0, 13 / 48, -3 / 5, 557 / 1440, 281 / 630, -1983433 / 1935360],
    [0, 0, 61 / 240, -103 / 140, 15061 / 26880, 167603 / 181440],
    [0, 0, 0, 49561 / 161280, -179 / 168, 6601661 / 7257600],
    [0, 0, 0, 0, 34729 / 80640, -3418889 / 1995840],
    [0, 0, 0, 0, 0, 212378941 / 319334400],
])
_BETA = _series([
    [1 / 2, -2 / 3, 37 / 96, -1 / 360, -81 / 512, 96199 / 604800],
    [0, 1 / 48, 1 / 15, -437 / 1440, 46 / 105, -1118711 / 3870720],
    [0, 0, 17 / 480, -37 / 840, -209 / 4480, 5569 / 90720],
    [0, 0, 0, 4397 / 161280, -11 / 504, -830251 / 7257600],
    [0, 0, 0, 0, 4583 / 161280, -108847 / 3991680],
    [0, 0, 0, 0, 0, 20648693 / 638668800],
])


def _tau_prime(tau: float) -> float:
    sigma = math.sinh(_ECC * math.atanh(_ECC * tau / math.hypot(1, tau)))
    return tau * math.hypot(1, sigma) - sigma * math.hypot(1, tau)


def _tau_from_tau_prime(tp: float) -> float:
    tau = tp
    for _ in range(6):
        tpi = _tau_prime(tau)
        dtau = (tp - tpi) / math.hypot(1, tpi) * (
            (1 + (1 - _E2) * tau * tau) / ((1 - _E2) * math.hypot(1, tau))
        )
        tau += dtau
        if abs(dtau) < 1e-14:
            break
    return tau


def _kruger_xi_eta(lat: float, dlon: float) -> tuple[float, float]:
    tp = _tau_prime(math.tan(lat))
    xi_p = math.atan2(tp, math.cos(dlon))
    eta_p = math.asinh(math.sin(dlon) / math.hypot(tp, math.cos(dlon)))
    xi, eta = xi_p, eta_p
    for j, a in enumerate(_ALPHA, start=1):
        xi += a * math.sin(2 * j * xi_p) * math.cosh(2 * j * eta_p)
        eta += a * math.cos(2 * j * xi_p) * math.sinh(2 * j * eta_p)
    return xi, eta


_XI0 = _kruger_xi_eta(_LAT0, 0.0)[0]


def project(lat: float, lon: float) -> tuple[float, float]:
    """Latitude and longitude in degrees to EPSG:6527 easting and northing in metres."""
    xi, eta = _kruger_xi_eta(lat * DEG, lon * DEG - _LON0)
    return _FE + _K0 * _RECT_A * eta, _K0 * _RECT_A * (xi - _XI0)


def unproject(e: float, n: float) -> tuple[float, float]:
    """EPSG:6527 easting and northing in metres to latitude and longitude in degrees."""
    xi = n / (_K0 * _RECT_A) + _XI0
    eta = (e - _FE) / (_K0 * _RECT_A)
    xi_p, eta_p = xi, eta
    for j, b in enumerate(_BETA, start=1):
        xi_p -= b * math.sin(2 * j * xi) * math.cosh(2 * j * eta)
        eta_p -= b * math.cos(2 * j * xi) * math.sinh(2 * j * eta)
    tp = math.sin(xi_p) / math.hypot(math.sinh(eta_p), math.cos(xi_p))
    dlon = math.atan2(math.sinh(eta_p), math.cos(xi_p))
    return math.atan(_tau_from_tau_prime(tp)) / DEG, (_LON0 + dlon) / DEG


def to_local(lat: float, lon: float) -> tuple[float, float]:
    """Latitude and longitude to three.js metres (x east, z = -grid north)."""
    e, n = project(lat, lon)
    return e - E0_FTUS * M_PER_FTUS, -(n - N0_FTUS * M_PER_FTUS)


def from_local(x: float, z: float) -> tuple[float, float]:
    """three.js metres to latitude and longitude in degrees."""
    return unproject(x + E0_FTUS * M_PER_FTUS, -z + N0_FTUS * M_PER_FTUS)


# --- Area of interest ---------------------------------------------------------------------


def load_tiles(repo: Path) -> list[tuple[float, float]]:
    manifest = json.loads((repo / "models" / "main" / "manifest.json").read_text())
    return sorted({tuple(t["center"]) for t in manifest["tiles"] if t.get("center")})


def covered(x: float, z: float, tiles: list) -> bool:
    return any(abs(x - cx) <= TILE_HALF and abs(z - cz) <= TILE_HALF for cx, cz in tiles)


def fetch_bbox(tiles: list) -> tuple[float, float, float, float]:
    """(left, bottom, right, top) in degrees around every tile square plus the margin."""
    centres = tiles
    pad = TILE_HALF + MARGIN
    x0 = min(c[0] for c in centres) - pad
    x1 = max(c[0] for c in centres) + pad
    z0 = min(c[1] for c in centres) - pad
    z1 = max(c[1] for c in centres) + pad
    # Grid and geographic axes differ by about 0.2 degrees, so take all four corners.
    corners = [from_local(x, z) for x in (x0, x1) for z in (z0, z1)]
    lats = [c[0] for c in corners]
    lons = [c[1] for c in corners]
    return min(lons), min(lats), max(lons), max(lats)


# --- OSM API ------------------------------------------------------------------------------


class Fetcher:
    """OSM API client with an on-disk cache and at most one request per second."""

    def __init__(self, cache: Path, offline: bool):
        self.cache = cache
        self.offline = offline
        self.last = 0.0
        self.fetched_dates: set[str] = set()
        cache.mkdir(parents=True, exist_ok=True)

    def get(self, path: str, key: str) -> bytes | None:
        """Response body for API path, or None for HTTP 400 and 509 (area too big)."""
        file = self.cache / f"{key}.osm"
        if file.exists():
            mtime = dt.datetime.fromtimestamp(file.stat().st_mtime, dt.UTC)
            self.fetched_dates.add(mtime.date().isoformat())
            return file.read_bytes()
        if self.offline:
            raise SystemExit(f"offline and not cached: {path}")
        wait = 1.0 - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(API + path, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read()
        except urllib.error.HTTPError as err:
            if err.code in (400, 509):
                return None
            raise
        finally:
            self.last = time.monotonic()
        file.write_bytes(body)
        self.fetched_dates.add(dt.datetime.now(dt.UTC).date().isoformat())
        print(f"fetched {path} ({len(body)} bytes)", file=sys.stderr)
        return body


class OsmData:
    def __init__(self):
        self.nodes: dict[int, tuple[float, float]] = {}
        self.node_tags: dict[int, dict] = {}
        self.ways: dict[int, list[int]] = {}
        self.way_tags: dict[int, dict] = {}
        self.relations: dict[int, list[tuple[str, int, str]]] = {}
        self.relation_tags: dict[int, dict] = {}

    def add(self, xml: bytes) -> None:
        root = ET.fromstring(xml)
        for el in root:
            if el.tag not in ("node", "way", "relation"):
                continue  # <bounds> and the like
            tags = {t.get("k"): t.get("v") for t in el.findall("tag")}
            oid = int(el.get("id"))
            if el.tag == "node":
                self.nodes[oid] = (float(el.get("lat")), float(el.get("lon")))
                if tags:
                    self.node_tags[oid] = tags
            elif el.tag == "way":
                self.ways[oid] = [int(nd.get("ref")) for nd in el.findall("nd")]
                self.way_tags[oid] = tags
            elif el.tag == "relation":
                self.relations[oid] = [
                    (m.get("type"), int(m.get("ref")), m.get("role") or "")
                    for m in el.findall("member")
                ]
                self.relation_tags[oid] = tags


def fetch_area(fetcher: Fetcher, data: OsmData, bbox, depth: int = 0) -> None:
    left, bottom, right, top = bbox
    key = f"map_{left:.6f}_{bottom:.6f}_{right:.6f}_{top:.6f}"
    body = fetcher.get(f"/map?bbox={left:.7f},{bottom:.7f},{right:.7f},{top:.7f}", key)
    if body is not None:
        data.add(body)
        return
    if depth > 6:
        raise SystemExit("OSM API keeps refusing the area even after splitting")
    mid_lon = (left + right) / 2
    mid_lat = (bottom + top) / 2
    for quad in (
        (left, bottom, mid_lon, mid_lat), (mid_lon, bottom, right, mid_lat),
        (left, mid_lat, mid_lon, top), (mid_lon, mid_lat, right, top),
    ):
        fetch_area(fetcher, data, quad, depth + 1)


def complete_relations(fetcher: Fetcher, data: OsmData, wanted: list[int]) -> None:
    """The map call omits member ways that lie outside the bbox; fetch those relations whole."""
    for rid in wanted:
        members = data.relations[rid]
        missing = any(
            t == "way"
            and (ref not in data.ways or any(n not in data.nodes for n in data.ways[ref]))
            for t, ref, _ in members
        )
        if missing:
            body = fetcher.get(f"/relation/{rid}/full", f"relation_{rid}_full")
            if body is not None:
                data.add(body)


# --- Selection and geometry ---------------------------------------------------------------

SPORTS = {"pitch", "stadium", "sports_centre", "track"}
STATION_RAILWAY = {"station", "halt", "platform"}
LANDMARK_AMENITY = {"theatre", "library", "fountain", "place_of_worship"}


def classify(tags: dict) -> str | None:
    """Kind of place, or None when the feature is not one the viewer labels."""
    if "name" not in tags:
        return None
    if tags.get("amenity") == "university" and "building" not in tags:
        return None  # the campus-wide polygon
    if tags.get("railway") in STATION_RAILWAY or tags.get("public_transport") in (
        "station", "platform",
    ):
        return "station"
    if tags.get("amenity") == "parking" or tags.get("building") == "parking":
        return "parking"
    if tags.get("leisure") in SPORTS:
        return "sports"
    if "building" in tags:
        return "building"
    if (
        tags.get("tourism") in ("artwork", "attraction")
        or "historic" in tags
        or tags.get("amenity") in LANDMARK_AMENITY
        or tags.get("man_made") == "tower"
        or tags.get("leisure") in ("park", "garden")
    ):
        return "landmark"
    return None


def join_rings(ways: list[list[int]]) -> list[list[int]]:
    """Join way node lists end to end into closed rings; open leftovers are kept as they are."""
    rings = []
    pending = [list(w) for w in ways if len(w) >= 2]
    while pending:
        ring = pending.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, w in enumerate(pending):
                if w[0] == ring[-1]:
                    ring += w[1:]
                elif w[-1] == ring[-1]:
                    ring += w[-2::-1]
                elif w[-1] == ring[0]:
                    ring = w[:-1] + ring
                elif w[0] == ring[0]:
                    ring = w[:0:-1] + ring
                else:
                    continue
                pending.pop(i)
                changed = True
                break
        rings.append(ring)
    return rings


def centroid(rings: list[list[tuple[float, float]]]) -> tuple[float, float]:
    """Area-weighted centroid of closed rings; falls back to the vertex mean for slivers."""
    area_sum = cx = cz = 0.0
    for pts in rings:
        for (x1, z1), (x2, z2) in zip(pts, pts[1:] + pts[:1], strict=True):
            cross = x1 * z2 - x2 * z1
            area_sum += cross
            cx += (x1 + x2) * cross
            cz += (z1 + z2) * cross
    if abs(area_sum) > 1e-6:
        return cx / (3 * area_sum), cz / (3 * area_sum)
    pts = [p for ring in rings for p in ring]
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def to_local_ring(data: OsmData, node_ids: list[int]) -> list[tuple[float, float]]:
    pts = [to_local(*data.nodes[n]) for n in node_ids if n in data.nodes]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts


def geometry(data: OsmData, kind: str, oid: int):
    """(x, z, r) of a feature in three.js metres, or None when its geometry is missing."""
    if kind == "node":
        x, z = to_local(*data.nodes[oid])
        return x, z, 0.0
    if kind == "way":
        rings = [to_local_ring(data, data.ways[oid])]
    else:
        outers = [
            data.ways[ref] for t, ref, role in data.relations[oid]
            if t == "way" and role in ("outer", "") and ref in data.ways
        ]
        rings = [to_local_ring(data, r) for r in join_rings(outers)]
    rings = [r for r in rings if r]
    if not rings:
        return None
    x, z = centroid(rings)
    r = max(math.hypot(px - x, pz - z) for ring in rings for px, pz in ring)
    return x, z, r


def collect(data: OsmData, tiles: list) -> list[dict]:
    candidates = []
    sources = (
        ("node", data.node_tags), ("way", data.way_tags), ("relation", data.relation_tags),
    )
    for osm_type, table in sources:
        for oid, tags in table.items():
            kind = classify(tags)
            if kind is None:
                continue
            if osm_type == "relation" and tags.get("type") not in ("multipolygon", "boundary"):
                continue
            geom = geometry(data, osm_type, oid)
            if geom is None:
                continue
            x, z, r = geom
            if not covered(x, z, tiles):
                continue
            lat, lon = from_local(x, z)
            candidates.append({
                "name": place_name(osm_type, oid, tags),
                "kind": kind,
                "x": round(x, 2),
                "z": round(z, 2),
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "r": round(r, 1),
                "osm": f"{osm_type}/{oid}",
                "tags": {k: tags[k] for k in KEEP_TAGS if k in tags},
            })
    return dedupe(candidates)


def dedupe(places: list[dict]) -> list[dict]:
    """Drop a node when a way or relation with the same name lies within DEDUPE_RADIUS."""
    seen = {}
    for p in places:
        seen[p["osm"]] = p
    areas = [p for p in seen.values() if not p["osm"].startswith("node/")]
    kept = []
    for p in seen.values():
        if p["osm"].startswith("node/") and any(
            a["name"].casefold() == p["name"].casefold()
            and math.hypot(a["x"] - p["x"], a["z"] - p["z"]) <= DEDUPE_RADIUS
            for a in areas
        ):
            continue
        kept.append(p)
    return kept


def osm_sort_key(p: dict) -> tuple:
    osm_type, oid = p["osm"].split("/")
    return p["name"], osm_type, int(oid)


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--cache", type=Path, default=Path(tempfile.gettempdir()) / "places-osm-cache",
        help="directory for raw OSM API responses (keep it outside the repository)",
    )
    parser.add_argument("--offline", action="store_true", help="use cached responses only")
    parser.add_argument("--out", type=Path, default=repo / "viewer" / "places.json")
    args = parser.parse_args(argv)

    tiles = load_tiles(repo)
    bbox = fetch_bbox(tiles)
    print("bbox (lon/lat): " + ",".join(f"{v:.6f}" for v in bbox), file=sys.stderr)

    fetcher = Fetcher(args.cache, args.offline)
    data = OsmData()
    fetch_area(fetcher, data, bbox)
    wanted = [
        rid for rid, tags in data.relation_tags.items()
        if classify(tags) and tags.get("type") in ("multipolygon", "boundary")
    ]
    complete_relations(fetcher, data, wanted)

    places = sorted(collect(data, tiles), key=osm_sort_key)
    fetched = max(fetcher.fetched_dates) if fetcher.fetched_dates else dt.date.today().isoformat()
    out = {
        "source": "OpenStreetMap contributors",
        "licence": "ODbL 1.0",
        "fetched": fetched,
        "frame": FRAME,
        "places": places,
    }
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    counts = {}
    for p in places:
        counts[p["kind"]] = counts.get(p["kind"], 0) + 1
    print(f"wrote {len(places)} places to {args.out}: {counts}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
