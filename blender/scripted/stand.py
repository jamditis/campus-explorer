"""Sprague Field stands: the elevated west grandstand, its press box, and the low east bleachers.

Read from the athletics photos (/workspace/refs/sw/meta.txt): the west stand is an aluminium
bleacher on an open galvanised frame with red risers, a front walkway and guard rail, aisles with
handrails, stairs down to the ground at the front and black chain-link guards on the back and
ends; a red press box with a dark flat roof and a steel stair stands behind it. Its field face is
grey siding with red trim and a window band (C04A0106). The east stands are ground bleachers with
red end and back panels and no red risers (DSC05256). Every size here is inferred from the photos,
not measured, so objects carry `_UNVERIFIED` unless the caller says otherwise.
"""

import math
import os
import sys

try:
    import bpy
except ImportError:  # outside Blender: the unit tests use the pure bowl parts
    bpy = None

try:
    import kit
except ImportError:  # run as a script: demo() puts this folder on sys.path first (or no Blender)
    kit = None

GUARD = 1.07  # guard height above a walking surface (IBC 1015)
DEFAULTS = {
    "plank": "#c9cdd1",
    "frame": "#9aa1a4",
    "panel": "#a3222a",
    "footing": "#aaa59c",
    "chainlink": "#1d1f20",
}


def materials(colours=None):
    """The stand materials. Non-default colours get their own material names."""
    c = {**DEFAULTS, **(colours or {})}

    def nm(key, base):
        return base if c[key] == DEFAULTS[key] else f"{base}_{c[key].lstrip('#')}"

    return {
        "plank": kit.mat("metal", nm("plank", "aluminium_plank"), kit.srgb(c["plank"]), 0.45, 0.9),
        "frame": kit.mat("metal", nm("frame", "galvanised_steel"), kit.srgb(c["frame"]), 0.55, 0.8),
        "panel": kit.mat("metal", nm("panel", "red_panel"), kit.srgb(c["panel"]), 0.5, 0.3),
        "footing": kit.mat("concrete", nm("footing", "footing"), kit.srgb(c["footing"]), 0.9),
        "chain": kit.mat(
            "metal",
            nm("chainlink", "chainlink_black"),
            kit.srgb(c["chainlink"]),
            0.6,
            0.5,
            alpha=0.45,
        ),
    }


class Local:
    """A kit.Builder that takes stand-local coordinates (u along, v back, w up)."""

    def __init__(self, name, place, angle):
        self.b, self.p, self.a = kit.Builder(name), place, angle

    def box(self, u0, u1, v0, v1, w0, w1, m):
        c = self.p((u0 + u1) / 2, (v0 + v1) / 2, (w0 + w1) / 2)
        self.b.box(c, (u1 - u0, v1 - v0, w1 - w0), m, angle=self.a)

    def beam(self, p0, p1, m, width=0.05, depth=None):
        """Member from p0 to p1. Vertical ones are posts squared to the stand and 1.5 cm thicker
        than asked, so their faces never line up with the rails and braces they carry."""
        if p0[:2] == p1[:2]:
            r = (width + 0.015) / 2
            u, v = p0[:2]
            self.box(u - r, u + r, v - r, v + r, min(p0[2], p1[2]), max(p0[2], p1[2]), m)
        else:
            self.b.beam(self.p(*p0), self.p(*p1), width, depth or width, m)

    def plate(self, pts, du, m):
        """Convex outline [(v, w), ...] at u = pts' u, extruded by du along u."""
        u, ring = pts[0], pts[1:]
        n = len(ring)
        vs = [self.p(u, v, w) for v, w in ring] + [self.p(u + du, v, w) for v, w in ring]
        f = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        self.b.faces(vs, f + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], m)

    def column(self, u, v, top, m, foot, size=0.2, pad=0.6):
        """Steel column on a small concrete footing (footing top 0.15 m above grade)."""
        self.box(u - pad / 2, u + pad / 2, v - pad / 2, v + pad / 2, -0.25, 0.15, foot)
        self.beam((u, v, 0.1), (u, v, top), m, size)

    def finish(self):
        return self.b.finish()


