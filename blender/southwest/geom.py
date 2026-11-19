"""Plan geometry for the southwest build: straight runs and true arcs only. No bpy, no third-party
imports.

A *path* is a list of vertices `[x, y]` or `[x, y, r]`, in model metres (x east, y north). `r`
rounds that
corner with a true arc of radius r, tangent to both neighbouring runs. `expand()` turns a path into
a dense
polyline; nothing else in the build invents curve points, so every edge is a straight run or a true
arc.
"""

import math

CHORD = 0.01  # largest gap between an arc and its polyline, metres


def _unit(ax, ay, bx, by):
    d = math.hypot(bx - ax, by - ay)
    return ((bx - ax) / d, (by - ay) / d, d) if d > 1e-12 else (0.0, 0.0, 0.0)


def fillet(p, v, n, r, chord=CHORD):
    """
    Arc points that round corner `v` between runs p->v and v->n. Empty when the runs are collinear.
    """
    ux, uy, du = _unit(v[0], v[1], p[0], p[1])
    wx, wy, dw = _unit(v[0], v[1], n[0], n[1])
    cos_a = max(-1.0, min(1.0, ux * wx + uy * wy))
    ang = math.acos(cos_a)  # interior angle at v
    if r <= 0 or ang < 1e-6 or math.pi - ang < 1e-6:
        return []
    t = r / math.tan(ang / 2)  # distance from v to each tangent point
    if t > min(du, dw) + 1e-9:
        raise ValueError(
            f"fillet radius {r} does not fit at {v[:2]}: "
            f"needs {t:.2f} m of run, has {min(du, dw):.2f}"
        )
    bis = _unit(0, 0, ux + wx, uy + wy)
    k = r / math.sin(ang / 2)
    cx, cy = v[0] + bis[0] * k, v[1] + bis[1] * k
    a0 = math.atan2(v[1] + uy * t - cy, v[0] + ux * t - cx)
    a1 = math.atan2(v[1] + wy * t - cy, v[0] + wx * t - cx)
    sweep = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    steps = max(2, math.ceil(abs(sweep) / (2 * math.acos(max(0.0, 1 - chord / r)))))
    return [
        (cx + r * math.cos(a0 + sweep * i / steps), cy + r * math.sin(a0 + sweep * i / steps))
        for i in range(steps + 1)
    ]


def expand(path, closed=False, chord=CHORD):
    """Dense polyline for a path. A closed path does not repeat its first point."""
    n = len(path)
    out = []
    for i, v in enumerate(path):
        r = v[2] if len(v) > 2 else 0
        ends = not closed and i in (0, n - 1)
        pts = [] if ends or not r else fillet(path[(i - 1) % n], v, path[(i + 1) % n], r, chord)
        for q in pts or [(v[0], v[1])]:
            if not out or math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) > 1e-6:
                out.append((q[0], q[1]))
    if (
        closed
        and len(out) > 1
        and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-6
    ):
        out.pop()
    return out


def length(line, closed=False):
    pts = line + [line[0]] if closed else line
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:], strict=False))


def offset(line, d, closed=False):
    """Parallel copy of a dense polyline, `d` metres to its left (negative: right). Mitred at each
    point.
    """
    n = len(line)
    out = []
    for i, p in enumerate(line):
        a = line[(i - 1) % n] if closed or i > 0 else None
        b = line[(i + 1) % n] if closed or i < n - 1 else None
        u1 = _unit(a[0], a[1], p[0], p[1]) if a else None
        u2 = _unit(p[0], p[1], b[0], b[1]) if b else None
        u1, u2 = u1 or u2, u2 or u1
        nx, ny = -(u1[1] + u2[1]), u1[0] + u2[0]
        m = math.hypot(nx, ny)
        if m < 1e-9:  # a reversal: fall back to one run's normal
            nx, ny, m = -u1[1], u1[0], 1.0
        nx, ny = nx / m, ny / m
        k = d / max(0.2, nx * -u1[1] + ny * u1[0])  # mitre length, limited at sharp corners
        out.append((p[0] + nx * k, p[1] + ny * k))
    return out


def ribbon(centre, width, chord=CHORD):
    """Closed outline of a strip `width` wide along a centre path (road, walk, fence line)."""
    line = expand(centre, False, chord)
    return offset(line, width / 2) + offset(line, -width / 2)[::-1]


def resample(line, step, closed=False):
    """
    Points every `step` metres along a polyline, plus its corners, with the cumulative distance of
    each.
    """
    pts = line + [line[0]] if closed else line
    out, s = [], 0.0
    for a, b in zip(pts, pts[1:], strict=False):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, math.ceil(d / step))
        for i in range(k):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k, s + d * i / k))
        s += d
    if not closed:
        out.append((pts[-1][0], pts[-1][1], s))
    return out


def area(ring):
    """Signed area of a closed polyline: positive when it runs anticlockwise."""
    return (
        sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:] + ring[:1], strict=True)) / 2
    )


