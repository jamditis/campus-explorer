"""Ground heights of the southwest build: paving is graded, soft ground follows the LiDAR.

Needs numpy (Blender has it; the test is skipped where it is missing).
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

try:
    import numpy as np
    import terrain
except ImportError:  # no numpy on this machine
    np = None

ROAD = [(10, 40), (190, 40), (190, 52), (10, 52)]
FOOT = [(0, 0), (200, 0), (200, 100), (0, 100)]


def lidar_file(folder, bank=0.0):
    """A 200 x 100 m plane falling 2% eastward, with 6 cm LiDAR noise; `bank` raises y above 52."""
    rng = np.random.default_rng(7)
    x, y = rng.uniform(0, 200, 60000), rng.uniform(0, 100, 60000)
    z = 100 - 0.02 * x + rng.normal(0, 0.06, len(x)) + np.where(y > 52, bank, 0.0)
    pts = np.c_[x, y, z, np.full(len(x), 2), np.ones(len(x)), np.ones(len(x))].astype("f4")
    path = Path(folder) / "lidar.npz"
    np.savez(path, pts=pts, box=np.array([0, 0, 200, 100, 0.5]))
    return path


@unittest.skipIf(np is None, "numpy is not installed")
class Grading(unittest.TestCase):
    def test_a_road_on_noisy_ground_comes_out_smooth(self):
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), paved=[ROAD])
        x = np.arange(20.0, 180.0, 1.0)
        y = np.full(len(x), 46.0)
        road = t.surface(x, y, np.ones(len(x), bool)) - (100 - 0.02 * x)
        soft = t.surface(x, y, np.zeros(len(x), bool)) - (100 - 0.02 * x)
        self.assertLess(np.abs(road).max(), 0.015)  # within 1.5 cm of the true grade
        self.assertLess(road.std(), soft.std() / 2)  # and clearly smoother than soft ground

    def test_a_bank_beside_a_road_does_not_lift_the_road(self):
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d, bank=1.5), paved=[ROAD])
        x = np.arange(20.0, 180.0, 2.0)
        edge = t.surface(x, np.full(len(x), 51.0), np.ones(len(x), bool)) - (100 - 0.02 * x)
        self.assertLess(np.abs(edge).max(), 0.05)  # 1 m from a 1.5 m bank, the road stays on grade

    def test_paving_meets_a_level_neighbour_but_not_a_bank(self):
        samples = [[x, 0.0, 99.0] for x in range(0, 200)]  # neighbour ground along the south edge
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), edge=samples, footprint=FOOT, paved=[ROAD])
        x, y = np.array([50.0, 150.0]), np.array([0.2, 0.2])
        truth = (
            100 - 0.02 * x
        )  # 99.0 at x 50 (level with the neighbour), 97.0 at x 150 (2 m below it)
        paved = t.surface(x, y, np.ones(2, bool))
        self.assertAlmostEqual(paved[0], 99.0, delta=0.05)
        self.assertAlmostEqual(paved[1], truth[1], delta=0.1)  # stays down: the neighbour is a bank
        soft = t.surface(x, y, np.zeros(2, bool))
        self.assertAlmostEqual(soft[1], 99.0, delta=0.1)  # soft ground rises to meet it

    def test_a_lift_is_full_inside_its_ring_and_gone_past_its_feather(self):
        lift = dict(ring=[(90, 0), (110, 0), (110, 100), (90, 100)], dz=0.65, feather=10.0)
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), lifts=[lift])
        got = t.lift(np.array([100.0, 115.0, 121.0]), np.array([50.0, 50.0, 50.0]))
        self.assertAlmostEqual(got[0], 0.65)
        self.assertAlmostEqual(got[1], 0.325, places=3)  # half way through the feather
        self.assertEqual(got[2], 0.0)


if __name__ == "__main__":
    unittest.main()