def rail_run(lc, u0, u1, v, w, m, heights=(GUARD, 0.55), spacing=2.4, post=0.05):
    """Guard rail along u at v on a surface at height w: posts and horizontal rails."""
    n = max(1, math.ceil((u1 - u0) / spacing))
    for k in range(n + 1):
        u = u0 + (u1 - u0) * k / n
        lc.beam((u, v, w - 0.04), (u, v, w + max(heights) + 0.03), m, post)
    for h in heights:
        lc.beam((u0, v, w + h), (u1, v, w + h), m, 0.045)


def grandstand(
    name,
    at,
    angle,
    length,
    depth,
    rows,
    *,
    first_row_height=1.2,
    rise=0.2,
    tread=0.7,
    sections=None,
    aisle_width=1.2,
    frame=True,
    back_height=None,
    colours=None,
    unverified=True,
):
    """Elevated aluminium bleacher. `at` = (x, y, z) of the front-left corner at ground level;
    `angle` = direction of the front edge (the edge nearest the field) from east. Rows rise away
    from the front. Returns a list of objects.

    Inferred: the front walkway is what `depth` leaves after `rows * tread` (at least 1.5 m, the
    tread shrinks to fit); row 1's foot plank is level with it; seats are 0.43 m above the foot
    plank with a red riser under each; one stair to the ground at every other aisle.
    """
    m, place, tag = materials(colours), kit.placer(at, angle), "_UNVERIFIED" if unverified else ""
    walk = max(1.5, depth - rows * tread)
    t = (depth - walk) / rows
    fence = GUARD if back_height is None else back_height
    n = sections or max(1, round(length / 13))
    sec = (length - (n - 1) * aisle_width) / n
    h = [first_row_height + i * rise for i in range(rows)]
    a = [walk + i * t for i in range(rows)]
    h0, top = h[0], h[-1]
    aisles = [(k + 1) * sec + k * aisle_width for k in range(n - 1)]
    pl, pn, rl = (Local(f"{name}_{p}{tag}", place, angle) for p in ("planks", "panels", "rails"))

    pl.box(0, length, 0.02, walk - 0.02, h0 - 0.05, h0, m["plank"])  # front walkway
    pn.box(0, length, -0.04, -0.02, h0 - 0.4, h0 + 0.02, m["panel"])  # front fascia
    for i in range(rows):
        b = a[i] + t - 0.02
        for k in range(n):
            u0 = k * (sec + aisle_width)
            pl.box(u0, u0 + sec, a[i] + 0.02, b - 0.33, h[i] - 0.05, h[i], m["plank"])
            pl.box(u0, u0 + sec, b - 0.3, b, h[i] + 0.38, h[i] + 0.43, m["plank"])
            pn.box(
                u0 + 0.03, u0 + sec - 0.03, b - 0.16, b - 0.14, h[i] - 0.15, h[i] + 0.4, m["panel"]
            )
        for ua in aisles:  # full step at the row level, half step halfway up
            pl.box(
                ua + 0.03,
                ua + aisle_width - 0.03,
                a[i] + 0.02,
                a[i] + t / 2,
                h[i] - 0.05,
                h[i],
                m["plank"],
            )
            pl.box(
                ua + 0.03,
                ua + aisle_width - 0.03,
                a[i] + t / 2 + 0.02,
                b,
                h[i] + rise / 2 - 0.05,
                h[i] + rise / 2,
                m["plank"],
            )

    for ua in aisles:  # aisle handrail on the centre line, a post every fourth row
        uc = ua + aisle_width / 2
        rl.beam(
            (uc, a[0] + 0.1, h0 + 0.9), (uc, a[-1] + t - 0.1, top + 0.9 + rise), m["frame"], 0.05
        )
        for i in range(0, rows, 4):
            rl.beam((uc, a[i] + 0.15, h[i] - 0.04), (uc, a[i] + 0.15, h[i] + 0.93), m["frame"])

    # stairs from the walkway to the ground in front of every other aisle, running along +u
    gaps, risers = [], math.ceil(h0 / 0.18)
    rh, go = h0 / risers, 0.28
    for ua in aisles[::2] or [1.0]:
        g = ua + aisle_width / 2 - 0.6
        gaps.append(g)
        pl.box(g, g + 1.2, -1.4, -0.07, h0 - 0.05, h0, m["plank"])  # landing
        u1 = g + 1.2 + (risers - 1) * go
        for j in range(1, risers):
            u = g + 1.2 + (j - 1) * go
            pl.box(u + 0.01, u + go, -1.38, -0.1, h0 - j * rh - 0.04, h0 - j * rh, m["plank"])
        for v in (-1.4, -0.08):
            rl.beam((g + 1.2, v, h0 - 0.12), (u1 + 0.1, v, -0.1), m["frame"], 0.06, 0.25)
            rl.beam((g + 1.2, v, h0 + 0.9), (u1, v, 0.9 + rh), m["frame"])
            rl.beam((u1, v, -0.05), (u1, v, 0.95 + rh), m["frame"])
        rail_run(rl, g, g + 1.2, -1.4, h0, m["frame"], spacing=1.2)
        rl.beam((g, -1.4, h0 + 1.04), (g, -0.08, h0 + 1.04), m["frame"], 0.045)
        for u in (g, g + 1.2):
            rl.beam((u, -1.4, 0.1), (u, -1.4, h0 - 0.03), m["frame"], 0.1)

    spans, u = [], 0.0
    for g in gaps:
        spans.append((u, g))
        u = g + 1.2
    for u0, u1 in [*spans, (u, length)]:
        rail_run(rl, u0, u1, 0.07, h0, m["frame"])

    # back and end guards: black chain-link with posts and rails
    vb = depth + 0.03
    rl.box(0.02, length - 0.02, vb - 0.01, vb + 0.01, top - 0.13, top + fence, m["chain"])
    rail_run(rl, 0, length, vb, top, m["frame"], heights=(fence,), spacing=3.0, post=0.06)
    rl.beam((0, vb, top - 0.12), (length, vb, top - 0.12), m["frame"], 0.06)
    for u, du in ((-0.04, 0.02), (length + 0.02, 0.02)):
        uc = u + du / 2
        w0, w1 = walk - 0.02, walk + 0.02  # the two plates meet behind the post at the walkway
        rl.plate(
            [u, (w1, h0 - 0.15), (vb, top - 0.15), (vb, top + fence), (w1, h0 + fence)],
            du,
            m["chain"],
        )
        rl.plate(
            [u, (0.02, h0 - 0.15), (w0, h0 - 0.15), (w0, h0 + GUARD), (0.02, h0 + GUARD)],
            du,
            m["chain"],
        )
        rl.beam((uc, walk, h0 + fence), (uc, vb, top + fence), m["frame"], 0.05)
        rl.beam((uc, 0.07, h0 + GUARD), (uc, walk, h0 + GUARD), m["frame"], 0.04)
        rl.beam((uc, walk, h0 - 0.03), (uc, walk, h0 + fence + 0.03), m["frame"], 0.05)
    objs = [pl.finish(), pn.finish(), rl.finish()]
    if frame:
        objs.append(
            _stand_frame(
                f"{name}_frame{tag}", place, angle, length, depth, rows, walk, t, h, rise, m
            )
        )
    return objs


