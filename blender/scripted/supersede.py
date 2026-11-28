"""Write the rules for tools/web-export/supersede.mjs: for every area, the footprint outline and
which meshes of the other source models are ground inside it (<area>/footprint.json, "supersede"),
or, for an area that owns no ground, its `volumes`: what of the other sources' tiles it replaces.

usage: python3 blender/scripted/supersede.py OUT.json [--areas NAME,NAME]
Every area's rules are written, so marks of other areas stay known; `--areas` marks the rest `skip`.
"""

import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geom  # noqa: E402
import layout  # noqa: E402
import numpy as np  # noqa: E402

VOLUME_KEYS = {"name", "ring", "meshes", "drop", "above", "keep", "why"}
SHARPEST = 10.0  # degrees: a sharper ring corner is an offset's miter spike, not a wall
# metres: along an edge it shares with another area, a footprint's cut reaches this far into the
# other area. Two areas that both cut the far field on the same line left a sliver of it standing
# between the cuts (the far field stands up to 0.9 m over the new ground there): a dark line along
# the seam. The far field's cut edge lies anywhere from 1 cm to a grid diagonal (0.55 m on the
# north model's 0.38 m grid) inside the outline that cut it (tools/web-export/cut.mjs
# snapQuantized); the other area's cut takes that edge away only if it reaches past it.
OVERLAP = 0.6
MIN_SHARED = 1.0  # metres: a shared stretch shorter than this stays where it is
TOL = 0.02  # metres: a run this close to another area's outline lies on it


def _crosses(p, q, r, s):
    """Do segments p-q and r-s cross at a point inside both (not at a shared end)?"""

    def side(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    return side(p, q, r) * side(p, q, s) < 0 and side(r, s, p) * side(r, s, q) < 0


def _check_ring(name, ring):
    if len(ring) < 3 or abs(geom.area(ring)) < 0.01:
        raise ValueError(f"volume {name!r}: a ring needs three corners round an area")
    n = len(ring)
    for i in range(n):
        a, b, c = ring[i - 1], ring[i], ring[(i + 1) % n]
        u, w = (a[0] - b[0], a[1] - b[1]), (c[0] - b[0], c[1] - b[1])
        cos = (u[0] * w[0] + u[1] * w[1]) / ((math.hypot(*u) * math.hypot(*w)) or 1.0)
        if math.degrees(math.acos(max(-1.0, min(1.0, cos)))) < SHARPEST:
            raise ValueError(f"volume {name!r}: corner {list(b)} is sharper than {SHARPEST} deg")
        for j in range(i + 2, n):
            if (j + 1) % n != i and _crosses(b, c, ring[j], ring[(j + 1) % n]):
                raise ValueError(f"volume {name!r}: the ring crosses itself near {list(b)}")


def check_volumes(volumes):
    """The `volumes` of an area as supersede.mjs takes them; refuses what it cannot honour. A
    volume is a `ring` (true-arc corners allowed; with `above`, only what lies above that level,
    NAVD88 metres; `keep`, patterns on 'mesh name material name' that stay) or `meshes` (exact mesh
    names, dropped whole). `drop` is "all". `why` is for people and is left out."""
    out, names = [], set()
    for v in volumes:
        name = v.get("name")
        if not name or name in names:
            raise ValueError(f"volume names must be given and unique: {name!r}")
        names.add(name)
        extra = set(v) - VOLUME_KEYS
        if extra:
            raise ValueError(f"volume {name!r}: unknown keys {sorted(extra)}")
        if v.get("drop", "all") != "all":
            raise ValueError(f"volume {name!r}: drop must be 'all'")
        if ("ring" in v) == ("meshes" in v):
            raise ValueError(f"volume {name!r}: give a ring or meshes, not both or neither")
        r = dict(name=name)
        if "meshes" in v:
            if not v["meshes"] or not all(isinstance(m, str) and m for m in v["meshes"]):
                raise ValueError(f"volume {name!r}: meshes must be mesh names")
            r.update(meshes=list(v["meshes"]), drop="all")
            out.append(r)
            continue
        ring = [(round(x, 3), round(y, 3)) for x, y in geom.expand(v["ring"], True)]
        _check_ring(name, ring)
        r.update(ring=[list(p) for p in ring], drop="all")
        if "above" in v:
            a = v["above"]
            if isinstance(a, bool) or not isinstance(a, int | float) or not math.isfinite(a):
                raise ValueError(f"volume {name!r}: above must be a height in metres")
            r["above"] = float(a)
        if "keep" in v:
            for k in v["keep"]:
                try:
                    re.compile(k)
                except re.error as e:
                    raise ValueError(f"volume {name!r}: keep pattern {k!r}: {e}") from None
            r["keep"] = list(v["keep"])
        out.append(r)
    return out


def _near_ring(ring, x, y, tol=TOL):
    n = len(ring)
    for i in range(n):
        (ax, ay), (bx, by) = ring[i][:2], ring[(i + 1) % n][:2]
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ((dx * dx + dy * dy) or 1e-12)))
        if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= tol * tol:
            return True
    return False


