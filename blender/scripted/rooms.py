"""Pure geometry of building interiors drawn from a floor plan: wall runs with door openings as
boxes, cut out of the parts another model already has (`keep_out`) and kept inside the shell
(`inside`); prisms for slabs, stairs, lift shafts and piers; room labels. No bpy.

Coordinates are model metres (x east, y north, z NAVD88), as everywhere in blender/scripted.
"""

import math

import geom

DOOR_HEAD = 2.1  # metres above the floor: a door's head when the plan gives none (UNVERIFIED)
WALL = 0.15  # partition thickness when the plan gives none


def _cuts(p, q, ring):
    """Fractions along p->q where the segment crosses the edges of `ring`."""
    out = []
    dx, dy = q[0] - p[0], q[1] - p[1]
    for a, b in zip(ring, ring[1:] + ring[:1], strict=True):
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
        u = ((a[0] - p[0]) * dy - (a[1] - p[1]) * dx) / den
        if 0 < t < 1 and 0 <= u <= 1:
            out.append(t)
    return out


def clip(seg, keep_out=(), inside=None):
    """The parts of segment `seg` ((x, y), (x, y)) that lie inside `inside` (when given) and
    outside every ring of `keep_out`, in order along the segment."""
    p, q = seg
    rings = list(keep_out) + ([inside] if inside else [])
    ts = sorted({0.0, 1.0, *[t for r in rings for t in _cuts(p, q, r)]})
    out = []
    for t0, t1 in zip(ts, ts[1:], strict=False):
        if t1 - t0 < 1e-9:
            continue
        tm = (t0 + t1) / 2
        mx, my = p[0] + (q[0] - p[0]) * tm, p[1] + (q[1] - p[1]) * tm
        if inside and not geom.inside(inside, mx, my):
            continue
        if any(geom.inside(r, mx, my) for r in keep_out):
            continue
        a = (p[0] + (q[0] - p[0]) * t0, p[1] + (q[1] - p[1]) * t0)
        b = (p[0] + (q[0] - p[0]) * t1, p[1] + (q[1] - p[1]) * t1)
        if out and math.dist(out[-1][1], a) < 1e-9:
            out[-1] = (out[-1][0], b)  # touching pieces are one piece
        else:
            out.append((a, b))
    return out


def _along(path, pt):
    """Distance along the polyline `path` of the point on it nearest to `pt`."""
    best, at, run = None, 0.0, 0.0
    for a, b in zip(path, path[1:], strict=False):
        ux, uy, d = b[0] - a[0], b[1] - a[1], math.dist(a, b)
        t = max(0.0, min(1.0, ((pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy) / (d * d or 1.0)))
        e = math.dist(pt, (a[0] + ux * t, a[1] + uy * t))
        if best is None or e < best:
            best, at = e, run + t * d
        run += d
    return at


def _point(path, s):
    """The point at distance `s` along the polyline `path`."""
    for a, b in zip(path, path[1:], strict=False):
        d = math.dist(a, b)
        if s <= d or b is path[-1]:
            t = s / d if d else 0.0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        s -= d
    return tuple(path[-1][:2])


def run_pieces(run, z0, z1, keep_out=(), inside=None):
    """A wall run as straight pieces {p, q, t, z0, z1}.

    `run`: {"path": [[x, y], ...], "thickness" (default WALL), "openings": [{"at": [x, y],
    "to": [x, y], "head": metres above z0 (default DOOR_HEAD; null for an opening to the
    ceiling)}]}. Each piece of the path is carried on by half the thickness past an inner corner,
    so the corners close. An opening leaves a lintel from its head to z1. Pieces are then cut to
    lie inside `inside` and outside every `keep_out` ring.
    """
    path = [tuple(v[:2]) for v in run["path"]]
    t = run.get("thickness", WALL)
    spans = []  # (s0, s1, z0, z1) along the path
    total = sum(math.dist(a, b) for a, b in zip(path, path[1:], strict=False))
    gaps = sorted(
        (sorted((_along(path, o["at"]), _along(path, o["to"]))), o.get("head", DOOR_HEAD))
        for o in run.get("openings", [])
    )
    s = 0.0
    for (g0, g1), head in gaps:
        if g0 > s:
            spans.append((s, g0, z0, z1))
        if head is not None and z0 + head < z1:
            spans.append((g0, g1, z0 + head, z1))
        s = max(s, g1)
    if s < total:
        spans.append((s, total, z0, z1))
    corners = []  # distances along the path of the inner corners
    run_len = 0.0
    for a, b in zip(path[:-1], path[1:-1], strict=False):
        run_len += math.dist(a, b)
        corners.append(run_len)
    out = []
    for s0, s1, za, zb in spans:
        # split the span at the corners, so every piece is straight
        cuts = [s0] + [c for c in corners if s0 < c < s1] + [s1]
        for c0, c1 in zip(cuts, cuts[1:], strict=False):
            p, q = _point(path, c0), _point(path, c1)
            d = math.dist(p, q)
            if d < 1e-6:
                continue
            ux, uy = (q[0] - p[0]) / d, (q[1] - p[1]) / d
            if any(abs(c0 - c) < 1e-9 for c in corners):
                p = (p[0] - ux * t / 2, p[1] - uy * t / 2)
            if any(abs(c1 - c) < 1e-9 for c in corners):
                q = (q[0] + ux * t / 2, q[1] + uy * t / 2)
            for a, b in clip((p, q), keep_out, inside):
                out.append(dict(p=a, q=b, t=t, z0=za, z1=zb))
    return out


def box(piece):
    """Eight corners of a wall piece: bottom four anticlockwise, then the top four."""
    (px, py), (qx, qy), h = piece["p"], piece["q"], piece["t"] / 2
    d = math.dist((px, py), (qx, qy))
    nx, ny = -(qy - py) / d * h, (qx - px) / d * h
    foot = [(px - nx, py - ny), (qx - nx, qy - ny), (qx + nx, qy + ny), (px + nx, py + ny)]
    return [(x, y, piece["z0"]) for x, y in foot] + [(x, y, piece["z1"]) for x, y in foot]


def prism(ring, z0, z1):
    """Vertices and outward faces of a closed vertical extrusion of `ring` from z0 to z1."""
    ring = [tuple(p[:2]) for p in ring]
    if geom.area(ring) < 0:
        ring = ring[::-1]
    n = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n, 2 * n)))
    faces.append(list(range(n - 1, -1, -1)))
    return verts, faces


def box_mesh(corners):
    """Vertices and outward faces of a box from `box()`."""
    return prism([c[:2] for c in corners[:4]], corners[0][2], corners[4][2])


def overlaps(ring, rings, step=0.25):
    """Does `ring` share area with any of `rings`? Sampled on a `step` grid inside `ring`, plus
    the vertices of the others: enough for plan checks, not for geometry."""
    x0, y0, x1, y1 = geom.bounds(ring)
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    for i in range(nx):
        for j in range(ny):
            x, y = x0 + (i + 0.5) * step, y0 + (j + 0.5) * step
            if geom.inside(ring, x, y) and any(geom.inside(r, x, y) for r in rings):
                return True
    return any(geom.inside(ring, *p[:2]) for r in rings for p in r)


def labels(floors):
    """Room numbers as plain label data: name, model x, y, label height z, floor, guess note."""
    out = []
    for f in floors:
        for r in f["rooms"]:
            out.append(
                dict(
                    name=r["number"],
                    x=round(r["at"][0], 2),
                    y=round(r["at"][1], 2),
                    z=round(f["floor"] + 1.6, 2),
                    floor=f["level"],
                    unverified=f["unverified"],
                )
            )
    return out