def _stand_frame(oname, place, angle, length, depth, rows, walk, t, h, rise, m):
    """Open steel frame: a stringer under each row, rakers on column lines about 3.6 m apart,
    girders under the walkway, ties, X braces in every third line and some back bays (inferred)."""
    fr, h0 = Local(oname, place, angle), h[0]

    def raker_top(v):
        return h0 - 0.13 + (v - walk - 0.17) * rise / t

    for i in range(rows):  # stringers, tops embedded 2 cm in the foot planks
        v = walk + i * t + 0.17
        fr.beam((0.12, v, h[i] - 0.09), (length - 0.12, v, h[i] - 0.09), m["frame"], 0.08, 0.12)
    for v in (0.3, walk - 0.4):
        fr.beam((0.12, v, h0 - 0.09), (length - 0.12, v, h0 - 0.09), m["frame"], 0.08, 0.12)
    nu = max(1, round(length / 3.6))
    nv = max(1, round((depth - walk) / 3.6))
    us = [0.15 + (length - 0.3) * k / nu for k in range(nu + 1)]
    vs = [0.3, walk] + [walk + (depth - walk - 0.25) * j / nv for j in range(1, nv + 1)]
    tops = [h0 - 0.36] + [raker_top(v) - 0.25 for v in vs[1:]]
    for k, u in enumerate(us):
        fr.beam((u, 0.05, h0 - 0.26), (u, walk + 0.3, h0 - 0.26), m["frame"], 0.14, 0.25)
        fr.beam(
            (u, walk, raker_top(walk) - 0.15),
            (u, depth, raker_top(depth) - 0.15),
            m["frame"],
            0.1,
            0.3,
        )
        for v, w in zip(vs, tops, strict=True):
            fr.column(u, v, w, m["frame"], m["footing"])
        if k % 3 == 0:
            for j in range(1, len(vs) - 1):
                fr.beam((u, vs[j], 0.4), (u, vs[j + 1], tops[j + 1] - 0.2), m["frame"], 0.08)
                fr.beam((u, vs[j + 1], 0.4), (u, vs[j], tops[j] - 0.2), m["frame"], 0.04)
    for v, w in zip(vs, tops, strict=True):
        fr.beam((us[0], v, w * 0.5), (us[-1], v, w * 0.5), m["frame"], 0.08, 0.12)
    for k in range(1, nu, 4):
        for v, w in ((vs[-1], tops[-1]), (vs[0], tops[0])):
            fr.beam((us[k], v + 0.12, 0.4), (us[k + 1], v + 0.12, w - 0.2), m["frame"], 0.08)
            fr.beam((us[k + 1], v + 0.12, 0.4), (us[k], v + 0.12, w - 0.2), m["frame"], 0.04)
    return fr.finish()