def inside(ring, x, y):
    """Even-odd test: is (x, y) inside the closed polyline?"""
    hit = False
    for a, b in zip(ring, ring[1:] + ring[:1], strict=True):
        if (a[1] > y) != (b[1] > y) and x < a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]):
            hit = not hit
    return hit


def bounds(ring):
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    return min(xs), min(ys), max(xs), max(ys)


def frame(origin, angle_deg):
    """
    Functions that map model (x, y) to a local frame (u along `angle_deg` from east, v to its left)
    and back.
    """
    c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    ox, oy = origin

    def to_local(x, y):
        return (x - ox) * c + (y - oy) * s, -(x - ox) * s + (y - oy) * c

    def to_model(u, v):
        return ox + u * c - v * s, oy + u * s + v * c

    return to_local, to_model


def stalls(m):
    """Divider lines of a `stalls` marking: `count` stalls along `line` give count + 1 lines.

    Each line starts on `line` and runs `depth` metres to its `side` ("left" or "right" of the
    direction
    from the first point to the second), at `angle` degrees to the line (90 = square stalls).
    """
    (ax, ay), (bx, by) = m["line"]
    n = m["count"]
    d = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / d, (by - ay) / d
    ang = math.radians(m.get("angle", 90)) * (1 if m.get("side", "left") == "left" else -1)
    dx, dy = ux * math.cos(ang) - uy * math.sin(ang), ux * math.sin(ang) + uy * math.cos(ang)
    depth = m.get("depth", 5.5)
    return [
        [
            (ax + ux * d * i / n, ay + uy * d * i / n),
            (ax + ux * d * i / n + dx * depth, ay + uy * d * i / n + dy * depth),
        ]
        for i in range(n + 1)
    ]


def hull(points):
    """Convex hull of (x, y) points, anticlockwise (Andrew's monotone chain)."""
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def half(seq):
        out = []
        for p in seq:
            while (
                len(out) >= 2
                and (out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])
                <= 0
            ):
                out.pop()
            out.append(p)
        return out[:-1]

    return half(pts) + half(pts[::-1])


def long_axis(ring):
    """
    Angle (degrees from east, 0..180) of the side of the smallest rectangle around the ring that is
    longest.
    """
    h = hull([(p[0], p[1]) for p in ring])
    best = None
    for a, b in zip(h, h[1:] + h[:1], strict=True):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        c, s = math.cos(ang), math.sin(ang)
        us = [p[0] * c + p[1] * s for p in h]
        vs = [-p[0] * s + p[1] * c for p in h]
        du, dv = max(us) - min(us), max(vs) - min(vs)
        if best is None or du * dv < best[0]:
            best = (du * dv, ang if du >= dv else ang + math.pi / 2)
    return math.degrees(best[1]) % 180


def sheets(name, ring, max_len=100.0, margin=3.0, ppm=40.0, max_px=4096):
    """Texture sheets for a painted surface: rectangles along the surface's long axis, at most
    `max_len` long.

    Each sheet is {"name", "angle", "u0", "u1", "v0", "v1", "w", "h", "cut0", "cut1"}: its frame is
    model
    (x, y) turned by `angle` about the origin; u0..u1 and v0..v1 are its extent there (with `margin`
    all round),
    w x h its size in pixels, and cut0..cut1 the part of the long axis whose faces use this sheet.
    paint.py draws them and ground.py maps faces to them, so both must call this with the same
    arguments.
    """
    ang = long_axis(ring)
    to_local, _ = frame((0.0, 0.0), ang)
    loc = [to_local(p[0], p[1]) for p in ring]
    u0, u1 = min(p[0] for p in loc), max(p[0] for p in loc)
    v0, v1 = min(p[1] for p in loc), max(p[1] for p in loc)
    n = max(1, math.ceil((u1 - u0) / max_len))
    step = (u1 - u0) / n
    out = []
    for i in range(n):
        a, b = u0 + i * step, u0 + (i + 1) * step
        su0, su1, sv0, sv1 = a - margin, b + margin, v0 - margin, v1 + margin
        k = min(ppm, max_px / (su1 - su0), max_px / (sv1 - sv0))
        out.append(
            dict(
                name=f"authored_{name}_{i}",
                angle=ang,
                u0=su0,
                u1=su1,
                v0=sv0,
                v1=sv1,
                w=max(8, round((su1 - su0) * k)),
                h=max(8, round((sv1 - sv0) * k)),
                cut0=a,
                cut1=b,
            )
        )
    return out


def dashes(line, dash, gap):
    """Cut a dense polyline into dash pieces of length `dash` separated by `gap`."""
    out, cur, s, on = [], [line[0]], 0.0, True
    for a, b in zip(line, line[1:], strict=False):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        t = 0.0
        while d - t > 1e-9:
            room = (dash if on else gap) - s
            take = min(room, d - t)
            t += take
            s += take
            p = (a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d)
            if on:
                cur.append(p)
            if s >= (dash if on else gap) - 1e-9:
                if on and len(cur) > 1:
                    out.append(cur)
                on, s, cur = not on, 0.0, [p]
    if on and len(cur) > 1:
        out.append(cur)
    return out
