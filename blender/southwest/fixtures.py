"""Outdoor fixtures for the southwest build: Sprague Field and Montclair Heights station.

Every builder makes ONE object through `kit.Builder` (one material slot per material) and
returns it. `at` is the base point on the ground (model frame: +X east, +Y north, +Z up, metres);
`angle` is degrees anticlockwise from east, the way the fixture faces or runs. Local frame used
below: u along `angle`, v to its left, w up (see `kit.placer`). Touching parts intersect or stand
2 cm apart, never coplanar; parts that meet the ground go 5 cm into it.

Sizes from standards are named in each docstring. Everything else is estimated from the reference
photographs in refs/sw (see meta.txt there), so those objects default to `unverified=True`.

Demo row and previews:
    blender -b --factory-startup --python blender/southwest/fixtures.py
"""

import math
import os
import sys

from mathutils import Matrix, Vector

try:
    import kit
except ImportError:  # executed as a script: demo() puts this folder on sys.path first
    kit = None

PREVIEW_DIR = "/workspace/build/sw/preview"


def _name(name, unverified):
    return f"{name}_UNVERIFIED" if unverified else name


def _m(key):
    """The fixture materials (linear RGB from sRGB hex), made on first use."""
    k, s = kit.mat, kit.srgb
    table = {
        "galv": lambda: k("metal", "galvanised", s("#9ca0a4"), rough=0.45, metal=0.8),
        "housing": lambda: k("metal", "flood_housing", s("#3a3c3f"), rough=0.5, metal=0.5),
        "flood_lens": lambda: k("glass", "flood_lens", s("#e4e8ea"), rough=0.1),
        "footing": lambda: k("concrete", "footing", s("#a9a59d")),
        "yellow": lambda: k("paint", "goal_yellow", s("#f2c81e"), rough=0.4),
        "pad": lambda: k("rubber", "goal_pad", s("#c9cbcc")),
        "board": lambda: k("metal", "board_black", s("#1c1d1f"), rough=0.6),
        "face": lambda: k("sign", "scoreboard_face", s("#101113"), rough=0.3),
        "red": lambda: k("paint", "msu_red", s("#c8102e"), rough=0.5),
        "white_alu": lambda: k("metal", "bench_white", s("#e8e9e9"), rough=0.45, metal=0.3),
        "black": lambda: k("metal", "black_steel", s("#1e1f21"), rough=0.55, metal=0.4),
        "grey": lambda: k("metal", "gate_grey", s("#a6a9ac"), rough=0.5, metal=0.6),
        "xbuck": lambda: k("sign", "crossbuck_white", s("#f2f2ef"), rough=0.4),
        "flasher": lambda: k("glass", "flasher_red", s("#b3160f"), rough=0.2),
        "arm_red": lambda: k("paint", "arm_red", s("#c4161c"), rough=0.4),
        "arm_white": lambda: k("paint", "arm_white", s("#f2f2f0"), rough=0.4),
        "weight": lambda: k("metal", "counterweight", s("#56595c"), rough=0.6, metal=0.5),
        "lamp": lambda: k("metal", "lamp_dark", s("#2a2a2c"), rough=0.5, metal=0.5),
        "lamp_lens": lambda: k("glass", "lamp_lens", s("#d8dcdf"), rough=0.15),
        "station": lambda: k("sign", "station_black", s("#18191b"), rough=0.4),
        "picket": lambda: k("metal", "picket_black", s("#1e1f21"), rough=0.55, alpha=0.5),
        "tvm_blue": lambda: k("paint", "tvm_blue", s("#1f4e9c"), rough=0.4),
        "tvm_orange": lambda: k("paint", "tvm_orange", s("#ef7d1f"), rough=0.4),
        "screen": lambda: k("glass", "tvm_screen", s("#0c1014"), rough=0.1),
        "timber": lambda: k("wood", "platform_timber", s("#8b7a63")),
        "edge": lambda: k("paint", "edge_yellow", s("#f5c518"), rough=0.5),
        "pole": lambda: k("wood", "pole_creosote", s("#5a4632")),
        "insulator": lambda: k("plastic", "insulator", s("#7d847f"), rough=0.3),
        "net": lambda: k("metal", "netting_black", s("#151617"), rough=0.8, alpha=0.22),
    }
    return table[key]()


FENCE_RGB = {"black": "#1b1c1e", "galvanised": "#9ea2a6", "green": "#2e4a35"}