# Solid concrete seating bowl (Yogi Berra Stadium): stepped concrete on fill, read from the
# LiDAR, which classes the whole deck as ground. No frame, no columns, no stairs to the ground.
# Levels are absolute (NAVD88 metres); v runs back from the front edge, u along it.
BOWL_TREAD = 0.85  # row depth measured on the Yogi Berra Stadium LiDAR profiles


def bowl_profile(walk, tiers, aisles, back, depth, tread=BOWL_TREAD):
    """The flats of a bowl from the front edge back: a front walkway, rows in tiers with a cross
    aisle between each pair of tiers, then a back walkway at `back` up to `depth` if room is left.

    `walk` = [depth, level]; a tier = {"rows", "first" (level of its first row), "rise"}; an aisle
    = {"width", "level"}. Returns [{"kind", "v": (v0, v1), "level", "row", "tier"}]; rows are
    numbered from 0 through all tiers.
    """
    if len(aisles) != len(tiers) - 1:
        raise ValueError("a bowl needs one cross aisle between each pair of tiers")

    def flat(kind, v0, v1, level, row=None, tier=None):
        return dict(kind=kind, v=(v0, v1), level=level, row=row, tier=tier)

    flats = [flat("walk", 0.0, walk[0], walk[1])] if walk[0] > 0 else []
    v, row = walk[0], 0
    for k, t in enumerate(tiers):
        for i in range(t["rows"]):
            flats.append(flat("row", v, v + tread, t["first"] + i * t["rise"], row, k))
            v, row = v + tread, row + 1
        if k < len(aisles):
            flats.append(flat("aisle", v, v + aisles[k]["width"], aisles[k]["level"]))
            v += aisles[k]["width"]
    if v > depth + 1e-6:
        raise ValueError(f"the rows run to {v:.2f} m, past the stand's depth {depth:.2f} m")
    if v < depth - 1e-6:
        flats.append(flat("back", v, depth, back))
    return flats


