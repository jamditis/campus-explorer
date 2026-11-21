"""Edge samples read from a triangle dump: the neighbour's top ground just outside the footprint.

Needs numpy (the test is skipped where it is missing).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

try:
    import edge
    import numpy as np
except ImportError:  # no numpy on this machine
    np = None

FOOT = [(0, 0), (20, 0), (20, 20), (0, 20)]


@unittest.skipIf(np is None, "numpy is not installed")
class EdgeFromTriangles(unittest.TestCase):
    def test_points_lie_just_outside_the_footprint_either_way_round(self):
        for ring in (FOOT, FOOT[::-1]):
            pts = edge.outside(ring, 1.0, 0.3)
            self.assertEqual(len(pts), 80)
            for x, y, px, py in pts:
                self.assertAlmostEqual(np.hypot(px - x, py - y), 0.3, places=6)
                self.assertFalse(0 < px < 20 and 0 < py < 20)

    def test_the_highest_triangle_over_a_point_sets_its_height(self):
        # a skirt at 100 m and a sidewalk 0.15 m over it on part of it; nothing at x 50
        skirt = [
            [(-5, -5, 100), (25, -5, 100), (25, 25, 100)],
            [(-5, -5, 100), (25, 25, 100), (-5, 25, 100)],
        ]
        walk = [[(5, -2, 100.15), (15, -2, 100.15), (15, 0, 100.15)]]
        tris = np.array(skirt + walk, float)
        z = edge.top_z(tris, np.array([2.0, 14.0, 50.0]), np.array([-1.0, -0.3, 0.0]))
        np.testing.assert_allclose(z[:2], [100.0, 100.15])
        self.assertTrue(np.isnan(z[2]))


if __name__ == "__main__":
    unittest.main()