def _sweep(b, pts, r, side, material, sides=8):
    """Round tube along a plane polyline `pts`; `side` is the plane normal. Mitred bends, caps."""
    side = Vector(side).normalized()
    pts = [Vector(p) for p in pts]
    n, verts = len(pts), []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        nn = side.cross(t).normalized()
        s = 1.0
        if 0 < i < n - 1:
            a, c = (p - pts[i - 1]).normalized(), (pts[i + 1] - p).normalized()
            s = 1 / max(0.5, math.cos(a.angle(c) / 2))
        for k in range(sides):
            ang = 2 * math.pi * k / sides
            verts.append(p + side * (r * math.cos(ang)) + nn * (r * s * math.sin(ang)))
    f = [
        (
            i * sides + k,
            i * sides + (k + 1) % sides,
            (i + 1) * sides + (k + 1) % sides,
            (i + 1) * sides + k,
        )
        for i in range(n - 1)
        for k in range(sides)
    ]
    f += [tuple(range(sides - 1, -1, -1)), tuple(range((n - 1) * sides, n * sides))]
    b.faces(verts, f, material, smooth=True)


def _strip(b, pts, width, depth, materials):
    """Rectangular member through `pts`, each run in the next of `materials` (stripes); end caps."""
    pts = [Vector(p) for p in pts]
    for i in range(len(pts) - 1):
        d = (pts[i + 1] - pts[i]).normalized()
        x = d.cross(Vector((0, 0, 1)))
        x = x.normalized() if x.length > 1e-6 else Vector((1, 0, 0))
        y = d.cross(x)
        v = [
            p + x * sx * width / 2 + y * sy * depth / 2
            for p in (pts[i], pts[i + 1])
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
        ]
        f = [(k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k) for k in range(4)]
        f += [(3, 2, 1, 0)] if i == 0 else []
        f += [(4, 5, 6, 7)] if i == len(pts) - 2 else []
        b.faces(v, f, materials[i % len(materials)])


def _hood(b, place, u0, u1, cv, cw, r, material, t=0.015, segs=4):
    """Half-round visor over a lens: a thick arc in the v-w plane run from u0 to u1."""
    arc = [math.pi * k / segs for k in range(segs + 1)]
    prof = [(cv + (r + t) * math.cos(a), cw + (r + t) * math.sin(a)) for a in arc]
    prof += [(cv + r * math.cos(a), cw + r * math.sin(a)) for a in reversed(arc)]
    m = len(prof)
    v = [place(u, pv, pw) for u in (u0, u1) for pv, pw in prof]
    f = [(i, (i + 1) % m, m + (i + 1) % m, m + i) for i in range(m)]
    for o in (0, m):
        f += [(o + k, o + k + 1, o + m - 2 - k, o + m - 1 - k) for k in range(segs)]
    b.faces(v, f, material)


def _resample(path, spacing):
    """Points every ~`spacing` metres (evenly) along an open polyline, ends included."""
    pts = [Vector((p[0], p[1])) for p in path]
    seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]
    total = sum(seg)
    n = max(1, math.ceil(total / spacing - 1e-6))
    out, i, acc = [], 0, 0.0
    for k in range(n + 1):
        s = total * k / n
        while i < len(seg) - 1 and acc + seg[i] < s:
            acc += seg[i]
            i += 1
        t = 0.0 if seg[i] == 0 else min(1.0, (s - acc) / seg[i])
        out.append(pts[i].lerp(pts[i + 1], t))
    return out


def _panel(b, p0, p1, z0a, z1a, z0b, z1b, material):
    """One vertical quad from p0 (z0a..z1a) to p1 (z0b..z1b)."""
    b.faces(
        [(p0.x, p0.y, z0a), (p1.x, p1.y, z0b), (p1.x, p1.y, z1b), (p0.x, p0.y, z1a)],
        [(0, 1, 2, 3)],
        material,
    )


def _post(b, x, y, z0, z1, size, heading, material):
    """Square vertical post without a bottom face (its foot is always buried in something)."""
    c, sn, r = math.cos(math.radians(heading)), math.sin(math.radians(heading)), size / 2
    xy = [
        (x + (cu * c - cv * sn) * r, y + (cu * sn + cv * c) * r)
        for cu, cv in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    v = [(px, py, z) for z in (z0, z1) for px, py in xy]
    b.faces(v, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)], material)


