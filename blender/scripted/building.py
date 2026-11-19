"""Buildings from the plan's `buildings` parts: walls, a roof, windows, parking deck levels.

A part is an outline with a roof type and heights from the LiDAR (see README, "Buildings"). This is
massing with a facade rhythm, not a survey: outline and heights are measured, the window grid and
the colours are estimates, so every object made here is named `_UNVERIFIED`.
"""

import math

import geom
import kit
import massing

WALL_KIND = {"dorm": "brick", "hall": "brick", "plant": "brick", "deck": "concrete"}
PARAPET = {"deck": 1.1}  # height of the parapet above the roof deck; 0.4 for everything else
PROUD = 0.06  # how far windows and bands stand off the wall: enough not to flicker far away


BRICK_TONE = "#96543f"  # the viewer's brick texture, on average (sRGB)


def _wall_material(kind, colour):
    """Wall material for a facade colour. The viewer multiplies a material's colour into the
    texture of its kind, so a brick-red colour on the red brick texture comes out near black.
    A brick-coloured wall therefore gets the tint that turns the texture into that colour, and a
    wall of any other colour (buff, grey) is not brick in the viewer: it gets the plaster kind.
    """
    rgb = kit.srgb(colour)
    if kind == "brick":
        if rgb[0] < 3.0 * rgb[2]:  # not a red or brown: the brick texture cannot show it
            kind = "plaster"
        else:
            tone = kit.srgb(BRICK_TONE)
            tint = [c / t for c, t in zip(rgb, tone, strict=True)]
            rgb = tuple(min(1.0, v / max(1.0, max(tint))) for v in tint)
    return kit.mat(kind, "wall_" + colour[1:], rgb, 0.9)


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


def _flat_roof(b, ring, top, drop, cap, deck):
    """Parapet and roof deck of a flat roof: the deck lies `drop` below the parapet top."""
    n = len(ring)
    inner = geom.offset(ring, 0.3, True)
    if not 0 < geom.area(inner) < geom.area(ring):
        inner = list(ring)  # too narrow for a parapet: a plain cap
    v = (
        [(p[0], p[1], top) for p in ring]
        + [(p[0], p[1], top) for p in inner]
        + [(p[0], p[1], top - drop) for p in inner]
    )
    f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    # the parapet's inner face looks in over the roof deck
    f += [(2 * n + (i + 1) % n, 2 * n + i, n + i, n + (i + 1) % n) for i in range(n)]
    b.faces(v, f, cap)
    b.faces(v[2 * n :], [tuple(range(n))], deck)


def _windows(b, part, ring, wall_top, ground, glass):
    """Rows of windows on every wall long enough for a bay, counted down from the wall top."""
    w = part["windows"]
    floors = part.get("floors", 1)
    low = min(ground(*p) for p in ring)
    h = massing.storey(wall_top, low, floors)
    sill, tall, wide = w.get("sill", 0.9), w["height"], w["width"]
    for _i, a, _b, length, u, nrm in _edges(ring):
        for s in massing.bays(length, w["spacing"]):
            g = ground(a[0] + u[0] * s, a[1] + u[1] * s)
            for f in range(floors):
                z0 = wall_top - (f + 1) * h + sill
                if z0 < g + 0.4:
                    break  # this storey is below ground on this side
                _panel(
                    b, a, u, nrm, s - wide / 2, s + wide / 2, z0, min(z0 + tall, wall_top), glass
                )


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


def part(lay_part, name, ground):
    """One building part as an object. `ground(x, y)` gives the terrain height."""
    p = lay_part
    ring = geom.expand(p["ring"], True)
    if geom.area(ring) < 0:
        ring = ring[::-1]
    style = p.get("style", "shed")
    hexes = dict(wall=p.get("wall", "#b9b6ad"), trim=p.get("trim", "#d9d6cc"))
    hexes["roof"] = p.get("roof_colour", "#8f9194")
    wall = _wall_material(WALL_KIND.get(style, "plaster"), hexes["wall"])
    trim = kit.mat("concrete", "trim_" + hexes["trim"][1:], kit.srgb(hexes["trim"]), 0.8)
    kind = p.get("roof", "flat")
    tops, slopes, gables = massing.roof(ring, kind, p["top"], p.get("eave"), p.get("ridge_angle"))
    # walls go 0.6 m into the lowest ground round the part, or stand on another part's roof
    samples = [q[:2] for q in geom.resample(ring, 2.0, True)]
    base = p["base"] if "base" in p else min(ground(x, y) for x, y in samples) - 0.6
    b = kit.Builder(name)
    n = len(ring)
    v = [(q[0], q[1], base) for q in ring] + [
        (q[0], q[1], z) for q, z in zip(ring, tops, strict=True)
    ]
    b.faces(v, [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)], wall)
    for face in gables:
        b.faces(face, [tuple(range(len(face)))], wall)
    if kind == "flat":
        deck = kit.mat("concrete", "roof_" + hexes["roof"][1:], kit.srgb(hexes["roof"]), 0.85)
        _flat_roof(b, ring, p["top"], PARAPET.get(style, 0.4), trim, deck)
    else:
        sheet = kit.mat("metal", "roof_" + hexes["roof"][1:], kit.srgb(hexes["roof"]), 0.55, 0.2)
        for face in slopes:
            b.faces(face, [tuple(range(len(face)))], sheet)
    wall_top = min(tops) - (PARAPET.get(style, 0.4) if kind == "flat" else 0.0)

    def local(x, y):  # a part on a roof has that roof as its ground
        return p["base"] if "base" in p else ground(x, y)

    if style == "deck" and kind == "flat":
        void = kit.mat("paint", "deck_opening", kit.srgb("#1b1c1e"), 0.95)
        _deck_levels(b, p, ring, p["top"], local, wall, void)
    elif p.get("windows"):
        glass = kit.mat("glass", "window", kit.srgb("#2b3640"), 0.15)
        _windows(b, p, ring, wall_top, local, glass)
    return b.finish(recalc=False)  # every face here is wound by hand; panels are loose quads


def build(lay, terrain, name_of):
    """Every plan building that gives a roof height (`top`). Returns the objects."""
    out = []
    for p in lay["buildings"]:
        if "top" in p:
            out.append(part(p, name_of(p) + "_UNVERIFIED", terrain.at))
    return out
