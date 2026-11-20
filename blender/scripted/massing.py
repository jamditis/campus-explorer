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


def _cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _seg_dist(p, a, b):
    """Distance from point p to segment a-b."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    k = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1.0)))
    return math.hypot(a[0] + dx * k - p[0], a[1] + dy * k - p[1])


def _crosses(a, b, c, d):
    """Do segments a-b and c-d cross at a point inside both (touching at an end does not count)?"""
    d1, d2 = _cross(c, d, a), _cross(c, d, b)
    d3, d4 = _cross(a, b, c), _cross(a, b, d)
    return d1 * d2 < 0 and d3 * d4 < 0


def _edges_of(ring):
    return list(zip(ring, ring[1:] + ring[:1], strict=True))


def check_wells(ring, wells, clear=0.05):
    """Raise ValueError unless every well outline lies inside `ring`, at least `clear` metres from
    it, and apart from the other wells.
    """
    for k, w in enumerate(wells):
        if len(w) < 3:
            raise ValueError(f"well {k} needs at least three corners")
        if not all(geom.inside(ring, *p) for p in w):
            raise ValueError(f"well {k} does not lie inside the part")
        near = min(
            min(_seg_dist(p, a, b) for a, b in _edges_of(ring)) for p in w
        )
        near = min(near, min(min(_seg_dist(p, a, b) for a, b in _edges_of(w)) for p in ring))
        if near < clear:
            raise ValueError(f"well {k} comes within {near:.2f} m of the part's outline")
        for j, o in enumerate(wells[:k]):
            if (
                any(geom.inside(o, *p) for p in w)
                or any(geom.inside(w, *p) for p in o)
                or any(_crosses(a, b, c, d) for a, b in _edges_of(w) for c, d in _edges_of(o))
            ):
                raise ValueError(f"wells {j} and {k} overlap")


def _bridge(poly, hole, pts):
    """Join a hole (clockwise, as indices) to the polygon (anticlockwise, as indices) by a cut from
    the hole's east-most corner to the nearest polygon corner it can see. Returns the new loop.
    """
    m = max(range(len(hole)), key=lambda i: (pts[hole[i]][0], -pts[hole[i]][1]))
    mp = pts[hole[m]]
    loop_edges = [(pts[a], pts[b]) for a, b in zip(poly, poly[1:] + poly[:1], strict=True)]
    hole_edges = [(pts[a], pts[b]) for a, b in zip(hole, hole[1:] + hole[:1], strict=True)]
    order = sorted(range(len(poly)), key=lambda i: math.dist(pts[poly[i]], mp))
    for i in order:
        q = pts[poly[i]]
        if any(_crosses(mp, q, a, b) for a, b in loop_edges + hole_edges):
            continue
        # the cut must leave the corner q into the polygon's inside
        prev, nxt = pts[poly[i - 1]], pts[poly[(i + 1) % len(poly)]]
        convex = _cross(prev, q, nxt) > 0
        left_in, right_in = _cross(prev, q, mp) > 0, _cross(q, nxt, mp) > 0
        if (left_in and right_in) if convex else (left_in or right_in):
            ring = hole[m:] + hole[:m]
            return poly[: i + 1] + ring + [hole[m], poly[i]] + poly[i + 1 :]
    raise ValueError("a well cannot be joined to the deck outline")


def _inside_tri(p, a, b, c):
    return _cross(a, b, p) > 1e-9 and _cross(b, c, p) > 1e-9 and _cross(c, a, p) > 1e-9


def deck_triangles(outer, holes=()):
    """Triangles of a flat deck: the anticlockwise `outer` outline with `holes` (wells) left open.

    Points are numbered as `outer` followed by each hole in turn; each triangle is a triple of
    those numbers, anticlockwise seen from above. Ear clipping after the holes are joined to the
    outline by cuts, so a deck of n corners with h hole corners in k holes gives n + h + 2k - 2
    triangles (fewer where corners lie on a straight run). No bpy, no dense grid.
    """
    pts = [tuple(p[:2]) for p in outer]
    poly = list(range(len(pts)))
    loops = []
    for h in holes:
        base = len(pts)
        pts += [tuple(p[:2]) for p in h]
        idx = list(range(base, len(pts)))
        loops.append(idx if geom.area([pts[i] for i in idx]) < 0 else idx[::-1])
    for hole in sorted(loops, key=lambda h: -max(pts[i][0] for i in h)):
        poly = _bridge(poly, hole, pts)
    tris = []
    guard = 0
    while len(poly) > 3 and guard < 10 * len(pts) ** 2:
        guard += 1
        n = len(poly)
        for i in range(n):
            ia, ib, ic = poly[i - 1], poly[i], poly[(i + 1) % n]
            a, b, c = pts[ia], pts[ib], pts[ic]
            turn = _cross(a, b, c)
            if abs(turn) < 1e-9:  # a straight run (or a cut folded back on itself): no triangle
                del poly[i]
                break
            if turn < 0:
                continue
            if any(
                _inside_tri(pts[j], a, b, c)
                for j in poly
                if pts[j] != a and pts[j] != b and pts[j] != c
            ):
                continue
            tris.append((ia, ib, ic))
            del poly[i]
            break
        else:
            raise ValueError("the deck outline cannot be split into triangles")
    if len(poly) == 3 and _cross(*(pts[i] for i in poly)) > 1e-9:
        tris.append(tuple(poly))
    return tris


def parapet_inner(ring, width=0.3):
    """Inner edge of a flat roof's parapet: the outline moved in by `width`, or the outline itself
    when the part is too narrow for a parapet.
    """
    inner = geom.offset(ring, width, True)
    return inner if 0 < geom.area(inner) < geom.area(ring) else list(ring)


def well_deck(ring, kind, top, eave=None, ridge_angle=None):
    """The outline that a part's wells sink into: the deck inside the parapet of a flat roof, or
    the flat top of a mansard. None for a roof that has no such deck.
    """
    if kind == "flat":
        return parapet_inner(ring)
    if kind in ("gable", "hip") and len(ring) != 4:
        return [q[:2] for q in roof(ring, kind, top, eave, ridge_angle)[1][-1]]
    return None