def _railing(b, pts, zf, h=1.07, step=2.0):
    """Black steel railing along a polyline: square posts, a top rail and see-through picket infill.
    `zf(x, y)` is the base height. Rails stop 1 cm inside the posts so nothing is coplanar."""
    pts = [Vector((p[0], p[1])) for p in pts]
    posts, heads = [], []
    for a, c in zip(pts, pts[1:], strict=False):
        n = max(1, math.ceil((c - a).length / step - 1e-6))
        heads += [math.degrees(math.atan2(c.y - a.y, c.x - a.x))] * n
        posts += [a.lerp(c, k / n) for k in range(n)]
    posts.append(pts[-1])
    heads.append(heads[-1])
    blk, pk = _m("black"), _m("picket")
    for p, hd in zip(posts, heads, strict=True):
        z = zf(p.x, p.y)
        _post(b, p.x, p.y, z - 0.02, z + h, 0.07, hd, blk)
    for q0, q1 in zip(posts, posts[1:], strict=False):
        d = (q1 - q0).normalized()
        s0, s1 = q0 + d * 0.025, q1 - d * 0.025
        z0, z1 = zf(s0.x, s0.y), zf(s1.x, s1.y)
        b.beam((s0.x, s0.y, z0 + h - 0.03), (s1.x, s1.y, z1 + h - 0.03), 0.04, 0.04, blk)
        _panel(b, s0, s1, z0 + 0.08, z0 + h - 0.04, z1 + 0.08, z1 + h - 0.04, pk)


# --------------------------------------------------------------------------- Sprague Field


def light_pole(name, at, angle, height=24.0, *, banks=2, per_bank=6, unverified=True):
    """Sports flood light. Estimated from the 2025 drone photos: tapered galvanised pole (0.28 m to
    0.14 m radius) on a concrete pier, `banks` cross arms near the top carrying `per_bank` round LED
    flood heads (0.6 m across, 0.75 m apart) facing `angle`, aimed 25 degrees down. `height` is the
    pole top; real heights are not measured."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    galv, hous, lens = _m("galv"), _m("housing"), _m("flood_lens")
    b.tube(P(0, 0, -0.1), P(0, 0, 0.6), 0.45, _m("footing"))
    b.tube(P(0, 0, 0.55), P(0, 0, height), 0.28, galv, radius1=0.14)
    b.box(P(-0.3, 0, 1.5), (0.25, 0.4, 0.6), galv, angle=angle)  # electrical cabinet
    tilt = math.radians(25)
    d = Vector((math.cos(tilt), 0, -math.sin(tilt)))
    span = per_bank * 0.75
    for i in range(banks):
        wb = height - 0.5 - 1.0 * i
        b.beam(P(0, 0, wb), P(0.55, 0, wb), 0.15, 0.15, galv)
        b.beam(P(0.55, -span / 2, wb), P(0.55, span / 2, wb), 0.12, 0.12, galv)
        for j in range(per_bank):
            v = -span / 2 + 0.375 + 0.75 * j
            c0 = Vector((0.58, v, wb))
            b.tube(P(*c0), P(*(c0 + d * 0.4)), 0.3, hous)
            b.tube(P(*(c0 + d * 0.38)), P(*(c0 + d * 0.415)), 0.26, lens)
            b.beam(P(0.5, v, wb - 0.06), P(*(c0 + d * 0.1)), 0.08, 0.08, galv)  # knuckle
    return b.finish()


def goalpost(name, at, angle, *, unverified=False):
    """Single-post (gooseneck) football goal, NCAA rule 1-2-4: crossbar top 3.05 m (10 ft) above the
    ground, uprights 5.64 m (18 ft 6 in) apart inside, upright tops 9.1 m (30 ft) above ground, all
    yellow. `at` is the post base; the gooseneck reaches 1.83 m (6 ft) toward the field (`angle`),
    so put `at` 1.83 m behind the end line. Pipe sizes (post 0.17 m, crossbar and uprights
    0.10 m) and the grey base pad are estimates."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    yel = _m("yellow")
    side = Vector(P(0, 1, 0)) - Vector(P(0, 0, 0))
    neck = [(0, -0.05), (0, 2.3), (0.22, 2.78), (0.75, 3.0), (1.83, 3.0)]
    _sweep(b, [P(u, 0, w) for u, w in neck], 0.085, side, yel)
    half = 5.64 / 2 + 0.051
    b.tube(P(1.83, -half, 3.0), P(1.83, half, 3.0), 0.05, yel)
    for s in (-1, 1):
        b.tube(P(1.83, s * half, 2.97), P(1.83, s * half, 9.1), 0.051, yel)
    b.tube(P(0, 0, -0.02), P(0, 0, 1.8), 0.2, _m("pad"))
    return b.finish()