def bowl_block(length, flats, base):
    """The solid stepped block of a bowl `length` long: vertices (u, v, w) and faces wound
    anticlockwise seen from outside. Treads and risers run the whole length; each end is one
    strip per flat (its edges carry the neighbours' corners, so the shell is closed); the front,
    back and bottom are one face each."""
    verts, index = [], {}

    def vid(u, v, w):
        key = (round(u, 9), round(v, 9), round(w, 9))
        if key not in index:
            index[key] = len(verts)
            verts.append((u, v, w))
        return index[key]

    L, n = length, len(flats)
    lv = [f["level"] for f in flats]
    faces = []
    for k, f in enumerate(flats):
        v0, v1 = f["v"]
        faces.append([vid(0, v0, lv[k]), vid(L, v0, lv[k]), vid(L, v1, lv[k]), vid(0, v1, lv[k])])
        if k + 1 < n and lv[k + 1] != lv[k]:  # riser: faces the field going up, the back going down
            faces.append(
                [vid(0, v1, lv[k]), vid(L, v1, lv[k]), vid(L, v1, lv[k + 1]), vid(0, v1, lv[k + 1])]
            )
        ring = [(v0, base), (v1, base)]
        if k + 1 < n and base < lv[k + 1] < lv[k]:
            ring.append((v1, lv[k + 1]))
        ring += [(v1, lv[k]), (v0, lv[k])]
        if k > 0 and base < lv[k - 1] < lv[k]:
            ring.append((v0, lv[k - 1]))
        faces.append([vid(L, v, w) for v, w in ring])  # the end at u = L faces +u
        faces.append([vid(0, v, w) for v, w in reversed(ring)])
    ve, top0, top1 = flats[-1]["v"][1], lv[0], lv[-1]
    faces.append([vid(0, 0, base), vid(L, 0, base), vid(L, 0, top0), vid(0, 0, top0)])
    faces.append([vid(0, ve, top1), vid(L, ve, top1), vid(L, ve, base), vid(0, ve, base)])
    edges = [0.0] + [f["v"][1] for f in flats]
    faces.append([vid(0, v, base) for v in edges] + [vid(L, v, base) for v in reversed(edges)])
    return verts, faces


def seat_for(seats, row, section):
    """The seat entry that covers this row (numbered through all tiers) and section, or None."""
    for s in seats:
        r0, r1 = s["rows"]
        if r0 <= row <= r1 and section in s.get("sections", [section]):
            return s
    return None


def bowl(name, at, angle, length, depth, spec, unverified=True):
    """A solid concrete seating bowl from a plan stand with `"style": "bowl"`: `at` = (x, y) of
    the front-left corner, `angle` the front edge's direction. `spec` carries `walk`, `tiers`,
    `aisles`, `back`, `base` (the block's bottom, below the ground in front), `tread`,
    `sections` and `aisle_width` (stair aisles: gaps in the seat rows) and `seats`.

    Seats are a simplification: one low box per row and section in the seat colour (`chairs`,
    0.45 m high) or an aluminium bench plank box (`bench`), not single chairs.
    """
    tag = "_UNVERIFIED" if unverified else ""
    place = kit.placer((at[0], at[1], 0.0), angle)
    flats = bowl_profile(
        spec["walk"],
        spec["tiers"],
        spec.get("aisles", []),
        spec["back"],
        depth,
        spec.get("tread", BOWL_TREAD),
    )
    verts, faces = bowl_block(length, flats, spec["base"])
    concrete = kit.mat("concrete", "seating_bowl", kit.srgb(spec.get("concrete", "#b5b1a8")), 0.9)
    b = kit.Builder(f"{name}_bowl{tag}")
    b.faces([place(*p) for p in verts], faces, concrete)
    out = [b.finish(recalc=False)]
    n, aw = int(spec.get("sections") or 1), spec.get("aisle_width", 1.2)
    sec = (length - (n - 1) * aw) / n
    seats = spec.get("seats", [])
    lc = Local(f"{name}_seats{tag}", place, angle)
    plank = materials()["plank"]
    for f in flats:
        if f["kind"] != "row":
            continue
        back, w = f["v"][1], f["level"]
        for k in range(n):
            s = seat_for(seats, f["row"], k)
            if s is None:
                continue
            u0 = k * (sec + aw)
            if s["type"] == "chairs":
                col = s.get("colour", "#a3322c")
                m = kit.mat("plastic", f"seat_{col.lstrip('#')}", kit.srgb(col), 0.5)
                lc.box(u0 + 0.05, u0 + sec - 0.05, back - 0.55, back - 0.1, w, w + 0.45, m)
            else:
                lc.box(u0 + 0.05, u0 + sec - 0.05, back - 0.35, back - 0.1, w, w + 0.43, plank)
    if seats:
        out.append(lc.finish())
    return out


