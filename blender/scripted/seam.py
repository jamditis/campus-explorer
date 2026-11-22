"""Where two scripted areas share an edge, both ground meshes take the same vertices there and the
same heights. numpy only (no bpy).

Each area densifies its own outline (ground.GRID), so along a shared edge the two meshes would
put their vertices at different points, and each area reads its heights from its own LiDAR
raster and edge blend: two outlines that do not meet, a crack and a step of a few centimetres,
more on a steep bank. So each area's outline also takes the other areas' densified points that lie
on it (`points_on`), and the area built first records the heights of its outline vertices
(`Seam.record`); a later area takes those heights for the vertices it shares (`Seam.take`).
"""

import math

import geom
import numpy as np

TOL = 0.02  # metres: a point this close to an outline lies on it (geom.insert_on_ring's tolerance)
CELL = 0.05  # metres: the lookup grid of recorded vertices


def points_on(ring, others, step=2.0):
    """The points of the other areas' outlines, densified every `step` metres as the ground
    densifies its own (ground.triangulate), that lie within TOL of the closed outline `ring`."""
    ring = [(p[0], p[1]) for p in ring]
    n = len(ring)
    out = []
    for other in others:
        for x, y, _s in geom.resample([(p[0], p[1]) for p in other], step, True):
            for i in range(n):
                (ax, ay), (bx, by) = ring[i], ring[(i + 1) % n]
                dx, dy = bx - ax, by - ay
                ln2 = (dx * dx + dy * dy) or 1e-12
                t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ln2))
                if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= TOL * TOL:
                    out.append((x, y))
                    break
    return out


END = 0.25  # metres along the outline either side that must lie on the shared edge too


def _near(ring, x, y, tol=TOL):
    n = len(ring)
    for i in range(n):
        (ax, ay), (bx, by) = ring[i][:2], ring[(i + 1) % n][:2]
        dx, dy = bx - ax, by - ay
        ln2 = (dx * dx + dy * dy) or 1e-12
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / ln2))
        if (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2 <= tol * tol:
            return True
    return False


def _along(ring, cum, total, s):
    """The point at arc length `s` (wrapped) along the closed outline `ring`."""
    s %= total
    i = int(np.searchsorted(cum, s, side="right") - 1)
    i = min(i, len(ring) - 1)
    (ax, ay), (bx, by) = ring[i], ring[(i + 1) % len(ring)]
    ln = cum[i + 1] - cum[i] or 1e-12
    t = (s - cum[i]) / ln
    return ax + t * (bx - ax), ay + t * (by - ay)


def ends(ring, others, step=END):
    """Points of the closed outline `ring`, `step` metres along it from each end of a stretch it
    shares with one of `others`, on the side that is not shared. At such an end the shared vertex
    takes the other area's height (the seam stays flush); the next vertex of this outline on its
    edge to the far field may be 2 m away, and the ground beside the far field climbed to that
    height over the whole run (up to 0.46 m in sw16 at village and west). A vertex here keeps
    this area's own height, so the change is held within `step`."""
    ring = [(p[0], p[1]) for p in ring]
    nxt = ring[1:] + ring[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(ring, nxt, strict=True)]
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cum[-1])

    def shared(x, y):
        return any(_near(o, x, y) for o in others)

    def arc(x, y):
        best, at = None, 0.0
        for i, (a, b) in enumerate(zip(ring, nxt, strict=True)):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln2 = (dx * dx + dy * dy) or 1e-12
            t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / ln2))
            d = (x - a[0] - t * dx) ** 2 + (y - a[1] - t * dy) ** 2
            if best is None or d < best:
                best, at = d, cum[i] + t * seg[i]
        return best, at

    # where a shared stretch can end: a corner of this outline on another one, or a corner of
    # another outline on this one
    cands = [p for p in ring if shared(*p)]
    for o in others:
        cands += [(p[0], p[1]) for p in o if arc(p[0], p[1])[0] <= TOL * TOL]
    out = []
    for x, y in cands:
        at = arc(x, y)[1]
        for s in (at - step, at + step):
            q = _along(ring, cum, total, s)
            if not shared(*q) and all(math.hypot(q[0] - r[0], q[1] - r[1]) > TOL for r in out):
                out.append(q)
    return out


class Seam:
    """Heights of outline vertices, shared between the areas of one build."""

    def __init__(self):
        self.cells = {}

    def record(self, xy, z):
        """Keep the heights `z` of the vertices `xy` (n x 2); a vertex already recorded keeps its
        first height."""
        for (x, y), h in zip(np.asarray(xy, float), np.asarray(z, float), strict=True):
            key = (round(x / CELL), round(y / CELL))
            self.cells.setdefault(key, []).append((x, y, float(h)))

    def take(self, xy):
        """The recorded height within TOL of each point of `xy`, NaN where none is."""
        xy = np.asarray(xy, float)
        out = np.full(len(xy), np.nan)
        for k, (x, y) in enumerate(xy):
            cx, cy = round(x / CELL), round(y / CELL)
            best = TOL * TOL + 1e-12  # strictly nearer: of two at one point, the first wins
            for i in (-1, 0, 1):
                for j in (-1, 0, 1):
                    for px, py, h in self.cells.get((cx + i, cy + j), ()):
                        d = (px - x) ** 2 + (py - y) ** 2
                        if d < best:
                            best, out[k] = d, h
        return out