def scoreboard(name, at, angle, width=6.0, height=3.0, *, clear=3.0, unverified=True):
    """Dark scoreboard (0.4 m deep cabinet, red top band, black face) on two square steel posts,
    face toward `angle`, bottom `clear` above ground. All sizes estimated from drone photo 0151."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    top = clear + height
    for s in (-1, 1):
        b.box(
            P(-0.25, s * width * 0.3, (top - 0.15) / 2),
            (0.25, 0.25, top - 0.05),
            _m("board"),
            angle=angle,
        )
        b.box(P(-0.25, s * width * 0.3, 0.1), (0.7, 0.7, 0.3), _m("footing"), angle=angle)
    b.box(P(0, 0, clear + height / 2), (0.4, width, height), _m("board"), angle=angle)
    b.box(P(0, 0, top - 0.155), (0.44, width + 0.04, 0.35), _m("red"), angle=angle)
    fh = height - 0.53
    b.box(P(0.2, 0, clear + 0.15 + fh / 2), (0.04, width - 0.2, fh), _m("face"), angle=angle)
    return b.finish()


def team_bench(name, at, angle, length=6.0, *, unverified=True):
    """White aluminium team bench without a back: two seat planks at 0.45 m on A-frame legs about
    every 2 m, and a foot plank. `angle` = the way the seated players face. Estimated from
    photo DSC05256."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    alu = _m("white_alu")
    for u in (-0.08, 0.08):
        b.box(P(u, 0, 0.45), (0.14, length, 0.04), alu, angle=angle)
    b.box(P(0.18, 0, 0.12), (0.14, length - 0.1, 0.03), alu, angle=angle)
    n = max(2, math.ceil(length / 2.0) + 1)
    for i in range(n):
        v = -length / 2 + 0.15 + (length - 0.3) * i / (n - 1)
        b.beam(P(0, v, 0.44), P(0.24, v, -0.05), 0.05, 0.05, alu)
        b.beam(P(0, v, 0.44), P(-0.24, v, -0.05), 0.05, 0.05, alu)
        b.beam(P(-0.18, v, 0.42), P(0.18, v, 0.42), 0.05, 0.04, alu)
    return b.finish()


def fence(
    name,
    path,
    height=1.8,
    *,
    ground=None,
    colour="black",
    mesh=True,
    post_spacing=3.0,
    unverified=True,
):
    """Chain-link fence along a dense polyline [(x, y), ...]. Standard line posts 60 mm (2-3/8 in
    nominal), top rail 42 mm (1-5/8 in); the fabric is one see-through panel per span
    (metal 'chainlink_<colour>', alpha 0.45). `ground(x, y)` gives the ground height (default 0).
    Posts are spaced evenly at no more than `post_spacing`."""
    g = ground or (lambda x, y: 0.0)
    b = kit.Builder(_name(name, unverified))
    rgb = kit.srgb(FENCE_RGB.get(colour, FENCE_RGB["black"]))
    post = kit.mat("metal", f"fence_{colour}", rgb, rough=0.5, metal=0.6)
    fab = kit.mat("metal", f"chainlink_{colour}", rgb, rough=0.5, metal=0.6, alpha=0.45)
    pts = _resample(path, post_spacing)
    zs = [g(p.x, p.y) for p in pts]
    for p, z in zip(pts, zs, strict=True):
        b.tube((p.x, p.y, z - 0.05), (p.x, p.y, z + height + 0.04), 0.03, post, sides=6)
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        b.tube(
            (p0.x, p0.y, zs[i] + height - 0.02),
            (p1.x, p1.y, zs[i + 1] + height - 0.02),
            0.021,
            post,
            sides=6,
            caps=False,
        )
        if mesh:
            _panel(
                b,
                p0,
                p1,
                zs[i] + 0.03,
                zs[i] + height - 0.04,
                zs[i + 1] + 0.03,
                zs[i + 1] + height - 0.04,
                fab,
            )
    return b.finish()


