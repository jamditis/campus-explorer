"""Buildings from the plan's `buildings` parts: walls, a roof, windows, parking deck levels.

A part is an outline with a roof type and heights from the LiDAR (see README, "Buildings"). This is
massing with a facade rhythm, not a survey: outline and heights are measured, the window grid and
the colours are estimates, so every object made here is named `_UNVERIFIED`.
"""

import math

import geom
import kit
import layout
import massing
from ground import sheet_material

WALL_KIND = {"dorm": "brick", "hall": "brick", "plant": "brick", "deck": "concrete"}
PARAPET = massing.PARAPET
PROUD = 0.06  # how far windows and bands stand off the wall: enough not to flicker far away


def _edges(ring):
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        if length > 1e-6:
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            yield (
                i,
                a,
                b,
                length,
                (ux, uy),
                (uy, -ux),
            )  # the outward normal of an anticlockwise ring


def _panel(b, a, u, nrm, s0, s1, z0, z1, material, off=PROUD):
    """A flat panel on a wall: from `s0` to `s1` metres along it, from z0 to z1, `off` proud."""
    p = [
        (a[0] + u[0] * s + nrm[0] * off, a[1] + u[1] * s + nrm[1] * off, z)
        for s, z in ((s0, z0), (s1, z0), (s1, z1), (s0, z1))
    ]
    b.faces(p, [(0, 1, 2, 3)], material)


def _wells(p, roof_hex):
    """The part's `wells` as (anticlockwise ring, floor height, floor colour)."""
    out = []
    for w in p.get("wells", ()):
        r = geom.expand(w["ring"], True)
        out.append((r if geom.area(r) > 0 else r[::-1], w["floor"], w.get("colour", roof_hex)))
    return out


def _deck(b, outline, z, wells, deck, side):
    """A flat deck at `z` on an anticlockwise outline, open over each well. A well has inner walls
    from the deck down to its floor (`side`) and a floor of its own colour.
    """
    rings = [w[0] for w in wells]
    massing.check_wells(outline, rings)
    pts = [(q[0], q[1], z) for q in outline] + [(q[0], q[1], z) for r in rings for q in r]
    b.faces(pts, massing.deck_triangles(outline, rings), deck)
    for r, floor, hexc in wells:
        if not floor < z - 0.05:
            raise ValueError(f"a well floor ({floor}) must lie below its deck ({z:.2f})")
        m = len(r)
        v = [(q[0], q[1], z) for q in r] + [(q[0], q[1], floor) for q in r]
        # inner walls look into the well (to the left of the anticlockwise ring)
        b.faces(v, [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)], side)
        mat = kit.mat("concrete", "roof_" + hexc[1:], kit.srgb(hexc), 0.85)
        b.faces(v[m:], [tuple(range(m))], mat)  # anticlockwise from above: looks up


def _flat_roof(b, ring, top, drop, cap, deck, wells=()):
    """Parapet and roof deck of a flat roof: the deck lies `drop` below the parapet top."""
    n = len(ring)
    inner = massing.parapet_inner(ring)  # the outline itself when too narrow for a parapet
    if inner == list(ring):  # a plain cap at the top (a thin wall), not a pit `drop` deep
        b.faces([(p[0], p[1], top) for p in ring], [tuple(range(n))], cap)
        return
    v = (
        [(p[0], p[1], top) for p in ring]
        + [(p[0], p[1], top) for p in inner]
        + [(p[0], p[1], top - drop) for p in inner]
    )
    f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    # the parapet's inner face looks in over the roof deck
    f += [(2 * n + (i + 1) % n, 2 * n + i, n + i, n + (i + 1) % n) for i in range(n)]
    b.faces(v, f, cap)
    if wells:
        _deck(b, inner, top - drop, wells, deck, cap)
    else:
        b.faces(v[2 * n :], [tuple(range(n))], deck)


def _windows(b, part, ring, wall_top, ground, glass, holes=None):
    """Rows of windows on every wall long enough for a bay: counted down from the wall top, on the
    floors given in `windows.levels`, or at the heights given in `windows.rows`. No window on an
    edge in `no_windows` or across an opening (`holes`: {edge: [(s0, s1, z0, z1)]})."""
    w = part["windows"]
    floors = part.get("floors", 1)
    low = min(ground(*p) for p in ring)
    h = massing.storey(wall_top, low, floors)
    sill, tall, wide = w.get("sill", 0.9), w["height"], w["width"]
    skip = set(part.get("no_windows", ()))
    for i, a, _b, length, u, nrm in _edges(ring):
        if i in skip:
            continue
        for s in massing.bays(length, w["spacing"]):
            cut = (holes or {}).get(i, ())
            if any(s0 - wide / 2 < s < s1 + wide / 2 for s0, s1, _z0, _z1 in cut):
                continue
            g = ground(a[0] + u[0] * s, a[1] + u[1] * s)
            rows = massing.window_rows(
                wall_top, g, tall, sill, w.get("levels"), floors=floors, storey_h=h,
                rows=w.get("rows"),
            )  # fmt: skip
            for z0, z1 in rows:
                _panel(b, a, u, nrm, s - wide / 2, s + wide / 2, z0, min(z1, wall_top), glass)


