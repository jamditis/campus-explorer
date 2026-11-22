"""Two scripted areas side by side meet on the same vertices at the same heights.

Needs numpy (the test is skipped where it is missing).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

try:
    import geom
    import numpy as np
    import seam
except ImportError:  # no numpy on this machine
    np = None

# two areas that share the edge x = 100 from y 0 to 92.3; each is densified along its own
# outline, so their points on the shared edge do not coincide (92.3 / 47 against 279 / 140 m)
WEST = [(0, 0), (100, 0), (100, 92.3), (0, 92.3)]
EAST = [(100, 0), (300, 0), (300, 279), (100, 279)]


def dense(ring, step=2.0):
    return [(p[0], p[1]) for p in geom.resample(ring, step, True)]


def on_edge(ring):
    return sorted(round(p[1], 6) for p in ring if abs(p[0] - 100) < 1e-9 and p[1] <= 92.3 + 1e-9)


@unittest.skipIf(np is None, "numpy is not installed")
class SharedEdge(unittest.TestCase):
    def test_both_areas_get_the_same_vertices_on_the_shared_edge(self):
        west, east = dense(WEST), dense(EAST)
        self.assertNotEqual(on_edge(west), on_edge(east))
        west2 = geom.insert_on_ring(west, seam.points_on(WEST, [EAST]))
        east2 = geom.insert_on_ring(east, seam.points_on(EAST, [WEST]))
        a, b = on_edge(west2), on_edge(east2)
        # every vertex of one lies on a vertex of the other (within the insertion's 2 cm)
        for y in a:
            self.assertLess(min(abs(y - v) for v in b), 0.021)
        for y in b:
            self.assertLess(min(abs(y - v) for v in a), 0.021)

    def test_points_off_the_shared_edge_are_not_taken(self):
        pts = seam.points_on(WEST, [EAST])
        self.assertTrue(pts)
        for x, y in pts:
            self.assertAlmostEqual(x, 100.0)
            self.assertLessEqual(y, 92.3 + 1e-9)

    def test_a_later_area_takes_the_heights_the_first_one_gave_the_shared_vertices(self):
        s = seam.Seam()
        xy = np.array([[100.0, 10.0], [100.0, 12.0], [50.0, 0.0]])
        self.assertTrue(np.isnan(s.take(xy)).all())  # nothing recorded yet
        s.record(xy, np.array([5.0, 6.0, 7.0]))
        got = s.take(np.array([[100.0, 10.01], [100.0, 12.5], [100.0, 11.0]]))
        self.assertEqual(got[0], 5.0)  # within 2 cm: the recorded height
        self.assertTrue(np.isnan(got[1:]).all())  # anything further is the area's own
