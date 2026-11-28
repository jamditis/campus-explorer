"""Pure geometry for building parts: roof shapes, window bays, storey heights. No bpy.

A part is an anticlockwise outline with a roof type. Every function here returns plain tuples, so
the shapes can be unit tested without Blender; building.py turns them into meshes.
"""

import math

import geom

PARAPET = {"deck": 1.1}  # height of the parapet above the roof deck; 0.4 for everything else


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


def _plane(face):
    """z(x, y) of the plane of a roof face (Newell normal; a roof face is never vertical)."""
    nx = ny = nz = 0.0
    for i, (x0, y0, z0) in enumerate(face):
        x1, y1, z1 = face[(i + 1) % len(face)]
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    cx, cy, cz = (sum(q[k] for q in face) / len(face) for k in range(3))
    return (lambda x, y: cz - (nx * (x - cx) + ny * (y - cy)) / nz), (nx, ny, nz)


def _up(poly):
    """A face wound anticlockwise seen from above (facing up)."""
    return poly if geom.area([q[:2] for q in poly]) > 0 else poly[::-1]


def overhang_roof(ring, faces, overhang):
    """The faces that carry a pitched roof `overhang` metres past its walls (wide eaves and
    rakes), each in the plane of the roof face it continues, so every face keeps its own pitch:
    a strip outside every face edge that lies on the wall line, and at each corner of the
    outline the gap between two strips, split where the two faces' planes meet (faces of
    different pitch join without a step). Faces off the wall line (a mansard's flat top, the
    edges of a roof well) get nothing. `ring` anticlockwise; returns the new faces, facing up."""
    n, out = len(ring), []
    norm = []
    for i in range(n):
        (ax, ay), (bx, by) = ring[i], ring[(i + 1) % n]
        ln = math.hypot(bx - ax, by - ay)
        norm.append(((by - ay) / ln, -(bx - ax) / ln))  # outward: right of an anticlockwise run

    def on_edge(p, i):
        (ax, ay), (bx, by) = ring[i], ring[(i + 1) % n]
        return _seg_dist(p[:2], (ax, ay), (bx, by)) < 1e-6

    owner = {}  # (ring edge, ring corner at its start or end) -> plane of the face over it
    for face in faces:
        z, _nrm = _plane(face)
        for k in range(len(face)):
            p, q = face[k], face[(k + 1) % len(face)]
            for i in range(n):
                if on_edge(p, i) and on_edge(q, i) and math.dist(p[:2], q[:2]) > 1e-6:
                    nx, ny = norm[i]
                    p2 = (p[0] + nx * overhang, p[1] + ny * overhang)
                    q2 = (q[0] + nx * overhang, q[1] + ny * overhang)
                    out.append(_up([p, q, (*q2, z(*q2)), (*p2, z(*p2))]))
                    for c, end in ((i, p), ((i + 1) % n, q)):
                        if math.dist(end[:2], ring[c]) < 1e-6:
                            owner[(i, c)] = (z, _nrm)
    for c in range(n):  # the corner between edge c - 1 (ending at c) and edge c (starting at c)
        a, b = (c - 1) % n, c
        if (a, c) not in owner or (b, c) not in owner:
            continue
        if norm[a][0] * norm[b][1] - norm[a][1] * norm[b][0] <= 0:
            continue  # a reflex corner: the two strips overlap there, there is no gap to fill
        (za, na), (zb, nb) = owner[(a, c)], owner[(b, c)]
        cx, cy = ring[c]
        ea = (cx + norm[a][0] * overhang, cy + norm[a][1] * overhang)
        eb = (cx + norm[b][0] * overhang, cy + norm[b][1] * overhang)
        dot = norm[a][0] * norm[b][0] + norm[a][1] * norm[b][1]
        m = (cx + (norm[a][0] + norm[b][0]) * overhang / (1 + dot),
             cy + (norm[a][1] + norm[b][1]) * overhang / (1 + dot))  # fmt: skip
        corner = (cx, cy, za(cx, cy))
        # where the planes meet, in plan: the line through the corner along the cross product
        dx = na[1] * nb[2] - na[2] * nb[1]
        dy = na[2] * nb[0] - na[0] * nb[2]
        split = m
        if math.hypot(dx, dy) > 1e-9:
            if dx * (m[0] - cx) + dy * (m[1] - cy) < 0:
                dx, dy = -dx, -dy
            best = None
            for e, nrm in ((ea, norm[a]), (eb, norm[b])):  # the strip's outer line it reaches
                den = dx * nrm[0] + dy * nrm[1]
                if den > 1e-12:
                    t = overhang / den
                    if best is None or t < best[0]:
                        best = (t, e)
            if best:
                split = (cx + dx * best[0], cy + dy * best[0])
        def on_line(q, e, nrm):  # on the strip's outer line through e
            return abs((q[0] - e[0]) * nrm[0] + (q[1] - e[1]) * nrm[1]) < 1e-6

        if math.dist(split, m) < 1e-9:
            pa, pb = [ea, m], [m, eb]
        elif on_line(split, ea, norm[a]):  # the meeting line leaves through edge a's side
            pa, pb = [ea, split], [split, m, eb]
        else:
            pa, pb = [ea, m, split], [split, eb]
        out.append(_up([corner, *[(*q, za(*q)) for q in pa]]))
        out.append(_up([(cx, cy, zb(cx, cy)), *[(*q, zb(*q)) for q in pb]]))
    return out


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
        # a well round a concave corner of the part has all its corners inside and still leaves it
        if any(geom.inside(w, *p) for p in ring) or any(
            _crosses(a, b, c, d) for a, b in _edges_of(w) for c, d in _edges_of(ring)
        ):
            raise ValueError(f"well {k} crosses the part's outline")
        near = min(min(_seg_dist(p, a, b) for a, b in _edges_of(ring)) for p in w)
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