def _recessed_cells(p, ring, tops, ground):
    """Window openings of a part whose `windows.style` is `recessed`, on its windowed edges."""
    w = p.get("windows") or {}
    if w.get("style") != "recessed":
        return []
    skip = set(p.get("no_windows", ()))
    edges = [i for i in range(len(ring)) if i not in skip]
    wall_top = min(tops) - p.get("parapet", PARAPET.get(p.get("style", "shed"), 0.4))
    return massing.window_cells(
        ring, ground, wall_top, w["width"], w["height"], w["spacing"], w.get("sill", 0.9),
        w.get("levels"), edges, rows=w.get("rows"),
    )  # fmt: skip


def _recessed(b, part, cells, hexes):
    """A recessed window in each opening: reveals, a frame with a mullion and a transom, glass set
    back, and a sill proud of the wall (the main model's window type, CCOM_Win_Wing_A)."""
    w = part["windows"]
    depth, back = w.get("reveal", 0.3), w.get("glass_back", 0.12)
    reveal = kit.mat("plaster", "reveal_" + hexes["wall"][1:], kit.srgb(hexes["wall"]), 0.9)
    fhex, shex = w.get("frame", "#2e3033"), w.get("sill_colour", "#cdc4b2")
    frame = kit.mat("metal", "frame_" + fhex[1:], kit.srgb(fhex), 0.5)
    sill = kit.mat("stone", "sill_" + shex[1:], kit.srgb(shex), 0.8)
    glass = kit.mat("glass", "window", kit.srgb("#2b3640"), 0.15)
    for c in cells:
        a, u, n = c["a"], c["u"], c["n"]

        def pt(s, z, off, a=a, u=u, n=n):  # along the wall, height, out (+) or in (-)
            return (a[0] + u[0] * s + n[0] * off, a[1] + u[1] * s + n[1] * off, z)

        s0, s1, z0, z1 = c["s0"], c["s1"], c["z0"], c["z1"]
        for q in (  # reveals look into the opening
            [pt(s0, z0, 0), pt(s0, z0, -depth), pt(s0, z1, -depth), pt(s0, z1, 0)],
            [pt(s1, z0, -depth), pt(s1, z0, 0), pt(s1, z1, 0), pt(s1, z1, -depth)],
            [pt(s0, z1, 0), pt(s0, z1, -depth), pt(s1, z1, -depth), pt(s1, z1, 0)],
            [pt(s1, z0, 0), pt(s1, z0, -depth), pt(s0, z0, -depth), pt(s0, z0, 0)],
        ):
            b.faces(q, [(0, 1, 2, 3)], reveal)
        b.faces([pt(s0, z0, -back), pt(s1, z0, -back), pt(s1, z1, -back), pt(s0, z1, -back)],
                [(0, 1, 2, 3)], glass)  # fmt: skip
        f, mid, tz = 0.06, (s0 + s1) / 2, z0 + (z1 - z0) * 2 / 3
        for bs0, bs1, bz0, bz1 in ((s0, s0 + f, z0, z1), (s1 - f, s1, z0, z1), (s0, s1, z1 - f, z1),
                                   (s0, s1, z0, z0 + f), (mid - f / 2, mid + f / 2, z0, z1),
                                   (s0, s1, tz - f / 2, tz + f / 2)):  # fmt: skip
            off = -back + 0.02
            b.faces([pt(bs0, bz0, off), pt(bs1, bz0, off), pt(bs1, bz1, off), pt(bs0, bz1, off)],
                    [(0, 1, 2, 3)], frame)  # fmt: skip
        sv = [pt(s, z, o) for s, z, o in ((s0 - 0.1, z0 - 0.09, 0.19), (s1 + 0.1, z0 - 0.09, 0.19),
                                          (s1 + 0.1, z0, 0.19), (s0 - 0.1, z0, 0.19),
                                          (s0 - 0.1, z0, 0.0), (s1 + 0.1, z0, 0.0))]  # fmt: skip
        b.faces(sv, [(0, 1, 2, 3), (3, 2, 5, 4)], sill)


