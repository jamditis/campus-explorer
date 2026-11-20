"""Water in the scripted build: its layer, no paint, a level surface and a clean shore.

The terrain cases need numpy (Blender has it; they are skipped where it is missing).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))
sys.path.insert(0, str(ROOT / "tools" / "evidence"))

import layout  # noqa: E402

try:
    import numpy as np
    import terrain
except ImportError:  # no numpy on this machine
    np = None

SQUARE = [(0, 0), (20, 0), (20, 20), (0, 20)]


class Layer(unittest.TestCase):
    def test_water_lies_above_soft_ground_and_below_paving(self):
        water = layout.LAYER["water"]
        for soft in ("lawn", "mulch", "gravel"):
            self.assertLess(layout.LAYER[soft], water, soft)
        for paved in ("asphalt", "turf", "concrete", "brick"):
            self.assertGreater(layout.LAYER[paved], water, paved)

    def test_water_takes_no_paint(self):
        self.assertFalse(layout.paintable(dict(kind="water")))
        lot = dict(kind="asphalt", ring=[(-10, -10), (30, -10), (30, 30), (-10, 30)], holes=[])
        pond = dict(kind="water", ring=SQUARE, holes=[])
        line = dict(line=[(5, 10), (15, 10)], width=0.1, colour="white")
        # the line lies on the water, which is on top there: nothing gets a sheet
        self.assertEqual(layout.painted_surfaces([lot, pond], [line]), set())


class Validation(unittest.TestCase):
    def test_a_plain_water_surface_is_accepted(self):
        layout.check_surface(dict(name="Pond", kind="water", ring=SQUARE))
        layout.check_surface(dict(name="Pool", kind="water", ring=SQUARE, level=112.6))

    def test_water_with_paint_or_a_bad_level_is_an_error(self):
        with self.assertRaises(ValueError):
            layout.check_surface(dict(name="Pond", kind="water", ring=SQUARE, paint=True))
        with self.assertRaises(ValueError):
            layout.check_surface(dict(name="Pond", kind="water", ring=SQUARE, level="high"))
        with self.assertRaises(ValueError):
            layout.check_surface(dict(name="Pond", kind="water", ring=SQUARE, level=float("nan")))

    def test_a_level_belongs_to_water_only(self):
        with self.assertRaises(ValueError):
            layout.check_surface(dict(name="Lawn", kind="lawn", ring=SQUARE, level=99.0))

    def test_load_checks_the_plan(self):
        with tempfile.TemporaryDirectory() as d:
            plan = dict(
                zone="t_water",
                footprint=[[-50, -50], [50, -50], [50, 50], [-50, 50]],
                surfaces=[dict(name="Pond", kind="water", ring=SQUARE, paint=True)],
            )
            (Path(d) / "plan.json").write_text(json.dumps(plan))
            with self.assertRaises(ValueError):
                layout.load(d)


class Trees(unittest.TestCase):
    def test_no_tree_stands_in_water(self):
        import trees

        self.assertIn("water", trees.PAVED)


def basin_file(folder):
    """A 200 x 100 m field at 100 m with a pond 18 m across round (100, 50), its water at 98.0 m,
    and banks rising 1 m over 4 m outside it. 6 cm LiDAR noise; the water returns as flat ground.
    """
    rng = np.random.default_rng(11)
    x, y = rng.uniform(0, 200, 80000), rng.uniform(0, 100, 80000)
    r = np.hypot(x - 100, y - 50)
    z = np.where(r < 9, 98.0, 98.0 + np.clip((r - 9) / 4, 0, 1) * 2.0)
    z = z + rng.normal(0, 0.06, len(x)) * (r >= 9)
    pts = np.c_[x, y, z, np.full(len(x), 2), np.ones(len(x)), np.ones(len(x))].astype("f4")
    path = Path(folder) / "lidar.npz"
    np.savez(path, pts=pts, box=np.array([0, 0, 200, 100, 0.5]))
    return path


def circle(cx, cy, r, n=40):
    return [
        (cx + r * np.cos(2 * np.pi * i / n), cy + r * np.sin(2 * np.pi * i / n)) for i in range(n)
    ]


@unittest.skipIf(np is None, "numpy is not installed")
class Level(unittest.TestCase):
    def test_shore_level_reads_the_waterline_not_the_bank_or_one_low_return(self):
        samples = [98.0] * 12 + [98.6, 99.1, 99.5] * 9 + [96.0]  # one stray low return
        self.assertAlmostEqual(terrain.shore_level(samples), 98.0, delta=0.01)

    def test_a_traced_shore_gives_the_water_level(self):
        with tempfile.TemporaryDirectory() as d:
            t = terrain.Terrain(basin_file(d))
            on_line = t.water_level(circle(100, 50, 9))
            # a third of the trace drawn 1 m out onto the bank still reads the water
            ring = [
                (100 + (p[0] - 100) * (10 / 9), 50 + (p[1] - 50) * (10 / 9)) if i % 3 == 0 else p
                for i, p in enumerate(circle(100, 50, 9))
            ]
            drifted = t.water_level(ring)
        self.assertAlmostEqual(on_line, 98.0, delta=0.1)
        self.assertAlmostEqual(drifted, 98.0, delta=0.1)

    def test_flood_sets_every_vertex_of_a_water_triangle_to_its_level(self):
        # two triangles sharing an edge: 0 is water at 98.0, 1 is lawn
        z = np.array([98.3, 98.5, 98.4, 99.0])
        tris = np.array([[0, 1, 2], [1, 3, 2]])
        owner = np.array([5, -1])
        out = terrain.flood(z, tris, owner, {5: 98.0})
        # the shared shore vertices (1, 2) take the level: the lawn meets the water without a gap
        np.testing.assert_allclose(out, [98.0, 98.0, 98.0, 99.0])
        np.testing.assert_allclose(z, [98.3, 98.5, 98.4, 99.0])  # the input is left alone


if __name__ == "__main__":
    unittest.main()