def net_poles(name, path, height=9.0, *, ground=None, spacing=9.0, unverified=True):
    """Ball-stop net: tall black poles (0.11 m, estimated) with a top cable and a see-through black
    net panel per span, from 0.2 m to the top. Height and spacing estimated from drone
    photo 0151."""
    g = ground or (lambda x, y: 0.0)
    b = kit.Builder(_name(name, unverified))
    blk, net = _m("black"), _m("net")
    pts = _resample(path, spacing)
    zs = [g(p.x, p.y) for p in pts]
    for p, z in zip(pts, zs, strict=True):
        b.tube((p.x, p.y, z - 0.05), (p.x, p.y, z + height), 0.055, blk, sides=6)
    for i in range(len(pts) - 1):
        p0, p1 = pts[i], pts[i + 1]
        b.beam(
            (p0.x, p0.y, zs[i] + height - 0.12),
            (p1.x, p1.y, zs[i + 1] + height - 0.12),
            0.02,
            0.02,
            blk,
        )
        _panel(
            b,
            p0,
            p1,
            zs[i] + 0.2,
            zs[i] + height - 0.14,
            zs[i + 1] + 0.2,
            zs[i + 1] + height - 0.14,
            net,
        )
    return b.finish()


# ------------------------------------------------------------------ Montclair Heights station


def crossing_gate(name, at, angle, arm=7.0, *, unverified=True):
    """US grade crossing gate (MUTCD part 8C): grey 0.11 m mast on a concrete base; crossbuck of
    two white 1.22 m x 0.23 m blades at 90 degrees, centred 3.9 m up (no lettering); two
    back-to-back pairs of red flashers, 0.3 m (12 in) lenses on 0.6 m black round backgrounds with
    hoods, centred 3.0 m up and 0.84 m apart; a bell on top; a gate mechanism with an `arm`-long
    red/white arm in 0.4 m (16 in) stripes, drawn raised at 80 degrees, and its counterweight.
    `angle` = the way the front flashers face (toward traffic); the arm lowers to the right of
    the front face (local -v). Mast height, mechanism and counterweight sizes are estimates from
    subwaynut photo 20."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    grey, blk = _m("grey"), _m("black")
    b.box(P(0, 0, -0.05), (0.8, 0.8, 0.3), _m("footing"), angle=angle)
    b.tube(P(0, 0, 0.08), P(0, 0, 4.62), 0.057, grey)
    b.tube(P(0, 0, 4.6), P(0, 0, 4.78), 0.13, blk, radius1=0.05)  # bell
    for uc, tw in ((0.055, 45), (0.075, -45)):
        b.box(
            P(uc, 0, 3.9),
            (0.012, 1.22, 0.23),
            _m("xbuck"),
            angle=angle,
            tilt=Matrix.Rotation(math.radians(tw), 4, "X"),
        )
    b.beam(P(0, -0.8, 3.0), P(0, 0.8, 3.0), 0.13, 0.1, grey)
    for s in (1, -1):
        for v in (-0.42, 0.42):
            b.tube(P(s * 0.06, v, 3.0), P(s * 0.09, v, 3.0), 0.3, blk)
            b.tube(P(s * 0.08, v, 3.0), P(s * 0.15, v, 3.0), 0.15, _m("flasher"))
            _hood(b, P, s * 0.09, s * 0.32, v, 3.0, 0.17, blk)
    n = round(arm / 0.4)
    if n < 2:  # a flasher mast without a gate arm
        return b.finish()
    # gate mechanism on the road side of the mast; the arm pivots clear of the flashers
    b.box(P(0.15, -0.25, 1.3), (0.45, 0.45, 0.7), grey, angle=angle)
    b.beam(P(0.15, -0.4, 1.4), P(0.15, -0.95, 1.4), 0.2, 0.2, grey)
    b.tube(P(0.0, -0.85, 1.4), P(0.52, -0.85, 1.4), 0.04, grey)
    up = math.radians(80)
    d = Vector((0, -math.cos(up), math.sin(up)))
    piv = Vector((0.45, -0.85, 1.4))
    _strip(
        b,
        [P(*(piv + d * (0.2 + arm * k / n))) for k in range(n + 1)],
        0.09,
        0.1,
        [_m("arm_red"), _m("arm_white")],
    )
    b.beam(P(*(piv - d * 0.95)), P(*(piv + d * 0.3)), 0.06, 0.12, grey)
    b.box(P(*(piv - d * 0.8)), (0.22, 0.32, 0.3), _m("weight"), angle=angle)
    return b.finish()


def lot_lamp(name, at, angle, height=7.5, *, heads=1, unverified=True):
    """Parking-lot lamp: dark 0.15 m square pole on a round concrete footing, with 1 or 2 flat
    'shoebox' heads (0.75 x 0.45 x 0.14 m) on short arms, back to back, the first facing `angle`.
    Sizes estimated from the station photos."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    dark = _m("lamp")
    b.tube(P(0, 0, -0.05), P(0, 0, 0.6), 0.3, _m("footing"))
    b.box(P(0, 0, (height + 0.55) / 2), (0.15, 0.15, height - 0.55), dark, angle=angle)
    for s in (1, -1)[: max(1, min(2, heads))]:
        b.beam(P(0, 0, height - 0.07), P(s * 0.4, 0, height - 0.07), 0.08, 0.08, dark)
        b.box(P(s * 0.55, 0, height - 0.07), (0.75, 0.45, 0.14), dark, angle=angle)
        b.box(P(s * 0.55, 0, height - 0.145), (0.6, 0.35, 0.03), _m("lamp_lens"), angle=angle)
    return b.finish()


