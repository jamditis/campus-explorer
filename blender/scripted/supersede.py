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

VOLUME_KEYS = {"name", "ring", "meshes", "drop", "above", "keep", "why"}
SHARPEST = 10.0  # degrees: a sharper ring corner is an offset's miter spike, not a wall
# metres: along an edge it shares with another area, a footprint's cut reaches this far into the
# other area. Two areas that both cut the far field on the same line left a sliver of it standing
# between the cuts (the tiles' quantisation moves a cut by a centimetre or two; the far field
# stands up to 0.9 m over the new ground there): a dark line along the seam.
OVERLAP = 0.25
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


def grow_shared(ring, others, d=OVERLAP):
    """The closed outline `ring` with every run that lies whole on another area's outline (both
    ends and its middle within TOL of one of `others`) moved `d` metres outward, into that area;
    the other runs stay where they are. Corners are where the moved and unmoved runs' lines meet;
    two runs in line, one moved, get a short step between them."""
    ring = [(p[0], p[1]) for p in ring]
    n = len(ring)
    sign = 1.0 if geom.area(ring) > 0 else -1.0  # outward is to the right of an anticlockwise run
    runs = []
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        shared = any(all(_near_ring(o, *p) for p in (a, b, mid)) for o in others)
        ln = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        u = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        off = d if shared else 0.0
        nx, ny = sign * u[1] * off, -sign * u[0] * off
        runs.append(((a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), u, shared))
    if not any(r[3] for r in runs):
        return ring
    out = []
    for i in range(n):
        (pa, pb, u, _s), (qa, _qb, w, _t) = runs[i - 1], runs[i]
        det = u[0] * w[1] - u[1] * w[0]
        if abs(det) < 1e-9:  # in line: one end, then the other (a step, or the same point)
            out.append(pb)
            if math.hypot(qa[0] - pb[0], qa[1] - pb[1]) > 1e-9:
                out.append(qa)
            continue
        k = ((qa[0] - pa[0]) * w[1] - (qa[1] - pa[1]) * w[0]) / det
        out.append((pa[0] + k * u[0], pa[1] + k * u[1]))
    return out


def area_rules(plan_dir, chosen, others=()):
    """One area's entry in the rules file: footprint and patterns, or volumes, or both. `others`
    are the other areas' footprints: where the area's rules ask for `overlap`, along an edge
    shared with one the cut reaches OVERLAP into it (grow_shared)."""
    rules = json.loads(Path(plan_dir / "footprint.json").read_text())["supersede"]
    out = dict(name=plan_dir.name, skip=not chosen)
    foot = layout.load(plan_dir)["footprint"]
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
    feet = {d.name: layout.load(d)["footprint"] for d in layout.areas()}
    for plan_dir in layout.areas():
        if not (plan_dir / "footprint.json").exists():
            continue  # interiors only: the area owns no ground and replaces nothing
        others = [f for name, f in feet.items() if name != plan_dir.name and f]
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
