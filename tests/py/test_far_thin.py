"""Far-field trees thinned with distance (tools/web-export/far_thin.py)."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "web-export"))

import far_thin  # noqa: E402

# one pixel at the walk view's 68 degree field of view on a 1080 px screen
PX = math.radians(68 / 1080)


def grove(dist, n=2000, r=3.8, h=20.0):
    """n trees spread along a 400 m strip at `dist` metres east of the origin (three.js axes)."""
    return [(dist + (i % 40) * 10.0, 120.0, (i // 40) * 8.0, r, h) for i in range(n)]


class FarThin(unittest.TestCase):
    def test_near_trees_stay_as_they_are(self):
        trees = grove(500)
        self.assertEqual(far_thin.thin(trees), trees)

    def test_far_trees_keep_their_covered_area_and_look_four_pixels_wide(self):
        trees = grove(2500)
        kept = far_thin.thin(trees)
        self.assertLess(len(kept), len(trees) * 0.7)
        area = sum(r * r for *_, r, _ in trees)
        self.assertAlmostEqual(sum(r * r for *_, r, _ in kept) / area, 1.0, delta=0.1)
        for x, _, z, r, _ in kept:
            self.assertAlmostEqual(2 * r / math.hypot(x, z), 4 * PX, delta=1e-6)

    def test_deterministic_and_a_second_run_changes_nothing(self):
        trees = grove(2200) + grove(900)
        once = far_thin.thin(trees)
        self.assertEqual(once, far_thin.thin(trees))
        self.assertEqual(far_thin.thin(once), once)

    def test_kept_trees_are_whole_rows_of_the_input(self):
        trees = grove(2600)
        by_pos = {(x, z): t for t in trees for x, _, z, *_ in [t]}
        for x, y, z, r, h in far_thin.thin(trees):
            src = by_pos[(x, z)]
            self.assertEqual((y, h), (src[1], src[4]))
            self.assertGreaterEqual(r, src[3])

    def test_a_crown_never_grows_past_what_the_tree_height_allows(self):
        kept = far_thin.thin(grove(2600, h=10.0))
        self.assertTrue(kept)
        for *_, r, h in kept:
            self.assertLessEqual(r, far_thin.MAX_R_OF_H * h + 1e-9)


if __name__ == "__main__":
    unittest.main()