def _curtain(b, ring, cw, hexes):
    """A curtain wall in its opening (`curtains`: `at`, `to` on one wall line, `z0`, `z1`, `cols`,
    `rows`, `frame` colour, `reveal`): reveals, one glass pane set back and a grid of frame bars
    splitting it into cols x rows lights, seen from both sides."""
    ((i, s0, s1, z0, z1),) = [
        (e, *h) for e, hs in massing.edge_openings(ring, [cw]).items() for h in hs
    ]
    a, bb = ring[i][:2], ring[(i + 1) % len(ring)][:2]
    length = math.dist(a, bb)
    u = ((bb[0] - a[0]) / length, (bb[1] - a[1]) / length)
    n = (u[1], -u[0])
    depth, back = cw.get("reveal", 0.3), cw.get("glass_back", 0.12)
    reveal = kit.mat("plaster", "reveal_" + hexes["wall"][1:], kit.srgb(hexes["wall"]), 0.9)
    fhex = cw.get("frame", "#592d28")
    frame = kit.mat("metal", "frame_" + fhex[1:], kit.srgb(fhex), 0.5)
    glass = kit.mat("glass", "window", kit.srgb("#2b3640"), 0.15)

    def pt(s, z, off):  # along the wall, height, out (+) or in (-)
        return (a[0] + u[0] * s + n[0] * off, a[1] + u[1] * s + n[1] * off, z)

    for q in (
        [pt(s0, z0, 0), pt(s0, z0, -depth), pt(s0, z1, -depth), pt(s0, z1, 0)],
        [pt(s1, z0, -depth), pt(s1, z0, 0), pt(s1, z1, 0), pt(s1, z1, -depth)],
        [pt(s0, z1, 0), pt(s0, z1, -depth), pt(s1, z1, -depth), pt(s1, z1, 0)],
        [pt(s1, z0, 0), pt(s1, z0, -depth), pt(s0, z0, -depth), pt(s0, z0, 0)],
    ):
        b.faces(q, [(0, 1, 2, 3)], reveal)
    b.faces([pt(s0, z0, -back), pt(s1, z0, -back), pt(s1, z1, -back), pt(s0, z1, -back)],
            [(0, 1, 2, 3)], glass)  # fmt: skip
    for off in (-back + 0.01, -back - 0.01):  # the grid on both faces of the glass
        for bs0, bs1, bz0, bz1 in massing.curtain_bars(s0, s1, z0, z1, cw["cols"], cw["rows"]):
            q = [pt(bs0, bz0, off), pt(bs1, bz0, off), pt(bs1, bz1, off), pt(bs0, bz1, off)]
            b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)


def _arch(b, ring, aw, hexes, wall):
    """A round-arched opening (`arches`: `at`, `to` on one wall line, `z0` the sill, `z1` the
    crown, `cols`, `rows`, `frame` colour, `glass` false for an open arch such as a belfry,
    `bands` [[z0, z1], ...] opaque panels in the frame colour across the glazing): the
    wall pieces over the head (spandrels), reveals round the jambs and along the head, and, when
    glazed, one pane set back with a frame of mullions, transoms and a curved head bar."""
    ((i, s0, s1, z0, z1),) = [
        (e, *h) for e, hs in massing.edge_openings(ring, [aw]).items() for h in hs
    ]
    a, bb = ring[i][:2], ring[(i + 1) % len(ring)][:2]
    length = math.dist(a, bb)
    u = ((bb[0] - a[0]) / length, (bb[1] - a[1]) / length)
    n = (u[1], -u[0])
    depth, back = aw.get("reveal", 0.3), aw.get("glass_back", 0.12)
    reveal = kit.mat("plaster", "reveal_" + hexes["wall"][1:], kit.srgb(hexes["wall"]), 0.9)

    def pt(s, z, off):  # along the wall, height, out (+) or in (-)
        return (a[0] + u[0] * s + n[0] * off, a[1] + u[1] * s + n[1] * off, z)

    for poly in massing.arch_spandrels(s0, s1, z1):  # wall the rectangular cut took over the head
        b.faces([pt(x, z, 0.0) for x, z in poly], [tuple(range(len(poly)))], wall)
    head = massing.arch_curve(s0, s1, z1)
    spring = head[0][1]
    for sx, sy in ((s0, 1), (s1, -1)):  # jamb reveals up to the springing line
        q = [pt(sx, z0, 0), pt(sx, z0, -depth), pt(sx, spring, -depth), pt(sx, spring, 0)]
        b.faces(q if sy > 0 else q[::-1], [(0, 1, 2, 3)], reveal)
    b.faces([pt(s0, z0, 0), pt(s1, z0, 0), pt(s1, z0, -depth), pt(s0, z0, -depth)][::-1],
            [(0, 1, 2, 3)], reveal)  # fmt: skip
    for (sa, za), (sb, zb) in zip(head, head[1:], strict=False):  # the head's soffit
        b.faces([pt(sa, za, 0), pt(sa, za, -depth), pt(sb, zb, -depth), pt(sb, zb, 0)],
                [(0, 1, 2, 3)], reveal)  # fmt: skip
    if not aw.get("glass", True):
        return
    glass = kit.mat("glass", "window", kit.srgb("#2b3640"), 0.15)
    pane = massing.arch_outline(s0, s1, z0, z1)
    b.faces([pt(x, z, -back) for x, z in pane], [tuple(range(len(pane)))], glass)
    fhex = aw.get("frame", "#33291f")
    frame = kit.mat("metal", "frame_" + fhex[1:], kit.srgb(fhex), 0.5)
    for bz0, bz1 in aw.get("bands", ()):  # an opaque panel across the opening (a transom band)
        for off in (-back + 0.015, -back - 0.015):
            q = [pt(s0, bz0, off), pt(s1, bz0, off), pt(s1, bz1, off), pt(s0, bz1, off)]
            b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)
    rects, bars = massing.arch_bars(s0, s1, z0, z1, aw.get("cols", 3), aw.get("rows", 4))
    w = 0.08
    for off in (-back + 0.01, -back - 0.01):  # on both faces of the glass
        for bs0, bs1, bz0, bz1 in rects:
            q = [pt(bs0, bz0, off), pt(bs1, bz0, off), pt(bs1, bz1, off), pt(bs0, bz1, off)]
            b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)
        cs, r = (s0 + s1) / 2, (s1 - s0) / 2
        for (sa, za), (sb, zb) in bars:  # the head: a band w wide just inside the curve
            ia = (cs + (sa - cs) * (r - w) / r, spring + (za - spring) * (r - w) / r)
            ib = (cs + (sb - cs) * (r - w) / r, spring + (zb - spring) * (r - w) / r)
            q = [pt(sa, za, off), pt(*ia, off), pt(*ib, off), pt(sb, zb, off)]
            b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)