def _split(ring, others):
    """`ring` with a corner added wherever a corner of one of `others` lies on one of its runs (a
    stretch the two outlines share can start or end there)."""
    out = []
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        out.append(a)
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln2 = dx * dx + dy * dy
        if ln2 < 1e-12:
            continue
        ts = set()
        for o in others:
            for q in o:
                t = ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / ln2
                if 1e-6 < t < 1 - 1e-6:
                    if math.hypot(a[0] + t * dx - q[0], a[1] + t * dy - q[1]) <= TOL:
                        ts.add(round(t, 9))
        ln = math.sqrt(ln2)
        last = 0.0
        for t in sorted(ts):
            if (t - last) * ln > 1e-3 and (1 - t) * ln > 1e-3:
                out.append((a[0] + t * dx, a[1] + t * dy))
                last = t
    return out


def shared_stretches(ring, others):
    """The runs of `ring`, split where a corner of another outline lies on it, that lie whole on
    one of `others` (both ends and the middle within TOL): [(a, b, index into others)]."""
    pts = _split([(p[0], p[1]) for p in ring], others)
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        for j, o in enumerate(others):
            if all(_near_ring(o, *p) for p in (a, b, mid)):
                out.append((a, b, j))
                break
    return out


def uncovered(ring, rings, step=0.02, tol=0.005):
    """Points of `ring`, every `step` metres, in none of `rings` and not within `tol` of one."""
    P = np.array([p[:2] for p in geom.resample(ring, step, True)], float)
    return [tuple(p) for p in P[~_covered(P, rings, tol)]]


def _covered(P, rings, tol):
    """Which of the points P (m x 2) lie inside one of `rings` (even-odd) or within `tol` of one.
    Points go in runs of 256 (a resampled outline keeps neighbours together), each against only the
    runs of a ring that can matter to it."""
    ok = np.zeros(len(P), bool)
    segs = []
    for r in rings:
        R = np.asarray([q[:2] for q in r], float)
        segs.append((R, np.roll(R, -1, 0)))
    for k in range(0, len(P), 256):
        Q = P[k : k + 256]
        (x0, y0), (x1, y1) = Q.min(0), Q.max(0)
        for A, B in segs:
            ylo, yhi = np.minimum(A[:, 1], B[:, 1]), np.maximum(A[:, 1], B[:, 1])
            xlo, xhi = np.minimum(A[:, 0], B[:, 0]), np.maximum(A[:, 0], B[:, 0])
            ray = (yhi >= y0) & (ylo <= y1) & (xhi >= x0)  # can cross a ray to +x from a point
            box = (yhi >= y0 - tol) & (ylo <= y1 + tol) & (xlo <= x1 + tol) & (xhi >= x0 - tol)
            q = Q[:, None, :]
            if ray.any():
                a, b = A[ray][None], B[ray][None]
                cross = (a[..., 1] > q[..., 1]) != (b[..., 1] > q[..., 1])
                dx, dy = b[..., 0] - a[..., 0], b[..., 1] - a[..., 1]
                with np.errstate(divide="ignore", invalid="ignore"):
                    xc = a[..., 0] + (q[..., 1] - a[..., 1]) * dx / dy
                ok[k : k + 256] |= (cross & (q[..., 0] < xc)).sum(1) % 2 == 1
            if box.any():
                a, d = A[box][None], (B[box] - A[box])[None]
                ln2 = (d**2).sum(-1)
                t = np.clip(((q - a) * d).sum(-1) / np.where(ln2 > 0, ln2, 1e-12), 0, 1)
                e = q - a - t[..., None] * d
                ok[k : k + 256] |= (e[..., 0] ** 2 + e[..., 1] ** 2 <= tol * tol).any(1)
    return ok


