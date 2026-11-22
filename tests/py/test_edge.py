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

    def test_a_step_between_two_samples_is_found_and_sampled_on_both_sides(self):
        # a skirt at 100 m outside the south edge, another model's sidewalk at 100.9 m from
        # x 12.37 on: samples every metre miss the step by up to half a metre; the refined ones
        # lie on either side of it, at most 5 cm apart, with their own side's height
        skirt = [[(-5, -5, 100), (12.37, -5, 100), (12.37, 0, 100)],
                 [(-5, -5, 100), (12.37, 0, 100), (-5, 0, 100)]]
        walk = [[(12.37, -5, 100.9), (25, -5, 100.9), (25, 0, 100.9)],
                [(12.37, -5, 100.9), (25, 0, 100.9), (12.37, 0, 100.9)]]
        tris = np.array(skirt + walk, float)
        got = edge.sample(FOOT, tris)
        south = [s for s in got if s[1] == 0.0 and 0 <= s[0] <= 20]
        xs = [s[0] for s in south]
        self.assertEqual(xs, sorted(xs))
        low = max(s[0] for s in south if s[2] < 100.5)
        high = min(s[0] for s in south if s[2] > 100.5)
        self.assertLess(high - low, 0.051)
        self.assertTrue(low <= 12.37 <= high)
        # the plain samples every metre are all still there
        self.assertTrue(all(any(abs(s[0] - x) < 1e-6 for s in south) for x in range(0, 20)))

    def test_a_step_at_a_corner_is_sampled_on_both_edges_of_the_corner(self):
        # another model's sidewalk south of the south edge (100.9 m), a skirt west of the west
        # edge (100 m): the neighbour steps at the corner (0, 0). No sample on the corner itself
        # (it would read either); one just along each edge, with that edge's height
        walk = [[(0, -5, 100.9), (25, -5, 100.9), (25, 0, 100.9)],
                [(0, -5, 100.9), (25, 0, 100.9), (0, 0, 100.9)]]
        skirt = [[(-5, -5, 100), (0, -5, 100), (0, 25, 100)],
                 [(-5, -5, 100), (0, 25, 100), (-5, 25, 100)]]
        got = edge.sample(FOOT, np.array(walk + skirt, float))
        near = [s for s in got if np.hypot(s[0], s[1]) < 0.5]
        self.assertFalse(any(s[0] == 0.0 and s[1] == 0.0 for s in near))
        south = [s for s in near if s[1] == 0.0 and s[0] > 0]
        west = [s for s in near if s[0] == 0.0 and s[1] > 0]
        self.assertTrue(south and west)
        self.assertLessEqual(max(s[0] for s in south), 0.03)
        self.assertLessEqual(max(s[1] for s in west), 0.03)
        self.assertEqual({s[2] for s in south}, {100.9})
        self.assertEqual({s[2] for s in west}, {100.0})

    def test_a_neighbour_that_falls_away_from_the_edge_is_read_where_it_meets_it(self):
        # the north model's terrain falls up to 1 m per metre away from where it was cut (its edge
        # faces were tucked 12 cm under the main model's): read 0.3 m out, the new ground's edge
        # stood 0.2 m under the neighbour along the west strip and Webster (sw17 tiles). Tiles cut
        # by supersede end exactly on the outline, so the reading is taken just outside it
        fall = [[(-5, -5, 95), (25, -5, 95), (25, 0, 100)],
                [(-5, -5, 95), (25, 0, 100), (-5, 0, 100)]]  # fmt: skip
        got = edge.sample(FOOT, np.array(fall, float))
        south = [s for s in got if s[1] == 0.0 and 0 < s[0] < 20]
        self.assertTrue(south)
        for s in south:
            self.assertGreater(s[2], 99.9)

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