def _on_wall(ring, opening):
    """The edge an opening (`at`, `to`) lies on: (edge start, direction, outward normal, s0, s1)."""
    ((i, s0, s1, _z0, _z1),) = [
        (e, *h)
        for e, hs in massing.edge_openings(ring, [dict(opening, z0=0.0, z1=0.0)]).items()
        for h in hs
    ]
    a, bb = ring[i][:2], ring[(i + 1) % len(ring)][:2]
    length = math.dist(a, bb)
    u = ((bb[0] - a[0]) / length, (bb[1] - a[1]) / length)
    return a, u, (u[1], -u[0]), s0, s1


def _storefront(b, ring, dr, hexes):
    """The fixed part of an entrance (`doors`: `at`, `to`, `z0` the sill, `z1` the head, `frame`,
    `leaves`): reveals round the opening, a head bar, and glass with a frame in every stretch the
    leaves leave open (sidelights, the panel between pairs). The leaves are objects of their own
    (door_leaves)."""
    a, u, n, s0, s1 = _on_wall(ring, dr)
    z0, z1, back = dr["z0"], dr["z1"], dr.get("glass_back", 0.12)
    reveal = kit.mat("plaster", "reveal_" + hexes["wall"][1:], kit.srgb(hexes["wall"]), 0.9)
    fhex = dr.get("frame", "#592d28")
    frame = kit.mat("metal", "frame_" + fhex[1:], kit.srgb(fhex), 0.5)
    glass = kit.mat("glass", "window", kit.srgb("#2b3640"), 0.15)

    def pt(s, z, off):
        return (a[0] + u[0] * s + n[0] * off, a[1] + u[1] * s + n[1] * off, z)

    for sx, sy in ((s0, 1), (s1, -1)):
        q = [pt(sx, z0, 0), pt(sx, z0, -0.3), pt(sx, z1, -0.3), pt(sx, z1, 0)]
        b.faces(q if sy > 0 else q[::-1], [(0, 1, 2, 3)], reveal)
    leaves = sorted(
        tuple(sorted(_on_wall(ring, lf)[3:5])) for lf in dr.get("leaves", ())
    )
    gaps, at = [], s0
    for la, lb in leaves:
        if la - at > 0.02:
            gaps.append((at, la))
        at = lb
    if s1 - at > 0.02:
        gaps.append((at, s1))
    f = 0.08
    for ga, gb in gaps:
        b.faces([pt(ga, z0, -back), pt(gb, z0, -back), pt(gb, z1, -back), pt(ga, z1, -back)],
                [(0, 1, 2, 3)], glass)  # fmt: skip
        for off in (-back + 0.01, -back - 0.01):
            bars = ((ga, ga + f, z0, z1), (gb - f, gb, z0, z1), (ga, gb, z0, z0 + 0.2))
            for ra, rb, rz0, rz1 in bars:
                q = [pt(ra, rz0, off), pt(rb, rz0, off), pt(rb, rz1, off), pt(ra, rz1, off)]
                b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)
    for off in (-back + 0.01, -back - 0.01):  # the head bar over the whole opening
        q = [pt(s0, z1 - f, off), pt(s1, z1 - f, off), pt(s1, z1, off), pt(s0, z1, off)]
        b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)