def station_sign(name, at, angle, width=1.8, height=0.9, *, clear=1.6, unverified=True):
    """Black station name panel (0.12 m deep, no lettering) on two black posts that run up inside
    it; face toward `angle`, bottom `clear` above ground. Sizes estimated from the station
    photos."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    b.box(P(0, 0, clear + height / 2), (0.12, width, height), _m("station"), angle=angle)
    for s in (-1, 1):
        top = clear + height - 0.05
        b.box(
            P(0, s * (width / 2 - 0.25), (top - 0.05) / 2),
            (0.08, 0.08, top + 0.05),
            _m("black"),
            angle=angle,
        )
    return b.finish()


def bike_rack(name, at, angle, hoops=4, *, unverified=True):
    """Row of black inverted-U hoops (60 mm pipe, 0.45 m wide, 0.93 m tall), 0.9 m apart along
    `angle`, each hoop across the row. Estimated from the Commons photo of the station racks."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    side = Vector(P(1, 0, 0)) - Vector(P(0, 0, 0))
    for i in range(hoops):
        u = 0.9 * (i - (hoops - 1) / 2)
        arc = [
            (0.225 * math.cos(math.pi * k / 6), 0.675 + 0.225 * math.sin(math.pi * k / 6))
            for k in range(6, -1, -1)
        ]
        pts = [(-0.225, -0.05), *arc, (0.225, -0.05)]
        _sweep(b, [P(u, v, w) for v, w in pts], 0.03, side, _m("black"), sides=6)
    return b.finish()


def platform_bench(name, at, angle, length=1.8, *, unverified=True):
    """Black metal platform bench with a back and end arms: three seat slats at 0.45 m, two back
    slats leaning 10 degrees, steel end frames. Faces `angle`. Estimated from subwaynut photo 16."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    blk = _m("black")
    for u in (-0.14, 0.0, 0.14):
        b.box(P(u, 0, 0.45), (0.12, length, 0.03), blk, angle=angle)
    lean = Matrix.Rotation(math.radians(-10), 4, "Y")
    for w in (0.62, 0.8):
        b.box(P(-0.27 - (w - 0.45) * 0.18, 0, w), (0.03, length, 0.12), blk, angle=angle, tilt=lean)
    for v in (-(length / 2 - 0.06), length / 2 - 0.06):
        b.beam(P(0.2, v, -0.05), P(0.2, v, 0.66), 0.04, 0.04, blk)
        b.beam(P(-0.22, v, -0.05), P(-0.36, v, 0.9), 0.04, 0.04, blk)
        b.beam(P(0.22, v, 0.43), P(-0.27, v, 0.43), 0.04, 0.03, blk)
        b.beam(P(0.24, v, 0.65), P(-0.31, v, 0.65), 0.05, 0.03, blk)
    return b.finish()


def ticket_machine(name, at, angle, *, unverified=True):
    """NJ Transit ticket vending machine: blue cabinet 0.9 m wide, 0.7 m deep, 1.96 m high with an
    orange front panel, a dark screen, a keypad shelf and an overhanging top, on a low plinth;
    front toward `angle`. Estimated from the Commons station photos."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    b.box(P(0, 0, 0.035), (0.6, 0.8, 0.17), _m("black"), angle=angle)
    b.box(P(0, 0, 1.0), (0.7, 0.9, 1.8), _m("tvm_blue"), angle=angle)
    b.box(P(0.36, 0, 1.25), (0.04, 0.7, 0.9), _m("tvm_orange"), angle=angle)
    b.box(P(0.385, 0, 1.4), (0.03, 0.4, 0.3), _m("screen"), angle=angle)
    b.box(P(0.42, 0, 0.98), (0.16, 0.6, 0.04), _m("black"), angle=angle)
    b.box(P(0.05, 0, 1.92), (0.8, 0.96, 0.08), _m("tvm_blue"), angle=angle)
    return b.finish()