def _bridge(poly, hole, pts, others=()):
    """Join a hole (clockwise, as indices) to the polygon (anticlockwise, as indices) by a cut from
    the hole's east-most corner to the nearest polygon corner it can see past the holes still to
    be joined (`others`). Returns the new loop.
    """
    m = max(range(len(hole)), key=lambda i: (pts[hole[i]][0], -pts[hole[i]][1]))
    mp = pts[hole[m]]
    loop_edges = [(pts[a], pts[b]) for a, b in zip(poly, poly[1:] + poly[:1], strict=True)]
    hole_edges = [
        (pts[a], pts[b]) for h in (hole, *others) for a, b in zip(h, h[1:] + h[:1], strict=True)
    ]
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
    loops.sort(key=lambda h: -max(pts[i][0] for i in h))
    for k, hole in enumerate(loops):
        poly = _bridge(poly, hole, pts, loops[k + 1 :])
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


def inset(ring, dists):
    """The anticlockwise outline `ring` with each edge i moved in by dists[i] (0 keeps it), as the
    corners where neighbouring moved edges meet. Corner i lies between edge i-1 and edge i."""
    n = len(ring)
    lines = []
    for i in range(n):
        (ax, ay), (bx, by) = ring[i][:2], ring[(i + 1) % n][:2]
        length = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / length, (by - ay) / length
        nx, ny = -uy, ux  # inward normal of an anticlockwise outline
        lines.append(((ax + nx * dists[i], ay + ny * dists[i]), (ux, uy)))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(den) < 0.35:  # (nearly) straight on: the lines meet far off or never
            # take the start of the edge moved further, square off its own wall
            k, p = (i - 1, p1) if dists[i - 1] > dists[i] else (i, p2)
            if k == i - 1:  # the end of the previous moved edge, at this corner
                (ax, ay), (ux, uy) = ring[i][:2], d1
                p = (ax - uy * dists[k], ay + ux * dists[k])
            out.append(p)
            continue
        u = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
        out.append((p1[0] + d1[0] * u, p1[1] + d1[1] * u))
    return out