def door_leaves(lay_part, building_id):
    """The swinging leaves of a part's entrance (`doors.leaves`: `name` (starting DOOR_), `at`,
    `to`, `hinge` "at" or "to", `pair`) as objects of their own, each a glass leaf in a frame with
    a pull, carrying a `door` custom property for the viewer (#119): id (one per pair; the leaves
    of a pair open together), building, kind swing, hinge [x, y, z] and axis in Blender world
    coordinates, and `open` (degrees about the axis that turn the leaf out of the building). Each
    leaf has materials of its own (told apart by a `door_leaf` extra, since the export's dedup
    ignores names), so the export's join keeps it a node of its own."""
    dr = lay_part.get("doors")
    if not dr:
        return []
    ring = geom.expand(lay_part["ring"], True)
    if geom.area(ring) < 0:
        ring = ring[::-1]
    z0, z1, back = dr["z0"], dr["z1"] - 0.1, dr.get("glass_back", 0.12)
    fhex = dr.get("frame", "#592d28")
    out = []
    for lf in dr["leaves"]:
        a, u, n, s0, s1 = _on_wall(ring, lf)
        tag = lf["name"].lower()
        frame = kit.mat("metal", tag + "_frame", kit.srgb(fhex), 0.5)
        glass = kit.mat("glass", tag + "_glass", kit.srgb("#2b3640"), 0.15)
        steel = kit.mat("metal", tag + "_pull", kit.srgb("#b7b9bb"), 0.35)
        for m in (frame, glass, steel):  # the export's dedup ignores names; an extra keeps it apart
            m["door_leaf"] = lf["name"]

        def pt(s, z, off, a=a, u=u, n=n):
            return (a[0] + u[0] * s + n[0] * off, a[1] + u[1] * s + n[1] * off, z)

        b = kit.Builder("SW_" + lf["name"])  # renamed to its DOOR_ name below (viewer #119)
        pane = [pt(s0, z0, -back), pt(s1, z0, -back), pt(s1, z1, -back), pt(s0, z1, -back)]
        b.faces(pane, [(0, 1, 2, 3)], glass)
        f = 0.1
        # which end of the leaf (s0 < s1 along the wall) is the hinge: the end its `hinge` names
        named = lf[lf.get("hinge", "at")]
        s_named = (named[0] - a[0]) * u[0] + (named[1] - a[1]) * u[1]
        hinge_s = s0 if abs(s_named - s0) < abs(s_named - s1) else s1
        free = s1 if hinge_s == s0 else s0  # the meeting stile carries the pull
        for off in (-back + 0.02, -back - 0.02):
            bars = ((s0, s0 + f, z0, z1), (s1 - f, s1, z0, z1), (s0, s1, z1 - f, z1),
                    (s0, s1, z0, z0 + 0.25))  # fmt: skip
            for ra, rb, rz0, rz1 in bars:
                q = [pt(ra, rz0, off), pt(rb, rz0, off), pt(rb, rz1, off), pt(ra, rz1, off)]
                b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], frame)
            ps = free - 0.18 if free == s1 else free + 0.18
            po = off * 1.6  # the pull stands off the leaf
            q = [pt(ps - 0.02, z0 + 0.9, po), pt(ps + 0.02, z0 + 0.9, po),
                 pt(ps + 0.02, z0 + 1.6, po), pt(ps - 0.02, z0 + 1.6, po)]  # fmt: skip
            b.faces(q if off > -back else q[::-1], [(0, 1, 2, 3)], steel)
        ob = b.finish(recalc=False)
        ob.name = lf["name"]
        hinge, angle = massing.door_swing(
            pt(hinge_s, 0, -back)[:2], pt(free, 0, -back)[:2], "at", n
        )
        ob["door"] = {
            "id": f"{building_id}_{lf['pair']}", "building": building_id, "kind": "swing",
            "hinge": [round(hinge[0], 3), round(hinge[1], 3), round(z0, 3)], "axis": [0, 0, 1],
            "open": angle,
        }  # fmt: skip
        out.append(ob)
    return out