def press_box(
    name,
    at,
    angle,
    length,
    depth,
    height,
    *,
    floor_z,
    stair_side="left",
    lettering=None,
    unverified=True,
):
    """Press box on the back of a stand: clad box with a window band toward the front (-v side),
    flat roof with a parapet rail, and an external steel stair from the ground to `floor_z`.

    Inferred: red cladding on the sides and back, grey siding below the windows on the field face
    (C04A0106), window band 1.0 m up to 0.6 m below the roof, steel columns at the corners, a
    switchback stair of two 1.0 m lanes beside the box with flights of at most 12 risers.
    """
    place, tag = kit.placer(at, angle), "_UNVERIFIED" if unverified else ""
    m = materials()
    red = kit.mat("metal", "pressbox_red", kit.srgb("#a8302c"), 0.5, 0.3)
    grey = kit.mat("metal", "pressbox_siding", kit.srgb("#8e99a2"), 0.5, 0.3)
    dark = kit.mat("metal", "roof_dark", kit.srgb("#3a3c3f"), 0.7, 0.3)
    glass = kit.mat("glass", "pressbox", kit.srgb("#3c4a55"), 0.05, 0.0, alpha=0.35)
    L, D, H, fz = length, depth, height, floor_z
    bx, st = Local(f"{name}{tag}", place, angle), Local(f"{name}_stair{tag}", place, angle)

    bx.box(-0.05, L + 0.05, -0.05, D + 0.05, fz - 0.3, fz, m["frame"])  # floor
    for u0 in (0, L - 0.15):
        bx.box(u0, u0 + 0.15, 0, D, fz - 0.12, fz + H - 0.02, red)
    bx.box(0.05, L - 0.05, D - 0.15, D - 0.03, fz - 0.1, fz + H, red)
    bx.box(0.05, L - 0.05, 0.03, 0.15, fz - 0.1, fz + 1.0, grey)
    bx.box(0.05, L - 0.05, 0.03, 0.15, fz + H - 0.6, fz + H, red)
    bx.box(0.1, L - 0.1, 0.09, 0.11, fz + 0.98, fz + H - 0.58, glass)
    nm = max(2, round(L / 1.5))
    for k in range(1, nm):
        u = L * k / nm
        bx.beam((u, 0.1, fz + 0.95), (u, 0.1, fz + H - 0.55), red, 0.06)
    bx.box(-0.15, L + 0.15, -0.15, D + 0.15, fz + H - 0.05, fz + H + 0.15, dark)  # roof
    if lettering:
        sign = kit.mat("sign", f"pressbox_{lettering.lower()}", kit.srgb("#e8e8e8"), 0.6)
        w = min(L * 0.4, 0.6 * len(lettering))
        bx.box(L / 2 - w / 2, L / 2 + w / 2, -0.01, 0.01, fz + H - 0.5, fz + H - 0.1, sign)
    side = -1 if stair_side == "left" else 1
    ue = -0.03 if side < 0 else L + 0.01
    bx.box(ue, ue + 0.02, 0.15, 1.0, fz + 0.02, fz + 2.1, dark)  # door to the top landing

    # roof parapet rail
    rt = fz + H + 0.15
    ring = [(-0.1, -0.1), (L + 0.1, -0.1), (L + 0.1, D + 0.1), (-0.1, D + 0.1)]
    for (u0, v0), (u1, v1) in zip(ring, ring[1:] + ring[:1], strict=True):
        span = math.hypot(u1 - u0, v1 - v0)
        for k in range(max(1, math.ceil(span / 3))):
            f = k / max(1, math.ceil(span / 3))
            st.beam(
                (u0 + (u1 - u0) * f, v0 + (v1 - v0) * f, rt - 0.03),
                (u0 + (u1 - u0) * f, v0 + (v1 - v0) * f, rt + GUARD + 0.03),
                m["frame"],
            )
        for hh in (GUARD, 0.55):  # rails along v sit 2 cm lower so the corners never coincide
            hh -= 0.02 * (u0 == u1)
            st.beam((u0, v0, rt + hh), (u1, v1, rt + hh), m["frame"], 0.045)

    # columns under the box, X braces in the back bays
    cu = [0.1, L - 0.1] if L <= 6 else [0.1, L / 2, L - 0.1]
    for u in cu:
        for v in (0.1, D - 0.1):
            st.column(u, v, fz - 0.25, m["frame"], m["footing"], pad=0.5)
    for u0, u1 in zip(cu, cu[1:], strict=False):
        st.beam((u0, D - 0.1, 0.4), (u1, D - 0.1, fz - 0.5), m["frame"], 0.08)
        st.beam((u1, D - 0.1, 0.4), (u0, D - 0.1, fz - 0.5), m["frame"], 0.04)

    # switchback stair: two lanes beside the box, the last flight arrives at the front landing
    risers = math.ceil(fz / 0.18)
    flights = math.ceil(risers / 12)
    r = math.ceil(risers / flights)
    rh, go = fz / (flights * r), 0.27
    run = (r - 1) * go
    v0, v1 = 1.1, 1.1 + run
    band = (-2.15, -0.07) if side < 0 else (L + 0.07, L + 2.15)
    lanes = [(band[1] - 1.0, band[1] - 0.04), (band[0], band[0] + 1.0)][::-side]
    for k in range(flights):
        z0, z1 = k * r * rh, (k + 1) * r * rh
        d = -1 if (flights - 1 - k) % 2 == 0 else 1
        vs, ve = (v1, v0) if d < 0 else (v0, v1)
        la, lb = lanes[k % 2]
        for j in range(1, r):
            p = vs + d * (j - 1) * go
            st.box(
                la + 0.02,
                lb - 0.02,
                min(p, p + d * go) + 0.01,
                max(p, p + d * go),
                z0 + j * rh - 0.04,
                z0 + j * rh,
                m["frame"],
            )
        for uu in (la, lb):
            st.beam((uu, vs, z0 - 0.12), (uu, ve, z1 - 0.12), m["frame"], 0.06, 0.25)
            st.beam((uu, vs, z0 + rh + 0.9), (uu, ve, z1 + 0.9), m["frame"], 0.045)
        ld = (0.0, v0) if d < 0 else (v1, v1 + 1.1)
        st.box(band[0], band[1], ld[0] + 0.01, ld[1], z1 - 0.08, z1, m["frame"])
        far = ld[0] + 0.03 if d < 0 else ld[1] - 0.03
        st.beam((band[0], far, z1 + GUARD), (band[1], far, z1 + GUARD), m["frame"], 0.045)
        uo = band[0] + 0.03 if side < 0 else band[1] - 0.03
        st.beam((uo, ld[0], z1 + 1.05), (uo, ld[1], z1 + 1.05), m["frame"], 0.045)
    for v in (0.6, v0 - 0.05, v1 + 0.05, v1 + 1.05):
        for u in band:
            st.column(
                u, v, (flights - (v > v1)) * r * rh - 0.05, m["frame"], m["footing"], 0.12, 0.4
            )
    return [bx.finish(), st.finish()]


