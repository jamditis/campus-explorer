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


def lidar_from(folder, f):
    """Ground returns of the surface f(x, y), 3 cm noise, reaching 20 m past the footprint FOOT
    (the evidence is fetched beyond an area's footprint)."""
    rng = np.random.default_rng(11)
    x, y = rng.uniform(-20, 220, 120000), rng.uniform(-20, 120, 120000)
    z = f(x, y) + rng.normal(0, 0.03, len(x))
    pts = np.c_[x, y, z, np.full(len(x), 2), np.ones(len(x)), np.ones(len(x))].astype("f8")
    path = Path(folder) / "lidar.npz"
    np.savez(path, pts=pts, box=np.array([-20, -20, 220, 120, 0.5]))
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

    def test_an_edge_with_no_samples_keeps_its_own_ground(self):
        # samples only along the south edge, 5 m above the ground: the north edge (shared with
        # another scripted area, so it has none) must not take a height from 100 m away
        samples = [[x, 0.0, 105.0] for x in range(0, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), edge=samples, footprint=FOOT, paved=[ROAD])
        x, y = np.array([50.0, 150.0]), np.array([99.8, 99.8])
        soft = t.surface(x, y, np.zeros(2, bool))
        np.testing.assert_allclose(soft, 100 - 0.02 * x, atol=0.1)
        south = t.surface(x, np.array([0.2, 0.2]), np.zeros(2, bool))
        np.testing.assert_allclose(south, 105.0, atol=0.3)  # the sampled edge still blends

    def test_edge_samples_are_not_averaged_across_a_gap(self):
        # two runs of samples at different levels with a gap between them (x 60 to 140)
        samples = [[x, 0.0, 99.0] for x in range(0, 60)] + [[x, 0.0, 96.0] for x in range(140, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), edge=samples, footprint=FOOT, paved=[ROAD])
        z = t.neighbour_z(np.array([58.0, 142.0]), np.array([0.0, 0.0]))
        np.testing.assert_allclose(z, [99.0, 96.0], atol=0.01)

    def test_a_run_of_samples_that_ends_on_a_slope_keeps_its_end_value(self):
        # the neighbour lies 0.5 m over a ground rising 0.3 m per m eastward; its samples stop at
        # x 59 and start again at x 140 (a stretch dropped at a shared edge or a free-edge ring)
        def f(x, y):
            return 100 + 0.3 * x

        xs = list(range(0, 60)) + list(range(140, 200))
        samples = [[x, 0.0, f(x, 0) + 0.5] for x in xs]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT)
        x = np.array([59.0, 58.0, 140.0, 141.0])
        z = t.neighbour_z(x, np.zeros(4))
        np.testing.assert_allclose(z, f(x, 0) + 0.5, atol=0.04)

    def test_the_edge_follows_real_relief_along_it(self):
        # a bank rising 3 m to a bridge end at x 100, and a cross-slope of 0.3 m per m from about
        # x 150 (eased in over a few metres): the neighbour's ground is the LiDAR's; the blended
        # edge follows it at every sample
        def f(x, y):
            ramp = 3 * np.logaddexp(0, (x - 150) / 3)  # 0 before x 140, x - 150 after x 160
            return 100 + 3 * np.exp(-(((x - 100) / 10) ** 2)) + 0.3 * ramp

        samples = [[x, 0.0, float(f(x, 0))] for x in range(0, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT)
        x = np.arange(5.0, 195.0, 1.0)
        got = t.surface(x, np.full(len(x), 0.05), np.zeros(len(x), bool))
        np.testing.assert_allclose(got, f(x, 0), atol=0.05)

    def test_a_sample_round_a_corner_sets_no_flat_height_on_a_shared_edge(self):
        # the ground rises 0.3 m per m eastward; the west edge (another model, on the LiDAR) has
        # samples, the south edge is shared with another scripted area and has none: 3 to 5 m
        # along it the ground keeps its own height, not the corner sample's
        def f(x, y):
            return 100 + 0.3 * x

        samples = [[0.0, y, f(0, y)] for y in range(0, 101)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT)
        x = np.array([3.0, 4.0, 5.0])
        got = t.surface(x, np.full(3, 0.2), np.zeros(3, bool))
        np.testing.assert_allclose(got, f(x, 0), atol=0.06)

    def test_a_coarse_neighbour_that_ignores_the_relief_is_met_at_its_own_height(self):
        # a coarse skirt lies flat at 100 m over ground with 2 m bumps every 12 m: its offset from
        # the LiDAR swings by 4 m along the run, so it is met as a height, not as an offset
        def f(x, y):
            return 100 + 2 * np.sin(x / 2)

        samples = [[x, 0.0, 100.0] for x in range(0, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT)
        x = np.arange(5.0, 195.0, 1.0)
        got = t.surface(x, np.full(len(x), 0.05), np.zeros(len(x), bool))
        np.testing.assert_allclose(got, 100.0, atol=0.05)

    def test_a_sample_over_a_void_keeps_its_own_height(self):
        # under a stand (a void) the LiDAR has no ground: there the neighbour's height is used as
        # it is, not as an offset from ground filled in from round the stand
        def f(x, y):
            return 100 + 0.3 * y

        void = [(40, -5), (60, -5), (60, 10), (40, 10)]
        samples = [[x, 0.0, 104.0] for x in range(0, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT, voids=[void])
        z = t.neighbour_z(np.array([50.0, 50.0, 150.0]), np.array([0.0, 3.0, 3.0]))
        self.assertAlmostEqual(z[0], 104.0, delta=0.01)
        self.assertAlmostEqual(z[1], 104.0, delta=0.01)  # as today: the sample's own height
        self.assertAlmostEqual(z[2], 104.0 + 0.9, delta=0.05)  # elsewhere: LiDAR plus offset

    def test_a_lift_is_full_inside_its_ring_and_gone_past_its_feather(self):
        lift = dict(ring=[(90, 0), (110, 0), (110, 100), (90, 100)], dz=0.65, feather=10.0)
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), lifts=[lift])
        got = t.lift(np.array([100.0, 115.0, 121.0]), np.array([50.0, 50.0, 50.0]))
        self.assertAlmostEqual(got[0], 0.65)
        self.assertAlmostEqual(got[1], 0.325, places=3)  # half way through the feather
        self.assertEqual(got[2], 0.0)

    def test_a_cap_holds_the_ground_under_a_bowl_and_leaves_the_rest(self):
        # a stepped top over x 90..110: 98.0 m west of x = 100, 99.5 m east of it; ground ~98 m
        ring = [(90, 20), (110, 20), (110, 80), (90, 80)]

        def top(x, y):
            return np.where(np.asarray(x) < 100, 98.0, 99.5)

        with tempfile.TemporaryDirectory() as d:
            plain = terrain.Terrain(lidar_file(d))
            capped = terrain.Terrain(lidar_file(d), caps=[dict(ring=ring, top=top)])
        x = np.array([95.0, 105.0, 90.0, 110.0, 85.0, 100.0])
        y = np.array([50.0, 50.0, 50.0, 50.0, 50.0, 85.0])
        free = plain.surface(x, y, np.zeros(6, bool))
        got = capped.surface(x, y, np.zeros(6, bool))
        # inside and on the ring: never above the top less the gap, otherwise as it was
        self.assertLessEqual(got[0], 98.0 - terrain.CAP_GAP + 1e-9)
        self.assertAlmostEqual(got[1], min(free[1], 99.5 - terrain.CAP_GAP))
        self.assertLessEqual(got[2], 98.0 - terrain.CAP_GAP + 1e-9)  # on the west side
        self.assertLessEqual(got[3], 99.5 - terrain.CAP_GAP + 1e-9)  # on the east side
        # outside the ring nothing changes: no feather lowers the concourse round a bowl
        np.testing.assert_allclose(got[4:], free[4:])
        # the ground outside keeps its own height on the outline too: the uncapped heights, and
        # which triangles (by their centres) take the capped ones
        np.testing.assert_allclose(capped.surface(x, y, np.zeros(6, bool), capped=False), free)
        inside = capped.under_caps(np.array([95.0, 89.0, 100.0]), np.array([50.0, 50.0, 81.0]))
        self.assertEqual(inside.tolist(), [True, False, False])


if __name__ == "__main__":
    unittest.main()