def _deck_levels(b, part, ring, top, ground, band, void):
    """Open parking levels: a dark opening between spandrel bands, columns every 9 m."""
    levels = part.get("levels", 4)
    low = min(ground(*p) for p in ring)
    h = (top - PARAPET["deck"] - low) / max(1, levels - 1)  # the top level is the roof deck
    for _i, a, _b, length, u, nrm in _edges(ring):
        cols = [0.0] + massing.bays(length, 9.0, 0.0) + [length]
        for lv in range(levels - 1):
            z0 = top - PARAPET["deck"] - (lv + 1) * h
            g = min(ground(a[0], a[1]), ground(a[0] + u[0] * length, a[1] + u[1] * length))
            if z0 + h < g + 0.5:
                continue
            _panel(b, a, u, nrm, 0.0, length, max(z0 + 1.1, g), z0 + h - 0.5, void, off=0.02)
            for s in cols:
                s0, s1 = max(0.0, s - 0.3), min(length, s + 0.3)
                if s1 - s0 > 0.1:
                    _panel(b, a, u, nrm, s0, s1, max(z0, g - 0.5), z0 + h, band)


def _canopy(name, p, ring, kind, tops, slopes, ground, roof_hex):
    """An open canopy (`"open": true`): the roof as a 0.2 m slab on a row of posts along its long
    axis, no walls. Used for solar canopies over parking and for shelters.
    """
    b = kit.Builder(name)
    sheet = kit.mat("metal", "roof_" + roof_hex[1:], kit.srgb(roof_hex), 0.5, 0.3)
    steel = kit.mat("metal", "canopy_steel", kit.srgb("#8d9195"), 0.5, 0.7)
    soffit = p.get("soffit")  # the slab's underside in the plan's soffit colour, if it gives one
    under_mat = kit.mat("paint", "soffit_" + soffit[1:], kit.srgb(soffit), 0.8) if soffit else steel
    faces = slopes or [[(q[0], q[1], p["top"]) for q in ring]]
    for face in faces:
        b.faces(face, [tuple(range(len(face)))], sheet)
        under = [(x, y, z - 0.2) for x, y, z in face]
        b.faces(under, [tuple(range(len(face) - 1, -1, -1))], under_mat)
        m = len(face)
        rim = face + under
        b.faces(rim, [((i + 1) % m, i, m + i, m + (i + 1) % m) for i in range(m)], steel)
    # the roof plane through the wall tops, to stand the posts under it
    (x0, y0), z0 = ring[0], tops[0]
    far = max(range(len(ring)), key=lambda i: (ring[i][0] - x0) ** 2 + (ring[i][1] - y0) ** 2)
    off = max(
        range(len(ring)),
        key=lambda i: abs(
            (ring[far][0] - x0) * (ring[i][1] - y0) - (ring[far][1] - y0) * (ring[i][0] - x0)
        ),
    )
    ax, ay, az = ring[far][0] - x0, ring[far][1] - y0, tops[far] - z0
    bx, by, bz = ring[off][0] - x0, ring[off][1] - y0, tops[off] - z0
    det = (ax * by - ay * bx) or 1.0
    gx, gy = (az * by - bz * ay) / det, (ax * bz - bx * az) / det

    def roof_z(x, y):
        if kind in ("gable", "hip"):
            return p["top"]  # the posts stand under the ridge
        return z0 + gx * (x - x0) + gy * (y - y0)

    ang = geom.long_axis(ring)
    to_local, to_model = geom.frame((0.0, 0.0), ang)
    loc = [to_local(q[0], q[1]) for q in ring]
    u0, u1 = min(q[0] for q in loc), max(q[0] for q in loc)
    v0, v1 = min(q[1] for q in loc), max(q[1] for q in loc)
    vm = (v0 + v1) / 2
    # end posts 3 m in from the ends (under a hip: where the ridge begins), the rest no more
    # than 9 m apart
    end = (v1 - v0) / 2 if kind == "hip" else 3.0
    span = u1 - u0 - 2 * end
    count = max(1, math.ceil(span / 9.0)) + 1 if span > 1.0 else 1
    us = [u0 + end + span * i / (count - 1) for i in range(count)] if count > 1 else [(u0 + u1) / 2]
    for u in us:
        x, y = to_model(u, vm)
        foot, head = ground(x, y) - 0.3, roof_z(x, y) - 0.2
        b.box((x, y, (foot + head) / 2), (0.3, 0.3, head - foot), steel, angle=ang)
    return b.finish(recalc=False)