def bleacher(
    name,
    at,
    angle,
    length,
    depth,
    rows,
    *,
    rise=0.3,
    first_row=0.45,
    back_height=None,
    colours=None,
    unverified=True,
):
    """Low bleacher section standing on the ground (first row 0.45 m up), with red end and back
    panels. Inferred: `first_row` is the row-1 seat height; foot planks 0.43 m below each seat (row
    1 has none, feet on the ground); A-frames on a sill about every 2.4 m; back panel 1.07 m above
    the top seat; no red risers (DSC05256)."""
    m, place, tag = materials(colours), kit.placer(at, angle), "_UNVERIFIED" if unverified else ""
    fence = GUARD if back_height is None else back_height
    t = (depth - 0.1) / rows
    pl, fr, pn = (Local(f"{name}_{p}{tag}", place, angle) for p in ("planks", "frame", "panels"))
    s = [first_row + i * rise for i in range(rows)]
    nf = max(1, round(length / 2.4))
    us = [0.15 + (length - 0.3) * k / nf for k in range(nf + 1)]

    def raker_top(v):  # through the foot-plank bottoms, 2 cm into them
        return first_row - 0.46 + (v - 0.17) * rise / t

    for i in range(rows):
        a, b = i * t, i * t + t - 0.02
        if s[i] - 0.43 > 0.1:
            pl.box(0, length, a + 0.02, b - 0.33, s[i] - 0.48, s[i] - 0.43, m["plank"])
        pl.box(0, length, b - 0.3, b, s[i] - 0.05, s[i], m["plank"])
        for u in us:
            fr.beam(
                (u, b - 0.15, raker_top(b - 0.15) - 0.05),
                (u, b - 0.15, s[i] - 0.03),
                m["frame"],
                0.05,
            )
    vt = depth - 0.2
    vr = max(0.1, 0.17 + (0.62 - first_row) * t / rise)  # the raker meets the sill here
    for u in us:
        fr.beam((u, 0.05, 0.07), (u, vt, 0.07), m["frame"], 0.1)  # sill, 2 cm above grade
        fr.beam(
            (u, vr, raker_top(vr) - 0.07), (u, vt, raker_top(vt) - 0.07), m["frame"], 0.06, 0.15
        )
        for v in (depth / 2, vt - 0.05):
            fr.beam((u, v, 0.08), (u, v, raker_top(v) - 0.05), m["frame"], 0.07)
        fr.beam((u, vr + 0.3, 0.1), (u, depth / 2, raker_top(depth / 2) - 0.2), m["frame"], 0.05)
    top = s[-1] + fence
    pn.box(0, length, depth - 0.06, depth - 0.04, 0.05, top, m["panel"])
    for u, du in ((-0.04, 0.02), (length + 0.02, 0.02)):
        pn.plate(
            [u, (0.0, 0.05), (depth - 0.04, 0.05), (depth - 0.04, top), (0.0, first_row + 0.45)],
            du,
            m["panel"],
        )
    return [pl.finish(), fr.finish(), pn.finish()]