def _inset(ring, d):
    """Mitred inward offset of an anticlockwise ring."""
    out, n = [], len(ring)
    for i in range(n):
        a, p, c = Vector(ring[i - 1]), Vector(ring[i]), Vector(ring[(i + 1) % n])
        e1, e2 = (p - a).normalized(), (c - p).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        m = (n1 + n2).normalized()
        out.append(p + m * (d / max(0.3, m.dot(n1))))
    return out


def mini_high_platform(name, ring, top_z, ground_z, *, ramp=None, unverified=True):
    """Wooden mini-high level boarding platform. `ring` [(x, y), ...] outlines the deck; its first
    edge (ring[0] to ring[1]) is the track edge, which gets a yellow strip on the deck and a yellow
    fascia. Timber deck 0.1 m thick at `top_z` over a plank skirt and 0.15 m corner posts; black
    railings (1.07 m, the ADA/IBC guard height) on the other edges; optional `ramp` [(x, y) top,
    (x, y) foot]: a 1.2 m wide timber ramp with railings both sides, leaving a gap in the deck
    railing. Plank and post sizes estimated from subwaynut photo 7."""
    b = kit.Builder(_name(name, unverified))
    ring = [Vector((p[0], p[1])) for p in ring]
    area = sum(a.x * c.y - c.x * a.y for a, c in zip(ring, ring[1:] + ring[:1], strict=True))
    if area < 0:
        ring = ring[1::-1] + ring[:1:-1]
    wood = _m("timber")
    b.prism([tuple(p) for p in ring], top_z - 0.1, top_z, wood, top=True, bottom=True)
    b.prism([tuple(p) for p in _inset(ring, 0.03)], ground_z - 0.05, top_z - 0.05, wood, top=False)
    for p in ring:
        _post(b, p.x, p.y, ground_z - 0.05, top_z - 0.05, 0.15, 0, wood)
    a, c = ring[0], ring[1]
    e = (c - a).normalized()
    nrm = Vector((e.y, -e.x))  # outward
    hd = math.degrees(math.atan2(e.y, e.x))
    mid, ln = (a + c) / 2, (c - a).length
    for off, size, z in (
        (0.005, (ln, 0.03, 0.28), top_z - 0.16),
        (-0.17, (ln - 0.1, 0.3, 0.018), top_z + 0.0),
    ):
        q = mid + nrm * off
        b.box((q.x, q.y, z), size, _m("edge"), angle=hd)
    chain = [*_inset(ring, 0.06)[1:], _inset(ring, 0.06)[0]]
    chains = [chain]
    rw = 1.2
    if ramp:
        r0, r1 = Vector(ramp[0]), Vector(ramp[1])
        best = None
        for i in range(len(chain) - 1):
            s0, s1 = chain[i], chain[i + 1]
            t = max(0.0, min(1.0, (r0 - s0).dot(s1 - s0) / (s1 - s0).length_squared))
            dist = (s0.lerp(s1, t) - r0).length
            if best is None or dist < best[0]:
                best = (dist, i, t * (s1 - s0).length)
        _, i, t = best
        s0, s1 = chain[i], chain[i + 1]
        dd = (s1 - s0).normalized()
        g0 = s0 + dd * max(0.0, t - rw / 2 - 0.05)
        g1 = s0 + dd * min((s1 - s0).length, t + rw / 2 + 0.05)
        chains = [chain[: i + 1] + [g0], [g1] + chain[i + 1 :]]
        rd = (r1 - r0).normalized()
        rn = Vector((-rd.y, rd.x))
        ln = (r1 - r0).length

        def rz(x, y, r0=r0, rd=rd, ln=ln):
            t = max(0.0, min(1.0, (Vector((x, y)) - r0).dot(rd) / ln))
            return top_z - 0.01 + (ground_z + 0.01 - top_z + 0.01) * t

        q0, q1 = r0 - rd * 0.05, r1
        b.beam((q0.x, q0.y, top_z - 0.07), (q1.x, q1.y, ground_z - 0.05), rw, 0.12, wood)
        for s in (-1, 1):
            o = rn * s * (rw / 2 - 0.06)
            _railing(b, [r0 + rd * 0.12 + o, r1 - rd * 0.05 + o], rz, step=3.5)
    for ch in chains:
        ch = [p for k, p in enumerate(ch) if k == 0 or (p - ch[k - 1]).length > 0.1]
        if len(ch) >= 2:
            _railing(b, ch, lambda x, y: top_z, step=2.5)
    return b.finish()


