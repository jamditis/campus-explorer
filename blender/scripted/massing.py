"""Pure geometry for building parts: roof shapes, window bays, storey heights. No bpy.

A part is an anticlockwise outline with a roof type. Every function here returns plain tuples, so
the shapes can be unit tested without Blender; building.py turns them into meshes.
"""

import math

import geom


def _mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def _pair(ring, ridge_angle=None):
    """For a four-corner outline, the index k of the edge the ridge runs parallel to: the edge
    nearest `ridge_angle` (degrees anticlockwise from east), or the longer pair when none is given.
    """
    e = [(ring[(i + 1) % 4][0] - ring[i][0], ring[(i + 1) % 4][1] - ring[i][1]) for i in range(4)]
    if ridge_angle is None:
        return 0 if math.hypot(*e[0]) >= math.hypot(*e[1]) else 1
    c, s = math.cos(math.radians(ridge_angle)), math.sin(math.radians(ridge_angle))

    def along(v):  # how parallel an edge is to the ridge direction, either way round
        return abs(v[0] * c + v[1] * s) / (math.hypot(*v) or 1.0)

    return 0 if along(e[0]) >= along(e[1]) else 1


def roof(ring, kind, top, eave=None, ridge_angle=None):
    """Roof of one part. `ring` is anticlockwise [(x, y), ...].

    Returns (tops, slopes, gables): the wall-top height at every ring corner, the roof faces and
    the gable wall faces, each face a list of (x, y, z) anticlockwise seen from outside.
    - flat: no faces here (the builder makes the parapet and the deck); walls end at `top`.
    - shed: one plane, `eave` on the low side, `top` on the high side; the high side is to the left
      of `ridge_angle`.
    - gable, hip: `top` is the ridge, `eave` the wall top. Four-corner outlines get a true gable or
      hip. Any other outline gets a mansard: the outline moved in by the rise, a flat top inside.
    """
    n = len(ring)
    if kind == "flat":
        return [top] * n, [], []
    if eave is None:
        raise ValueError(f"a {kind} roof needs an eave height")
    if kind == "shed":
        a = math.radians((ridge_angle or 0.0) + 90.0)
        d = [p[0] * math.cos(a) + p[1] * math.sin(a) for p in ring]
        lo, span = min(d), (max(d) - min(d)) or 1.0
        tops = [eave + (top - eave) * (v - lo) / span for v in d]
        return tops, [[(p[0], p[1], z) for p, z in zip(ring, tops, strict=True)]], []
    tops = [eave] * n
    c = [(p[0], p[1], eave) for p in ring]
    if n == 4:
        k = _pair(ring, ridge_angle)
        i0, i1, i2, i3 = k, (k + 1) % 4, (k + 2) % 4, (k + 3) % 4
        m1, m2 = _mid(ring[i1], ring[i2]), _mid(ring[i3], ring[i0])
        if kind == "hip":
            long = math.hypot(m1[0] - m2[0], m1[1] - m2[1])
            half = math.hypot(ring[i2][0] - ring[i1][0], ring[i2][1] - ring[i1][1]) / 2
            t = min(half, long / 2) / (long or 1.0)  # 45 degree hips in plan
            m1, m2 = (
                (m1[0] + (m2[0] - m1[0]) * t, m1[1] + (m2[1] - m1[1]) * t),
                (m2[0] + (m1[0] - m2[0]) * t, m2[1] + (m1[1] - m2[1]) * t),
            )
        r1, r2 = (m1[0], m1[1], top), (m2[0], m2[1], top)
        point = math.hypot(m1[0] - m2[0], m1[1] - m2[1]) < 1e-6  # a square hip is a pyramid
        slopes = [
            [c[i0], c[i1], r1] if point else [c[i0], c[i1], r1, r2],
            [c[i2], c[i3], r2] if point else [c[i2], c[i3], r2, r1],
        ]
        ends = [[c[i1], c[i2], r1], [c[i3], c[i0], r2]]
        return (tops, slopes + ends, []) if kind == "hip" else (tops, slopes, ends)
    inner = mansard(ring, top - eave)
    q = [(p[0], p[1], top) for p in inner]
    slopes = [[c[i], c[(i + 1) % n], q[(i + 1) % n], q[i]] for i in range(n)]
    return tops, slopes + [q], []


def mansard(ring, rise):
    """The outline moved in by `rise` (a 45 degree slope), or by less where the part is too narrow
    for that: halved until the inner outline keeps its sense and a tenth of the area.
    """
    full = geom.area(ring)
    d = rise
    while d > 0.05:
        inner = geom.offset(ring, d, True)
        if 0.1 * full < geom.area(inner) < full:
            return inner
        d /= 2
    return list(ring)


def bays(length, spacing, margin=0.6):
    """Centres of evenly spaced bays along a wall of `length`, as distances from its start. The
    bays are centred on the wall; none when the wall is shorter than one bay plus the margins.
    """
    n = int((length - 2 * margin) // spacing)
    if n < 1:
        return []
    first = (length - (n - 1) * spacing) / 2
    return [first + i * spacing for i in range(n)]


def storey(wall_top, ground_low, floors, lo=2.7, hi=4.6):
    """Storey height when `floors` storeys stand between the lowest ground and the wall top, kept
    within what a real storey can be (the outline may sit on a bank or a plinth).
    """
    return min(hi, max(lo, (wall_top - ground_low) / max(1, floors)))
