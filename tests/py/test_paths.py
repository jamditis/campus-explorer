"""The pure parts of tools/places/build_paths.py: which ways are walkable, slope, shapes."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "places"))

import build_paths as bpaths  # noqa: E402


class Walkable(unittest.TestCase):
    def test_footways_steps_and_streets(self):
        self.assertEqual(bpaths.walkable({"highway": "footway"}), 0)
        self.assertEqual(bpaths.walkable({"highway": "steps"}), 1)
        self.assertEqual(bpaths.walkable({"highway": "service"}), 4)
        self.assertEqual(bpaths.walkable({"highway": "footway", "footway": "crossing"}), 8)
        self.assertEqual(bpaths.walkable({"highway": "footway", "incline": "12%"}), 2)

    def test_no_indoor_private_or_motorway(self):
        # AGENTS.md rule 16: nothing indoor is routed
        self.assertIsNone(bpaths.walkable({"highway": "corridor"}))
        self.assertIsNone(bpaths.walkable({"highway": "footway", "indoor": "yes"}))
        self.assertIsNone(bpaths.walkable({"highway": "footway", "level": "2"}))
        self.assertIsNone(bpaths.walkable({"highway": "service", "access": "private"}))
        self.assertIsNone(bpaths.walkable({"highway": "trunk"}))
        self.assertIsNone(bpaths.walkable({"highway": "cycleway"}))


class Slope(unittest.TestCase):
    def test_window_ignores_one_bad_cell(self):
        pts = [(i * 10.0, 0.0) for i in range(5)]
        # a level path with one 3 m spike (a wall in the DEM): over 20 m that reads 15 %, not 30 %
        self.assertAlmostEqual(bpaths.steepest(pts, [100, 100, 103, 100, 100]), 15.0)
        # a steady 10 % ramp
        self.assertAlmostEqual(bpaths.steepest(pts, [100, 101, 102, 103, 104]), 10.0)

    def test_short_edge_measured_end_to_end(self):
        # 4 m with a 1.15 m rise is 28.75 %; under 2 m counts as level; a missing height is unknown
        self.assertAlmostEqual(bpaths.steepest([(0.0, 0.0), (4.0, 0.0)], [100, 101.15]), 28.75)
        self.assertEqual(bpaths.steepest([(0.0, 0.0), (1.5, 0.0)], [100, 101]), 0.0)
        self.assertIsNone(bpaths.steepest([(0.0, 0.0), (4.0, 0.0)], [100, None]))

    def test_end_window_reaches_the_last_sample(self):
        # samples at 0, 10, 20, 25 m: the 3 m rise at the end is 12 % over the last 25 m
        pts = [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (25.0, 0.0)]
        self.assertAlmostEqual(bpaths.steepest(pts, [100, 100, 100, 103]), 12.0)

    def test_split_edge_part_way(self):
        nodes = [(0.0, 0.0), (100.0, 0.0)]
        edges = [[0, 1, 0, 3]]
        self.assertEqual(bpaths.split_edge(nodes, edges, 0, 0.4), 2)
        self.assertEqual(nodes[2], (40.0, 0.0))
        self.assertEqual(edges, [[0, 2, 0, 3], [2, 1, 0, 3]])
        self.assertEqual(bpaths.split_edge(nodes, edges, 0, 0.001), 0)

    def test_resample_keeps_ends(self):
        s = bpaths.resample([(0.0, 0.0), (25.0, 0.0)], 10.0)
        self.assertEqual(s, [(0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (25.0, 0.0)])


class Shapes(unittest.TestCase):
    def test_simplify_drops_straight_points(self):
        pts = [(0, 0), (5, 0.1), (10, 0), (10, 10)]
        self.assertEqual(bpaths.simplify(pts, 0.6), [0, 2, 3])

    def test_a_path_through_a_corner_enters(self):
        square = [(0, 0), (10, 0), (10, 10), (0, 10)]
        hall = ((0, 10, 0, 10), [square], [])
        # cuts the corner: middle outside the square, but it crosses two walls
        self.assertTrue(bpaths.enters((-2, 4), (4, -2), hall))
        # ends at the wall (a door): not inside
        self.assertFalse(bpaths.enters((-5, 5), (0, 5), hall))
        # a path inside a courtyard (inner ring) is outdoors
        yard = [(4, 4), (6, 4), (6, 6), (4, 6)]
        self.assertFalse(bpaths.enters((4.5, 5), (5.5, 5), ((0, 10, 0, 10), [square], [yard])))

    def test_inside(self):
        square = [(0, 0), (10, 0), (10, 10), (0, 10)]
        self.assertTrue(bpaths.inside((5, 5), square))
        self.assertFalse(bpaths.inside((15, 5), square))


class Published(unittest.TestCase):
    def test_paths_json_is_consistent(self):
        d = json.loads((ROOT / "viewer" / "paths.json").read_text())
        n = len(d["nodes"]) // 2
        self.assertEqual(len(d["nodes"]) % 2, 0)
        for a, b, flags, grade in d["edges"]:
            self.assertTrue(0 <= a < n and 0 <= b < n and a != b)
            self.assertEqual(flags & ~15, 0)
            self.assertGreaterEqual(grade, -1)  # -1: no DEM height there
        places = json.loads((ROOT / "viewer" / "places.json").read_text())["places"]
        osm = {p["osm"] for p in places}
        for e in d["entrances"]:
            self.assertIn(e["osm"], osm)
            self.assertTrue(0 <= e["node"] < n)


if __name__ == "__main__":
    unittest.main()