def ring_roof(
    ring, eave, crest_z, crest_in, inner_in, base, flat_edges=(), crest=None, inner=None,
    overhang=None,
):  # fmt: skip
    """A tiled ring round a flat roof (a mansard band): from the wall line at `eave` up to a crest
    line `crest_in` metres in at `crest_z`, a flat crest band to `inner_in` metres in (each a
    number, or one per edge), then a drop to the flat roof at `base`. Edges in `flat_edges` (walls
    shared with another building, or a side another roof covers) get no slope: the band ends
    there with a vertical cap in the wall's plane. `crest` and `inner` may give the two inner
    outlines explicitly (one corner per ring corner) where a plain inset would fold over itself.
    `overhang` (a number, or one per edge) carries each slope on past the wall line, down at the
    same pitch. Returns faces of (x, y, z), each anticlockwise seen from outside."""
    ring = [tuple(p[:2]) for p in ring]
    n = len(ring)
    ci = list(crest_in) if isinstance(crest_in, list | tuple) else [crest_in] * n
    ii = list(inner_in) if isinstance(inner_in, list | tuple) else [inner_in] * n
    flat = set(flat_edges)
    if any(not 0 < ci[i] < ii[i] for i in range(n) if i not in flat):
        raise ValueError("the crest must lie between the wall line and the inner edge")
    c = crest or inset(ring, [0.0 if i in flat else ci[i] for i in range(n)])
    m = inner or inset(ring, [0.0 if i in flat else ii[i] for i in range(n)])
    ov = list(overhang) if isinstance(overhang, list | tuple) else [overhang or 0.0] * n
    ov = [0.0 if i in flat else ov[i] for i in range(n)]
    outer = inset(ring, [-v for v in ov]) if any(ov) else ring
    faces = []

    def add(face):
        # leave out faces that have no area (collapsed at a flat edge)
        pts = [f for k, f in enumerate(face) if k == 0 or math.dist(f, face[k - 1]) > 1e-6]
        if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
            pts = pts[:-1]
        if len(pts) >= 3 and any(abs(v) > 1e-9 for v in _area3(pts)):
            faces.append(pts)

    for i in range(n):
        j = (i + 1) % n
        if i in flat:
            continue
        o0, o1 = outer[i], outer[j]
        low = eave - ov[i] * (crest_z - eave) / ci[i]
        add([(*o0, low), (*o1, low), (*c[j], crest_z), (*c[i], crest_z)])
        add([(*c[i], crest_z), (*c[j], crest_z), (*m[j], crest_z), (*m[i], crest_z)])
        add([(*m[i], crest_z), (*m[j], crest_z), (*m[j], base), (*m[i], base)])
    for i in range(n):  # caps where a sloped edge meets a flat one, in the flat edge's wall plane
        j = (i + 1) % n
        if i in flat and (i - 1) % n not in flat:  # corner i: band coming from edge i-1
            o = ring[i]
            add([(*o, eave), (*o, base), (*m[i], base), (*m[i], crest_z), (*c[i], crest_z)])
        if i in flat and j not in flat:  # corner j: band going on along edge j
            o = ring[j]
            add([(*o, eave), (*c[j], crest_z), (*m[j], crest_z), (*m[j], base), (*o, base)])
    return faces


def _area3(pts):
    """Twice the vector area of a 3D polygon."""
    x = y = z = 0.0
    for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:] + pts[:1], strict=True):
        x += y0 * z1 - z0 * y1
        y += z0 * x1 - x0 * z1
        z += x0 * y1 - y0 * x1
    return x, y, z


def wall_pieces(length, z0, z1, openings):
    """A wall face `length` long from z0 to z1 as rectangles (s0, s1, za, zb) that leave out the
    `openings` (s0, s1, za, zb) along it: full-height strips between openings, and the parts below
    and above each opening."""
    cuts = sorted({0.0, length, *[max(0.0, min(length, v)) for o in openings for v in o[:2]]})
    out = []
    for s0, s1 in zip(cuts, cuts[1:], strict=False):
        if s1 - s0 < 1e-9:
            continue
        mid = (s0 + s1) / 2
        holes = sorted((o[2], o[3]) for o in openings if o[0] < mid < o[1])
        z = z0
        for za, zb in holes:
            if za > z:
                out.append((s0, s1, z, min(za, z1)))
            z = max(z, zb)
        if z < z1:
            out.append((s0, s1, z, z1))
    return out


def edge_openings(ring, openings):
    """{edge index: [(s0, s1, z0, z1), ...]} for openings given by two points `at`, `to` on one
    edge of the anticlockwise `ring` (within 0.3 m of its line) and their `z0`, `z1`."""
    out = {}
    n = len(ring)
    for o in openings:
        found = None
        for i in range(n):
            a, b = ring[i][:2], ring[(i + 1) % n][:2]
            length = math.dist(a, b)
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            ss = []
            for p in (o["at"], o["to"]):
                s = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
                off = abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux)
                ss.append(s if (off < 0.3 and -0.01 <= s <= length + 0.01) else None)
            if None not in ss:
                found = (i, min(ss), max(ss))
                break
        if found is None:
            raise ValueError(f"opening {o} lies on no edge of the outline")
        i, s0, s1 = found
        out.setdefault(i, []).append((s0, s1, o["z0"], o["z1"]))
    return out