def _polyline(pts, step=0.02):
    out = []
    for a, b in zip(pts, pts[1:], strict=False):
        k = max(1, math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(k)]
    return np.array(out + [pts[-1]], float)


def grow_shared(ring, others, d=OVERLAP):
    """The closed outline `ring` with every stretch it shares with another area (a run, split where
    a corner of the other outline lies on it, that lies whole on one of `others`, MIN_SHARED long
    or more) moved `d` metres outward, into that area; the other runs stay where they are.
    Where a moved run meets another run, the corner is where their lines meet, if the new outline
    there lies in this area or another; otherwise (the neighbour ends at a corner, and past it is
    ground no area owns) the moved run steps back to the old corner, as far along as it needs to
    take nothing outside the areas."""
    ring = [(p[0], p[1]) for p in ring]
    pts = _split(ring, others)
    n = len(pts)
    sign = 1.0 if geom.area(pts) > 0 else -1.0  # outward is to the right of an anticlockwise run
    runs = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ln = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        on = any(all(_near_ring(o, *p) for p in (a, b, mid)) for o in others)
        shared = ln >= MIN_SHARED and on
        u = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        runs.append((u, (sign * u[1], -sign * u[0]), ln, d if shared else 0.0))
    if not any(r[3] for r in runs):
        return ring
    areas = [ring, *others]

    def ok(chain):
        return bool(_covered(_polyline(chain), areas, 0.005).all())

    out = []
    for i in range(n):
        (ua, na, la, da), (ub, nb, lb, db) = runs[i - 1], runs[i]
        p = pts[i]
        if not da and not db:
            out.append(p)
            continue
        a1 = (p[0] + na[0] * da, p[1] + na[1] * da)  # the end of the previous run, moved
        b0 = (p[0] + nb[0] * db, p[1] + nb[1] * db)  # the start of the next run, moved
        ca, cb = min(la / 2, 4 * d), min(lb / 2, 4 * d)
        start = (a1[0] - ua[0] * ca, a1[1] - ua[1] * ca)
        end = (b0[0] + ub[0] * cb, b0[1] + ub[1] * cb)
        cands = []
        det = ua[0] * ub[1] - ua[1] * ub[0]
        if abs(det) > 1e-9:
            k = ((b0[0] - a1[0]) * ub[1] - (b0[1] - a1[1]) * ub[0]) / det
            cands.append([(a1[0] + k * ua[0], a1[1] + k * ua[1])])
        elif da and db:
            cands.append([a1])
        for s in (0.0, d / 2, d, 2 * d, 4 * d, 8 * d, 16 * d):
            sa, sb = min(s, 0.45 * la), min(s, 0.45 * lb)
            chain = [(a1[0] - ua[0] * sa, a1[1] - ua[1] * sa)] if da else []
            chain.append(p)
            if db:
                chain.append((b0[0] + ub[0] * sb, b0[1] + ub[1] * sb))
            cands.append(chain)
        best = next((c for c in cands if ok([start, *c, end])), cands[-1])
        for q in best:
            if not out or math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) > 1e-9:
                out.append(q)
    if math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= 1e-9:
        out.pop()
    return _unloop(out)