def part(lay_part, name, ground, image_dir=None):
    """One building part as an object. `ground(x, y)` gives the terrain height; `image_dir` holds
    the paint sheets (paint.py) of a painted roof."""
    p = lay_part
    ring = geom.expand(p["ring"], True)
    if geom.area(ring) < 0:
        ring = ring[::-1]
    style = p.get("style", "shed")
    hexes = dict(wall=p.get("wall", "#b9b6ad"), trim=p.get("trim", "#d9d6cc"))
    hexes["roof"] = p.get("roof_colour", "#8f9194")
    wall = kit.mat(
        WALL_KIND.get(style, "plaster"), "wall_" + hexes["wall"][1:], kit.srgb(hexes["wall"]), 0.9
    )
    trim = kit.mat("concrete", "trim_" + hexes["trim"][1:], kit.srgb(hexes["trim"]), 0.8)
    kind = p.get("roof", "flat")
    tops, slopes, gables = massing.roof(ring, kind, p["top"], p.get("eave"), p.get("ridge_angle"))
    # walls go 0.6 m into the lowest ground round the part, or stand on another part's roof
    samples = [q[:2] for q in geom.resample(ring, 2.0, True)]
    base = p["base"] if "base" in p else min(ground(x, y) for x, y in samples) - 0.6
    # wide eaves (`overhang`): faces that carry each roof face past the walls in its own plane
    eaves = massing.overhang_roof(ring, slopes, p["overhang"]) if p.get("overhang") else []
    if p.get("overhang") and kind not in ("gable", "hip"):
        raise ValueError(f"{name}: an overhang needs a gable or hip roof (or a mansard)")
    if p.get("open"):
        return _canopy(name, p, ring, kind, tops, slopes + eaves, ground, hexes["roof"])
    b = kit.Builder(name)
    n = len(ring)
    v = [(q[0], q[1], base) for q in ring] + [
        (q[0], q[1], z) for q, z in zip(ring, tops, strict=True)
    ]
    # a deck's ramp is a slab in the well of its deck: walls of its own would lie in the faces of
    # the well's walls
    cuts = list(p.get("openings", ())) + list(p.get("curtains", ())) + list(p.get("arches", ()))
    cuts += [p["doors"]] if p.get("doors") else []
    holes = massing.edge_openings(ring, cuts) if cuts else {}
    # a window of the grid never crosses an opening or a curtain wall
    cells = massing.clear_of(_recessed_cells(p, ring, tops, ground), holes)
    for c in cells:  # recessed windows are openings too
        holes.setdefault(c["edge"], []).append((c["s0"], c["s1"], c["z0"], c["z1"]))
    if holes:  # walls cut round the openings (a flat-topped part: one top per edge)
        for i, a, _e, length, u, _nrm in _edges(ring):
            for s0, s1, za, zb in massing.wall_pieces(length, base, tops[i], holes.get(i, [])):
                corners = ((s0, za), (s1, za), (s1, zb), (s0, zb))
                q = [(a[0] + u[0] * s, a[1] + u[1] * s, z) for s, z in corners]
                b.faces(q, [(0, 1, 2, 3)], wall)
    elif not (kind == "shed" and style == "deck"):
        b.faces(v, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], wall)
    for face in gables:
        b.faces(face, [tuple(range(len(face)))], wall)
    if kind == "flat":
        deck = kit.mat("concrete", "roof_" + hexes["roof"][1:], kit.srgb(hexes["roof"]), 0.85)
        if p.get("sheets"):  # the plan paints this roof (layout.roof_paint, paint.py)
            deck = sheet_material("concrete", p["sheets"][0], image_dir)
        wells = _wells(p, hexes["roof"])
        _flat_roof(b, ring, p["top"], p.get("parapet", PARAPET.get(style, 0.4)), trim, deck, wells)
        if p.get("ring_roof"):  # a tiled band round the flat roof (a mansard ring)
            r = p["ring_roof"]
            tile = kit.mat("rooftile", "roof_" + r["colour"][1:], kit.srgb(r["colour"]), 0.75)
            for face in massing.ring_roof(
                ring, p["top"], r["crest"], r["crest_in"], r["inner_in"],
                p["top"] - p.get("parapet", PARAPET.get(style, 0.4)), r.get("flat_edges", ()),
                overhang=r.get("overhang"),
            ):  # fmt: skip
                b.faces(face, [tuple(range(len(face)))], tile)
            if r.get("soffit"):  # the underside of the overhang and a fascia board
                sof = kit.mat("wood", "soffit_" + r["soffit"][1:], kit.srgb(r["soffit"]), 0.8)
                for face in massing.ring_soffits(
                    ring, p["top"], r["crest"], r["crest_in"], r.get("flat_edges", ()),
                    overhang=r.get("overhang"),
                ):  # fmt: skip
                    b.faces(face, [tuple(range(len(face)))], sof)
            if r.get("caps"):  # ridge and hip caps, a darker tile
                cap = kit.mat("rooftile", "cap_" + r["caps"][1:], kit.srgb(r["caps"]), 0.75)
                for verts, faces in massing.ring_caps(
                    ring, p["top"], r["crest"], r["crest_in"], r.get("flat_edges", ()),
                    overhang=r.get("overhang"),
                ):  # fmt: skip
                    b.faces(verts, [tuple(f) for f in faces], cap)
            if r.get("eave_course"):  # walls with no overhang: a tile course on the wall top
                cap = kit.mat("rooftile", "cap_" + r["caps"][1:], kit.srgb(r["caps"]), 0.75)
                for verts, faces in massing.eave_course(ring, r["eave_course"], p["top"]):
                    b.faces(verts, [tuple(f) for f in faces], cap)
    else:
        # a deck's sloped slab (a ramp bay) is concrete; other pitched roofs are sheet metal
        look = ("concrete", 0.85, 0.0) if style == "deck" else ("metal", 0.55, 0.2)
        sheet = kit.mat(look[0], "roof_" + hexes["roof"][1:], kit.srgb(hexes["roof"]), *look[1:])
        if p.get("sheets"):  # a deck's ramp painted by the plan (layout.roof_paint, paint.py)
            sheet = deck = sheet_material("concrete", p["sheets"][0], image_dir)
        wells = _wells(p, hexes["roof"])
        if wells:  # wells sink into the flat top of a mansard, the last face of `slopes`
            if kind not in ("gable", "hip") or n == 4:
                raise ValueError(f"{name}: wells need a flat roof or a mansard top")
            cap = slopes.pop()
            _deck(b, [q[:2] for q in cap], p["top"], wells, sheet, trim)
        if eaves:
            _soffit(b, eaves, ring, p.get("soffit", hexes["trim"]), p["overhang"])
        for face in slopes + eaves:
            b.faces(face, [tuple(range(len(face)))], sheet)
    wall_top = min(tops) - (p.get("parapet", PARAPET.get(style, 0.4)) if kind == "flat" else 0.0)

    def local(x, y):  # a part on a roof has that roof as its ground
        return p["base"] if "base" in p else ground(x, y)

    if style == "deck" and kind == "flat":
        void = kit.mat("paint", "deck_opening", kit.srgb("#1b1c1e"), 0.95)
        _deck_levels(b, p, ring, p["top"], local, wall, void)
    elif cells:
        _recessed(b, p, cells, hexes)
    elif p.get("windows"):
        glass = kit.mat("glass", "window", kit.srgb("#2b3640"), 0.15)
        _windows(b, p, ring, wall_top, local, glass, holes)
    for cw in p.get("curtains", ()):
        _curtain(b, ring, cw, hexes)
    for aw in p.get("arches", ()):
        _arch(b, ring, aw, hexes, wall)
    if p.get("doors"):
        _storefront(b, ring, p["doors"], hexes)
    if p.get("sheets"):
        _sheet_uvs(b, deck, p["sheets"][0])
    return b.finish(recalc=False)  # every face here is wound by hand; panels are loose quads


