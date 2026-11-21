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

    def test_a_narrow_strip_down_a_slope_follows_it_to_its_end(self):
        # a drive 3 m wide climbing 0.1 m per m northward, ending in soft ground at y 60: its end
        # has paved cells on one side only and must not take their (higher) mean
        def f(x, y):
            return 100 + 0.1 * y

        drive = [(98.5, 20), (101.5, 20), (101.5, 60), (98.5, 60)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), paved=[drive])
        y = np.arange(20.5, 60.0, 1.0)
        got = t.surface(np.full(len(y), 100.0), y, np.ones(len(y), bool))
        np.testing.assert_allclose(got, f(100, y), atol=0.04)

    def test_a_walk_ending_at_the_footprint_edge_follows_the_slope_there(self):
        # a walk 1.6 m wide running down 0.12 m per m to the footprint edge at y 0, where the
        # ground runs on outside (another model's road)
        def f(x, y):
            return 100 + 0.12 * y

        walk = [(49.2, 0), (50.8, 0), (50.8, 30), (49.2, 30)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), footprint=FOOT, paved=[walk])
        y = np.array([0.1, 1.0, 2.0, 5.0, 15.0])
        got = t.surface(np.full(len(y), 50.0), y, np.ones(len(y), bool))
        np.testing.assert_allclose(got, f(50, y), atol=0.04)

    def test_a_wide_lot_on_noisy_ground_stays_smooth_to_its_edges(self):
        # the grading still takes the LiDAR noise out, also along a lot's edge and in its corners
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), paved=[[(40, 20), (90, 20), (90, 70), (40, 70)]])
        xs, ys = np.meshgrid(np.arange(40.5, 90.0, 1.0), np.arange(20.5, 70.0, 1.0))
        x, y = xs.ravel(), ys.ravel()
        road = t.surface(x, y, np.ones(len(x), bool)) - (100 - 0.02 * x)
        soft = t.surface(x, y, np.zeros(len(x), bool)) - (100 - 0.02 * x)
        self.assertLess(np.abs(road).max(), 0.03)
        self.assertLess(road.std(), soft.std() / 2)
        # a plane fitted at the rim leans on fewer cells than in the middle: a little less smooth
        # there, but still well under the soft ground's noise and without the mean's lean
        rim = (np.minimum(x - 40, 90 - x) < 2) | (np.minimum(y - 20, 70 - y) < 2)
        self.assertLess(road[rim].std(), 0.7 * soft[rim].std())

    def test_paving_on_another_level_nearby_does_not_tilt_a_road(self):
        # a walk on top of a 5 m bank, 6 m from the road's edge: both are paved, but the road's
        # grade comes from the road
        def f(x, y):
            return 100 + 5 / (1 + np.exp(-(y - 55) / 0.5))

        walk = [(10, 58), (190, 58), (190, 61), (10, 61)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), paved=[ROAD, walk])
        x = np.arange(20.0, 180.0, 5.0)
        for y, want in ((51.5, 100.0), (46.0, 100.0), (59.5, 105.0)):
            got = t.surface(x, np.full(len(x), y), np.ones(len(x), bool))
            np.testing.assert_allclose(got, want, atol=0.05)

    def test_paving_under_a_stand_keeps_the_plain_mean(self):
        # under a stand's void the LiDAR ground is filled in: the grade there stays the masked mean
        # of the paving round it, as before the plane fit
        void = [(90, 42), (110, 42), (110, 50), (90, 50)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), paved=[ROAD], voids=[void])
        i, j = int(100 - t.x0), int(t.y1 - 46)
        mask = np.zeros_like(t.base, bool)
        cx = t.x0 + np.arange(t.base.shape[1]) + 0.5
        cy = t.y1 - np.arange(t.base.shape[0]) - 0.5
        gx, gy = np.meshgrid(cx, cy)
        mask[(gx > 10) & (gx < 190) & (gy > 40) & (gy < 52)] = True
        want = terrain._masked_blur(t.base, mask, terrain.GRADE)[j, i]
        self.assertAlmostEqual(t.graded[j, i], want, places=6)

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

    def test_edge_samples_are_not_averaged_across_a_step_in_the_neighbour(self):
        # the neighbour's ground steps up 1 m at x 100 (a skirt, then another model's sidewalk):
        # two meshes, two runs, each met at its own height up to the step
        samples = [[x, 0.0, 99.0 if x < 100 else 100.0] for x in range(0, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_file(d), edge=samples, footprint=FOOT, paved=[ROAD])
        z = t.neighbour_z(np.array([98.0, 99.0, 100.0, 101.0]), np.zeros(4))
        np.testing.assert_allclose(z, [99.0, 99.0, 100.0, 100.0], atol=0.02)

    def test_a_coarse_neighbours_bend_is_kept(self):
        # a coarse neighbour that ignores the 2 m bumps of the ground (so it is met as heights)
        # falls 0.1 m per m both ways from x 100: its own heights are smooth already, so a short
        # run keeps the bend within 0.2 m
        def f(x, y):
            return 100 + 2 * np.sin(x / 2)

        samples = [[x, 0.0, 100.0 - 0.1 * abs(x - 100)] for x in range(0, 200)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT)
        self.assertFalse(t.relative[100])
        self.assertAlmostEqual(t.neighbour_z(np.array([100.0]), np.zeros(1))[0], 100.0, delta=0.2)

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


# a road 20 m wide that crosses the south edge of FOOT and runs on north into the area
CUT = [(90, 0), (110, 0), (110, 70), (90, 70)]


def cut_samples(z):
    """The neighbour's ground along the south edge, every metre: `z` metres, flat (a coarse
    far-field ground that does not follow the LiDAR)."""
    return [[x, 0.0, z] for x in range(0, 201)]


@unittest.skipIf(np is None, "numpy is not installed")
class RoadCuts(unittest.TestCase):
    def test_outward_normals_of_a_ring_either_way_round(self):
        x, y = np.array([50.0, 200.0, 100.0, 0.0]), np.array([0.0, 50.0, 100.0, 30.0])
        want = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        for ring in (FOOT, FOOT[::-1]):
            np.testing.assert_allclose(terrain._normals(ring, x, y), want, atol=1e-9)

    def test_the_lidar_step_across_an_edge(self):
        # a plane sloping across the edge has no step; a 2 m wall on the edge has a 2 m step;
        # where the LiDAR does not reach past the edge the step is not known
        def wall(x, y):
            return 100 + 0.05 * y + 2 / (1 + np.exp(y / 0.2))

        x, y = np.array([50.0, 150.0]), np.zeros(2)
        n = np.array([[0.0, -1.0], [0.0, -1.0]])
        with tempfile.TemporaryDirectory() as d:
            plane = terrain.Terrain(lidar_from(d, lambda x, y: 100 + 0.05 * y))
            walled = terrain.Terrain(lidar_from(d, wall))
            short = terrain.Terrain(lidar_file(d))
        np.testing.assert_allclose(plane.step_across(x, y, n), 0.0, atol=0.05)
        # read from the soft ground, blurred over 1 m: a wall shows at about nine tenths
        np.testing.assert_allclose(walled.step_across(x, y, n), 1.8, atol=0.15)
        self.assertTrue(np.isnan(short.step_across(x, y, n)).all())

    def test_a_road_ramps_up_to_a_coarse_neighbour_the_lidar_does_not_see(self):
        # the LiDAR runs on level across the edge (the road goes on); the neighbour's coarse
        # ground lies 1.5 m above it: no step at the cut, a ramp no steeper than RAMP_GRADE
        # (smoothstep: 1.5 times the mean slope at most), and the road's own grade past it
        def f(x, y):
            return 100 + 0.01 * x

        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(
                lidar_from(d, f), edge=cut_samples(102.0), footprint=FOOT, paved=[CUT], roads=[CUT]
            )
        y = np.arange(0.1, 50.0, 0.5)
        x = np.full(len(y), 100.0)
        got = t.surface(x, y, np.ones(len(y), bool))
        np.testing.assert_allclose(t.surface(x, y, True), got)  # one flag for all (the curbs)
        self.assertAlmostEqual(got[0], 102.0, delta=0.1)
        # a ground vertex on the outline lies on the road's own edge too: it meets as well
        on_edge = t.surface(np.array([100.0, 110.0]), np.array([0.0, 0.0]), np.ones(2, bool))
        np.testing.assert_allclose(on_edge, 102.0, atol=0.1)
        self.assertLess(np.abs(np.diff(got) / 0.5).max(), 1.6 * terrain.RAMP_GRADE)
        far = y > terrain.RAMP_MAX + 1
        np.testing.assert_allclose(got[far], f(x[far], y[far]), atol=0.04)
        # the lawn 2 m beside the road ramps with it, past the 4 m soft-ground bend
        lawn = t.surface(np.array([88.0]), np.array([10.0]), np.zeros(1, bool))[0]
        self.assertGreater(lawn, f(88.0, 10.0) + 0.2)

    def test_only_paving_marked_road_ramps_and_it_may_ramp_down(self):
        # without "road": true paving keeps the old rule (meets only within SEAM), up or down;
        # a road ramps to the neighbour either way
        def f(x, y):
            return 100 + 0.01 * x

        x, y = np.array([100.0, 100.0]), np.array([0.1, 10.0])
        on = np.ones(2, bool)
        with tempfile.TemporaryDirectory() as d:
            path = lidar_from(d, f)
            for z in (99.0, 102.0):
                lot = terrain.Terrain(path, edge=cut_samples(z), footprint=FOOT, paved=[CUT])
                np.testing.assert_allclose(lot.surface(x, y, on), f(x, y), atol=0.04)
            road = terrain.Terrain(
                path, edge=cut_samples(99.0), footprint=FOOT, paved=[CUT], roads=[CUT]
            )
        got = road.surface(x, y, on)
        self.assertAlmostEqual(got[0], 99.0, delta=0.1)
        self.assertLess(got[1], f(100.0, 10.0) - 0.2)  # still on its way down 10 m in
        self.assertGreater(got[1], 99.0)

    def test_a_wall_the_lidar_shows_keeps_its_step(self):
        # a 2 m wall on the edge, the yard behind it at the neighbour's height: paving does not
        # climb it (a bank face closes the step), soft ground still bends to it
        def f(x, y):
            return 100 + 2 / (1 + np.exp(y / 0.2))

        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(
                lidar_from(d, f), edge=cut_samples(102.0), footprint=FOOT, paved=[CUT], roads=[CUT]
            )
        x, y = np.array([100.0, 100.0]), np.array([0.3, 3.0])
        np.testing.assert_allclose(t.surface(x, y, np.ones(2, bool)), 100.0, atol=0.15)
        self.assertGreater(t.surface(x[:1], y[:1], np.zeros(1, bool))[0], 101.5)

    def test_a_neighbour_against_the_lidars_step_is_not_met(self):
        # the LiDAR falls 1 m outside the edge (a bank down to a pond) and the coarse neighbour
        # lies 0.4 m over the lot: the LiDAR shows a real step there, so the lot keeps its grade
        # (a bank face closes the step; the neighbour is wrong, not the lot)
        def f(x, y):
            return 100 - 1 / (1 + np.exp(y / 0.2))

        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(
                lidar_from(d, f), edge=cut_samples(100.4), footprint=FOOT, paved=[CUT], roads=[CUT]
            )
        got = t.surface(np.array([100.0]), np.array([0.3]), np.ones(1, bool))
        self.assertAlmostEqual(got[0], 100.0, delta=0.1)

    def test_a_neighbour_that_follows_the_lidar_is_met_as_before(self):
        # an edge with no step at all: nothing moves, paved or not
        def f(x, y):
            return 100 + 0.01 * x + 0.02 * y

        samples = [[x, 0.0, float(f(x, 0.0))] for x in range(0, 201)]
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(lidar_from(d, f), edge=samples, footprint=FOOT, paved=[CUT])
        y = np.arange(0.1, 40.0, 2.0)
        x = np.full(len(y), 100.0)
        np.testing.assert_allclose(t.surface(x, y, np.ones(len(y), bool)), f(x, y), atol=0.04)


if __name__ == "__main__":
    unittest.main()