def window_rows(wall_top, ground, tall, sill, levels=None, floors=1, storey_h=None, rows=None):
    """(bottom, top) of the window rows on one bay. `rows` gives each row's bottom and top
    (NAVD88 metres: rows read off a neighbouring facade, so the two line up); with `levels`
    (floor heights) a row `tall` high stands `sill` above each floor. Either way a row is kept when
    its bottom is at least 0.4 m above the ground there and its top under the wall top. Without
    both, rows are counted down from the wall top in storeys of `storey_h`, stopping at the first
    one below the ground (the old rule)."""
    if rows is None and levels is not None:
        rows = [(lv + sill, lv + sill + tall) for lv in levels]
    if rows is not None:
        return [(z0, z1) for z0, z1 in rows if z0 >= ground + 0.4 and z1 <= wall_top]
    out = []
    for f in range(floors):
        z0 = wall_top - (f + 1) * storey_h + sill
        if z0 < ground + 0.4:
            break
        out.append((z0, z0 + tall))
    return out


def _beam(p, q, width, height):
    """A box of `width` on top of the segment p -> q (3D points), `height` tall: (verts, faces)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    d = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / d * width / 2, dx / d * width / 2
    b = [(p[0] - nx, p[1] - ny, p[2]), (q[0] - nx, q[1] - ny, q[2]),
         (q[0] + nx, q[1] + ny, q[2]), (p[0] + nx, p[1] + ny, p[2])]  # fmt: skip
    verts = b + [(x, y, z + height) for x, y, z in b]
    faces = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return verts, faces


def ring_caps(ring, eave, crest_z, crest_in, flat_edges=(), width=0.3, height=0.15, overhang=None):
    """Ridge and hip caps of a ring roof (ring_roof's arguments): a cap along the crest line of
    every sloped edge, and one up each convex corner where two sloped edges meet."""
    ring = [tuple(p[:2]) for p in ring]
    n = len(ring)
    flat = set(flat_edges)
    ci = list(crest_in) if isinstance(crest_in, list | tuple) else [crest_in] * n
    ov = list(overhang) if isinstance(overhang, list | tuple) else [overhang or 0.0] * n
    ov = [0.0 if i in flat else ov[i] for i in range(n)]
    c = inset(ring, [0.0 if i in flat else ci[i] for i in range(n)])
    outer = inset(ring, [-v for v in ov]) if any(ov) else ring
    out = []
    for i in range(n):
        j = (i + 1) % n
        if i in flat or math.dist(c[i], c[j]) < 1e-6:
            continue
        out.append(_beam((*c[i], crest_z), (*c[j], crest_z), width, height))
    for i in range(n):  # corner i between edge i-1 and edge i
        k = (i - 1) % n
        if i in flat or k in flat:
            continue
        a, o, b = ring[k], ring[i], ring[(i + 1) % n]
        turn = (o[0] - a[0]) * (b[1] - o[1]) - (o[1] - a[1]) * (b[0] - o[0])
        if turn <= 0:
            continue  # a concave corner takes a valley, not a hip
        low = eave - ov[i] * (crest_z - eave) / ci[i]
        out.append(_beam((*outer[i], low), (*c[i], crest_z), width, height))
    return out


def window_cells(ring, ground, wall_top, width, height, spacing, sill, levels, edges, rows=None):
    """Window openings on the listed edges of an anticlockwise outline: one per bay and row
    (massing.bays, massing.window_rows), as {edge, s0, s1, z0, z1, a, u, n}: the edge's start
    point, its direction and outward normal, and the opening along it."""
    out = []
    n = len(ring)
    for i in edges:
        a, b = ring[i][:2], ring[(i + 1) % n][:2]
        length = math.dist(a, b)
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        nrm = (u[1], -u[0])
        for s in bays(length, spacing):
            g = ground(a[0] + u[0] * s, a[1] + u[1] * s)
            for z0, z1 in window_rows(wall_top, g, height, sill, levels, rows=rows):
                out.append(dict(edge=i, s0=s - width / 2, s1=s + width / 2, z0=z0, z1=z1,
                                a=a, u=u, n=nrm))  # fmt: skip
    return out


def eave_course(ring, edges, z, width=0.45, height=0.22):
    """A tile course along the wall top of the listed edges, centred on the wall line, from `z`
    up: where a roof has no overhang (the main model's barrel tile eave course, scripted)."""
    n = len(ring)
    return [
        _beam((*ring[i][:2], z), (*ring[(i + 1) % n][:2], z), width, height) for i in edges
    ]