def _soffit(b, eaves, ring, colour, overhang, depth=0.15):
    """The underside of the eaves (massing.overhang_roof): each face again `depth` lower, facing
    down, and a fascia along the roof's outer edge (eave edges only one face has, off the wall
    line)."""
    mat = kit.mat("paint", "soffit_" + colour[1:], kit.srgb(colour), 0.8)
    count = {}

    def key(a, c):
        return tuple(sorted((tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in c))))

    for face in eaves:
        under = [(x, y, z - depth) for x, y, z in face]
        b.faces(under, [tuple(range(len(face) - 1, -1, -1))], mat)
        for i in range(len(face)):
            k = key(face[i], face[(i + 1) % len(face)])
            count[k] = count.get(k, 0) + 1
    walls = [(ring[i], ring[(i + 1) % len(ring)]) for i in range(len(ring))]
    for face in eaves:
        for i in range(len(face)):
            a, c = face[i], face[(i + 1) % len(face)]
            far = min(0.05, overhang / 2)  # off the wall line, even for a narrow overhang
            outside = all(min(massing._seg_dist(q[:2], *w) for w in walls) > far for q in (a, c))
            if count[key(a, c)] == 1 and outside:
                q = [c, a, (a[0], a[1], a[2] - depth), (c[0], c[1], c[2] - depth)]
                b.faces(q, [(0, 1, 2, 3)], mat)


def _sheet_uvs(b, material, sheet):
    """Map the faces of `material` onto a paint sheet: plan metres to the sheet's 0..1."""
    uv = b.bm.loops.layers.uv.get("UVMap") or b.bm.loops.layers.uv.new("UVMap")
    k = b.slot(material)
    for f in b.bm.faces:
        if f.material_index == k:
            for loop in f.loops:
                loop[uv].uv = layout.sheet_uv(sheet, loop.vert.co.x, loop.vert.co.y)


def build(lay, terrain, name_of):
    """Every plan building that gives a roof height (`top`). Returns the objects."""
    out = []
    for p in lay["buildings"]:
        if "top" in p:
            out.append(part(p, name_of(p) + "_UNVERIFIED", terrain.at, lay.get("image_dir")))
            out += door_leaves(p, p.get("doors", {}).get("building", "building"))
    return out