def tris(ob):
    ob.data.calc_loop_triangles()
    return len(ob.data.loop_triangles)


def demo():
    """Build the west stand, press box and one east bleacher on a ground plane; print triangle
    counts and render check pictures to /workspace/build/sw/preview/."""
    global kit
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import kit

    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    g = kit.Builder("SW_demo_ground")
    g.faces(
        [(-60, -30, 0), (120, -30, 0), (120, 120, 0), (-60, 120, 0)],
        [(0, 1, 2, 3)],
        kit.mat("lawn", "demo", kit.srgb("#5d7a45")),
    )
    g.finish()
    rows, fh, rise = 25, 1.2, 0.25
    west = grandstand(
        "SW_Sprague_west_stand", (0, 0, 0), 90, 90, 18, rows, first_row_height=fh, rise=rise
    )
    top = fh + (rows - 1) * rise
    place = kit.placer((0, 0, 0), 90)
    box = press_box(
        "SW_Sprague_press_box",
        place(45 - 4.6, 18.3),
        90,
        9.2,
        3.2,
        3.0,
        floor_z=top + 0.5,
        lettering="MSU",
    )
    east = bleacher("SW_Sprague_east_bleacher_1", (64, 54, 0), 270, 18, 7.6, 10)
    for label, group in (("west stand", west), ("press box", box), ("east bleacher", east)):
        for ob in group:
            print(f"{ob.name:48s} {tris(ob):7d} tris, materials {len(ob.data.materials)}")
        print(f"{label:48s} {sum(tris(o) for o in group):7d} tris total")
    out = "/workspace/build/sw/preview"
    os.makedirs(out, exist_ok=True)
    views = [
        ("stand_front", place(45, 9, 4), 85, 110, 18),
        ("stand_back", place(40, 12, 5), 55, 290, 18),
        ("stand_aisle", place(25.4, 3, h_at(3, fh, rise)), 9, 60, 22),
        ("stand_pressbox", place(43, 19, 7), 22, 245, 15),
        ("east_bleacher", (68, 45, 1.5), 22, 250, 20),
    ]
    for fname, target, dist, az, el in views:
        kit.preview(f"{out}/{fname}.png", target, distance=dist, azimuth=az, elevation=el)


def h_at(v, fh, rise, walk=1.5, t=0.66):
    """Rough walking height at depth v (for aiming the demo camera)."""
    return fh + max(0.0, v - walk) * rise / t


if __name__ == "__main__":
    demo()