def _unloop(ring):
    """`ring` with the small loops cut off where it crosses itself: where runs i and j cross, the
    corners between them (the shorter way round) go and the crossing point takes their place. A
    notch of a shared edge narrower than twice OVERLAP (an outline that runs round a door or a
    pier) leaves such a loop when the runs either side move out past each other; the outer line
    is the cut."""
    ring = list(ring)
    for _ in range(len(ring)):
        n = len(ring)
        hit = None
        for i in range(n):
            for j in range(i + 2, n):
                if (j + 1) % n == i:
                    continue
                p, q, r, s = ring[i], ring[(i + 1) % n], ring[j], ring[(j + 1) % n]
                if _crosses(p, q, r, s):
                    hit = (i, j, p, q, r, s)
                    break
            if hit:
                break
        if not hit:
            return ring
        i, j, p, q, r, s = hit
        dx, dy, ex, ey = q[0] - p[0], q[1] - p[1], s[0] - r[0], s[1] - r[1]
        t = ((r[0] - p[0]) * ey - (r[1] - p[1]) * ex) / (dx * ey - dy * ex)
        x = (p[0] + t * dx, p[1] + t * dy)
        inner = ring[i + 1 : j + 1]  # the corners between the two runs one way round
        outer = ring[j + 1 :] + ring[: i + 1]  # and the other way
        # the loop is the part that turns the other way round (a run moved out past its
        # neighbour), else the shorter part
        if geom.area([x, *inner]) * geom.area(ring) < 0 or len(inner) <= len(outer):
            ring = ring[: i + 1] + [x] + ring[j + 1 :]
        else:
            ring = [x, *inner]
    return ring


def grow_into(name, areas=None):
    """The other areas' footprints that area `name` may grow into (grow_shared). An area added
    beside published ones sets `"neighbours_keep_cuts": true` in its supersede rules: it alone
    cuts past the edges it shares with them, and they do not grow into it, so their rules (and the
    marks their cuts left in the published tiles) stay what they were and the new area can be
    applied to those tiles. Without it every neighbour's grown outline, and so its rules' hash,
    changes, and supersede.mjs refuses every tile the neighbour cut until the main and north
    tiles are exported again. `areas` (name -> plan folder) defaults to every area."""
    areas = areas if areas is not None else {d.name: d for d in layout.areas()}
    out = []
    for other, d in areas.items():
        foot = layout.load(d)["footprint"]
        if other == name or not foot:
            continue
        f = d / "footprint.json"
        if f.exists() and json.loads(f.read_text())["supersede"].get("neighbours_keep_cuts"):
            continue
        out.append(foot)
    return out


def area_rules(plan_dir, chosen, others=()):
    """One area's entry in the rules file: footprint and patterns, or volumes, or both. `others`
    are the other areas' footprints (grow_into): where the area's rules ask for `overlap`, along
    an edge shared with one the cut reaches OVERLAP into it (grow_shared)."""
    rules = json.loads(Path(plan_dir / "footprint.json").read_text())["supersede"]
    out = dict(name=plan_dir.name, skip=not chosen)
    foot = layout.load(plan_dir)["footprint"]
    if rules.get("neighbours_keep_cuts") and not rules.get("overlap"):
        raise ValueError(f"{plan_dir.name}: neighbours_keep_cuts needs overlap (it alone cuts)")
    if foot:
        out.update(
            # opt-in (`"overlap": true`): moving a run can shorten the run beside it at a sharp or
            # reflex corner, so an area takes it only where the grown outline holds the old one
            footprint=[
                [round(x, 3), round(y, 3)]
                for x, y in (grow_shared(foot, others) if rules.get("overlap") else foot)
            ],
            clip=rules["clip"],
            drop=rules.get("drop", []),
            tuck=rules.get("tuck", 0.5),
        )
    if rules.get("volumes"):
        out["volumes"] = check_volumes(rules["volumes"])
    if not foot and not rules.get("volumes"):
        raise ValueError(f"{plan_dir.name}: footprint.json has neither a footprint nor volumes")
    return out


def main():
    args = sys.argv[1:]
    out = []
    chosen = {d.name for d in layout.areas(args)}
    areas = {d.name: d for d in layout.areas()}
    for plan_dir in layout.areas():
        if not (plan_dir / "footprint.json").exists():
            continue  # interiors only: the area owns no ground and replaces nothing
        others = grow_into(plan_dir.name, areas)
        r = area_rules(plan_dir, plan_dir.name in chosen, others)
        out.append(r)
        print(
            f"supersede rules {plan_dir.name}: {len(r.get('footprint', []))} footprint points,",
            f"{len(r.get('clip', []))} clip and {len(r.get('drop', []))} drop patterns,",
            f"{len(r.get('volumes', []))} volumes",
        )
    json.dump(dict(areas=out), open(args[0], "w"))


if __name__ == "__main__":
    main()
