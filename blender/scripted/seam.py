"""Where two scripted areas share an edge, both ground meshes take the same vertices there and the
same heights. numpy only (no bpy).

Each area densifies its own outline (ground.GRID), so along a shared edge the two meshes would
put their vertices at different points, and each area reads its heights from its own LiDAR
raster and edge blend: two outlines that do not meet, a crack and a step of a few centimetres,
more on a steep bank. So each area's outline also takes the other areas' densified points that lie
on it (`points_on`), and the area built first records the heights of its outline vertices
(`Seam.record`); a later area takes those heights for the vertices it shares (`Seam.take`).
"""

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