def utility_pole(name, at, angle, height=11.0, *, unverified=True):
    """Wooden utility pole (0.32 m butt, 0.22 m top, creosote brown) with one 2.4 m cross arm
    across the line (the line runs along `angle`), two braces and three insulators. Estimated
    (typical class 4 pole, 2.4 m arm); real heights not measured."""
    b, P = kit.Builder(_name(name, unverified)), kit.placer(at, angle)
    wood = _m("pole")
    b.tube(P(0, 0, -0.05), P(0, 0, height), 0.16, wood, radius1=0.11)
    wa = height - 0.5
    b.box(P(0.16, 0, wa), (0.09, 2.4, 0.11), wood, angle=angle)
    for s in (-1, 1):
        b.beam(P(0.15, 0, wa - 0.65), P(0.15, s * 0.65, wa - 0.04), 0.05, 0.02, _m("grey"))
    for v in (-1.05, -0.45, 1.05):
        b.tube(P(0.16, v, wa + 0.045), P(0.16, v, wa + 0.2), 0.045, _m("insulator"), sides=6)
    return b.finish()


# --------------------------------------------------------------------------- demo


def tris(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def demo():
    global kit
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import bpy
    import kit as _kit

    kit = _kit
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    g = kit.Builder("SW_demo_ground")
    g.box((60, 5, -0.05), (150, 50, 0.1), kit.mat("lawn", "demo_grass", kit.srgb("#6f8a55")))
    g.finish()
    s = -90  # most fixtures face south, toward the preview camera
    obs = [
        light_pole("SW_Light_pole_demo", (0, 0, 0), s),
        goalpost("SW_Goal_demo", (10, 0, 0), 90),
        scoreboard("SW_Scoreboard_demo", (20, 2, 0), s),
        team_bench("SW_Team_bench_demo", (29, -2, 0), s),
        fence("SW_Fence_demo", [(26 + 0.5 * k, 4 + 0.02 * (k - 10) ** 2) for k in range(21)]),
        net_poles("SW_Net_demo", [(38, 8), (52, 8)]),
        crossing_gate("SW_Crossing_gate_demo", (56, -3, 0), s),
        lot_lamp("SW_Lot_lamp_demo", (61, -2, 0), 0, heads=2),
        station_sign("SW_Station_sign_demo", (65, -2, 0), s),
        bike_rack("SW_Bike_rack_demo", (70, -3, 0), 0),
        platform_bench("SW_Platform_bench_demo", (74.5, -3, 0), s),
        ticket_machine("SW_TVM_demo", (77.5, -3, 0), s),
        mini_high_platform(
            "SW_Mini_high_demo",
            [(81, -4), (87, -4), (87, -1.5), (81, -1.5)],
            1.0,
            0.0,
            ramp=[(87, -2.75), (99, -2.75)],
        ),
        utility_pole("SW_Utility_pole_demo", (100, 0, 0), 0),
    ]
    for ob in obs:
        print(f"{ob.name:40s} {tris(ob):6d} tris  {[m.name for m in ob.data.materials]}")
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    views = [  # file, target, distance, azimuth, elevation
        ("fixtures_field.png", (11, 0, 11), 62, 205, 14),
        ("fixtures_crossing.png", (58.5, -3, 2.6), 15, 215, 8),
        ("fixtures_station.png", (84, -2, 1.5), 28, 205, 16),
    ]
    for fn, target, dist, az, el in views:
        kit.preview(
            os.path.join(PREVIEW_DIR, fn),
            target,
            distance=dist,
            azimuth=az,
            elevation=el,
            size=(1280, 720),
            samples=16,
        )


if __name__ == "__main__":
    demo()
