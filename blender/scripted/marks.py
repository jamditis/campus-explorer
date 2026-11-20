"""Shapes of pavement markings as paint outlines: lane-use arrows, crosswalks, the box of a word.

Pure Python (no bpy), used by layout.py. Every shape is paint: paint.py draws it into the sheet of
the surface under it.
"""

import math

import geom

# Lane-use arrows, metres, from the FHWA Standard Highway Signs (metric edition, 2004), pavement
# markings sheets 10-8 (through and left) and 10-10 (through; left turn), read on their 100 mm grid.
# The 2003 MUTCD (Figure 3B-21) gives the through arrow as 2.9 m (9.5 ft) overall; the SHS sheet
# draws it 3.0 m, which is used here. Through: 0.3 m shaft, head 1.6 m long and 1.0 m wide, its
# barbs swept back 0.3 m along the shaft. Turn: the shaft bends through a quarter circle (outer
# radius 1.0 m, inner 0.7 m) into a 0.5 m arm; the head's tip is 1.7 m from the tail and 1.76 m to
# the side, its barbs 0.8 m beyond and 1.1 m short of the tip. Through-and-turn: the same turn on a
# through arrow 4.0 m long. Frame: u forward from the tail of the shaft, v to the left.
TURN_ARC_STEP = 7.5  # degrees per segment of the drawn quarter circles


def _through(length):
    return [
        (0.0, -0.15),
        (length - 1.3, -0.15),
        (length - 1.6, -0.5),
        (length, 0.0),
        (length - 1.6, 0.5),
        (length - 1.3, 0.15),
        (0.0, 0.15),
    ]


def _left_turn():
    n = round(90 / TURN_ARC_STEP)
    out = [(0.0, -0.15), (0.8, -0.15)]
    # outer edge: a quarter circle of 1.0 m about (0.8, 0.85), from the shaft's right edge to the
    # arm
    out += [
        (0.8 + math.sin(math.radians(a)), 0.85 - math.cos(math.radians(a)))
        for a in (90 * i / n for i in range(1, n + 1))
    ]
    out += [(1.8, 1.06), (2.5, 0.86), (1.7, 1.76), (0.6, 0.96), (1.3, 1.06), (1.3, 0.85)]
    # inner edge: a quarter circle of 0.7 m about (0.6, 0.85), back down to the shaft's left edge
    out += [
        (0.6 + 0.7 * math.sin(math.radians(a)), 0.85 - 0.7 * math.cos(math.radians(a)))
        for a in (90 * i / n for i in range(n - 1, -1, -1))
    ]
    return out + [(0.0, 0.15)]


def arrow_rings(shape):
    """Outlines of one arrow in its own frame, and its length (tail to the farthest point ahead)."""
    left = _left_turn()
    right = [(u, -v) for u, v in left]
    shapes = {
        "straight": ([_through(3.0)], 3.0),
        "left": ([left], 2.5),
        "right": ([right], 2.5),
        "straight_left": ([_through(4.0), left], 4.0),
        "straight_right": ([_through(4.0), right], 4.0),
    }
    if shape not in shapes:
        raise ValueError(f"unknown arrow shape {shape!r}; use one of {sorted(shapes)}")
    return shapes[shape]


def arrow(at, angle, shape, length=None):
    """An arrow pointing toward `angle` (degrees from east), `at` the middle of its length on the
    line of its shaft. `length` scales the whole standard shape to that length (the small arrows
    of a parking aisle). Returns model outlines."""
    rings, full = arrow_rings(shape)
    k = (length / full) if length else 1.0
    to_model = geom.frame(at, angle)[1]
    return [[to_model((u - full / 2) * k, v * k) for u, v in r] for r in rings]


def _rect(to_model, u0, u1, v0, v1):
    return [to_model(u0, v0), to_model(u1, v0), to_model(u1, v1), to_model(u0, v1)]


def crosswalk(line, width, style="continental", bar=0.6, spacing=1.2):
    """Outlines of a crosswalk whose centre line runs across the road along `line` (edge to edge).

    continental: bars `bar` wide at `spacing` centres, parallel to the traffic, `width` long,
    centred on the crossing; lines: two 0.3 m transverse lines whose outer edges are `width` apart;
    ladder: both.
    """
    (ax, ay), (bx, by) = line
    length = math.hypot(bx - ax, by - ay)
    to_model = geom.frame((ax, ay), math.degrees(math.atan2(by - ay, bx - ax)))[1]
    half = width / 2
    if style not in ("continental", "lines", "ladder"):
        raise ValueError(f"unknown crosswalk style {style!r}")
    out = []
    if style in ("continental", "ladder"):
        n = max(1, int((length - bar) / spacing + 1e-9) + 1)
        first = (length - (n - 1) * spacing) / 2
        for i in range(n):
            s = first + i * spacing
            out.append(_rect(to_model, s - bar / 2, s + bar / 2, -half, half))
    if style in ("lines", "ladder"):
        out.append(_rect(to_model, 0.0, length, -half, -half + 0.3))
        out.append(_rect(to_model, 0.0, length, half - 0.3, half))
    return out


# Pavement words: the SHS pavement alphabet (sheets 10-1 to 10-7) draws letters about a sixth as
# wide as they are tall; the gap between letters here is a guess.
LETTER, GAP = 0.17, 0.08


def word_width(text, height):
    """Default width of a pavement word `height` metres tall."""
    n = len(text)
    return height * (LETTER * n + GAP * max(0, n - 1))


def word_box(at, angle, height, width):
    """Outline of a word centred at `at`, read by someone facing `angle`: its letters run `height`
    along `angle` and the line of text `width` across it."""
    to_model = geom.frame(at, angle)[1]
    return _rect(to_model, -height / 2, height / 2, -width / 2, width / 2)
