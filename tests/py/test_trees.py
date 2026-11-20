"""Tree finding in a canopy height grid (tools/evidence/trees.py).

Needs numpy and Pillow (the test is skipped where they are missing; CI installs them).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "evidence"))

try:
    import numpy as np
    import trees
except ImportError:  # no numpy or Pillow on this machine
    np = None

CELL = 0.5


def crown(grid, x, y, height, radius, every=2):
    """A leaf-off crown: scattered returns on a dome, `every`th cell only."""
    for j in range(grid.shape[0]):
        for i in range(grid.shape[1]):
            d = ((i * CELL - x) ** 2 + (j * CELL - y) ** 2) ** 0.5
            if d <= radius and (i + j) % every == 0:
                grid[j, i] = max(grid[j, i], height * (1 - 0.5 * (d / radius) ** 2))


@unittest.skipIf(np is None, "numpy and Pillow are not installed")
class Peaks(unittest.TestCase):
    def test_two_trees_are_found_once_each_with_their_heights(self):
        g = np.zeros((120, 120))
        crown(g, 15, 15, 18.0, 5.0)
        crown(g, 40, 30, 12.0, 4.0)
        found = trees.peaks(g, CELL)
        self.assertEqual(len(found), 2)
        (j0, i0, z0), (j1, i1, z1) = found  # tallest first
        self.assertAlmostEqual(z0, 18.0, delta=0.5)
        self.assertAlmostEqual(z1, 12.0, delta=0.5)
        self.assertLess(abs(i0 * CELL - 15) + abs(j0 * CELL - 15), 2.5)
        self.assertLess(abs(i1 * CELL - 40) + abs(j1 * CELL - 30), 2.5)

    def test_a_pole_is_not_a_tree(self):
        g = np.zeros((80, 80))
        g[40, 40] = 11.0  # one tall return, nothing round it
        self.assertEqual(trees.peaks(g, CELL), [])

    def test_low_growth_and_missing_cells_are_ignored(self):
        g = np.full((80, 80), np.nan)
        crown(g, 20, 20, 3.0, 4.0)  # a shrub, below the 5 m limit
        self.assertEqual(trees.peaks(g, CELL), [])

    def test_fill_takes_values_from_neighbours(self):
        g = np.full((6, 6), 100.0)
        g[2:4, 2:4] = np.nan
        self.assertTrue(np.allclose(trees.fill(g), 100.0))


@unittest.skipIf(np is None, "numpy and Pillow are not installed")
class Existing(unittest.TestCase):
    def test_a_street_is_not_a_tree(self):
        for name in ("Tree_RedMaple_LOD1_v2Oct", "ShrubLeafCard", "Context tree crowns", "tree_12"):
            self.assertTrue(trees.is_vegetation(name), name)
        for name in ("MID_streets_20261015ae_me", "MID_streets_far_20261015ag_me", "Roads_asphalt"):
            self.assertFalse(trees.is_vegetation(name), name)


if __name__ == "__main__":
    unittest.main()
