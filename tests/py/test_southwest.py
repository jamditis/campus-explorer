"""Unit tests for the pure parts of the southwest build: plan geometry, the plan files, the layout.

Run with `python3 -m unittest discover -s tests/py` (no Blender, no third-party packages).
"""

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import geom  # noqa: E402
import layout  # noqa: E402

PLAN = ROOT / "blender" / "scripted" / "southwest"


class Geometry(unittest.TestCase):
    def test_fillet_is_a_true_arc(self):
        # a 10 m square with 2 m corners: every arc point is 2 m from its corner's centre
        ring = geom.expand([[0, 0, 2], [10, 0, 2], [10, 10, 2], [0, 10, 2]], True)
        centres = [(2, 2), (8, 2), (8, 8), (2, 8)]
        for x, y in ring:
            on_run = min(abs(x), abs(x - 10), abs(y), abs(y - 10)) < 1e-9
            on_arc = any(abs(math.hypot(x - cx, y - cy) - 2) < 1e-9 for cx, cy in centres)
            self.assertTrue(on_run or on_arc, (x, y))
        # the polyline stays within the chord tolerance of the exact area
        self.assertAlmostEqual(geom.area(ring), 100 - (4 - math.pi) * 4, delta=0.1)

    def test_fillet_that_does_not_fit_is_an_error(self):
        with self.assertRaises(ValueError):
            geom.expand([[0, 0], [1, 0, 5], [1, 1]], False)

    def test_two_fillets_that_overlap_on_one_run_are_an_error(self):
        # each 4 m radius fits its own corner; together they need 8 m of the 6 m run between them
        with self.assertRaises(ValueError):
            geom.expand([[0, 0], [10, 0, 4], [10, 6, 4], [0, 6]], False)
        geom.expand([[0, 0], [10, 0, 3], [10, 6, 3], [0, 6]], False)  # 3 + 3 fits exactly

    def test_open_path_keeps_its_ends(self):
        line = geom.expand([[0, 0, 3], [10, 0, 3], [10, 10, 3]], False)
        self.assertEqual(line[0], (0, 0))
        self.assertEqual(line[-1], (10, 10))

    def test_offset_of_a_straight_run_is_parallel(self):
        self.assertEqual(geom.offset([(0, 0), (10, 0)], 2), [(0, 2), (10, 2)])
        self.assertEqual(geom.offset([(0, 0), (10, 0)], -2), [(0, -2), (10, -2)])

    def test_ribbon_has_the_width_asked_for(self):
        ring = geom.ribbon([[0, 0], [20, 0]], 3)
        self.assertAlmostEqual(abs(geom.area(ring)), 60, places=6)

    def test_inside(self):
        square = [(0, 0), (4, 0), (4, 4), (0, 4)]
        self.assertTrue(geom.inside(square, 2, 2))
        self.assertFalse(geom.inside(square, 5, 2))

    def test_stalls_give_one_more_line_than_stalls(self):
        m = {"line": [[0, 0], [27, 0]], "count": 10, "depth": 5.5, "side": "left"}
        lines = geom.stalls(m)
        self.assertEqual(len(lines), 11)
        for a, b in lines:
            self.assertAlmostEqual(b[1] - a[1], 5.5)  # left of +x is +y
            self.assertAlmostEqual(b[0], a[0])
        right = geom.stalls({**m, "side": "right"})
        self.assertAlmostEqual(right[0][1][1], -5.5)

    def test_dashes(self):
        parts = geom.dashes([(0, 0), (10, 0)], 3, 2)
        self.assertEqual([(round(p[0][0], 6), round(p[-1][0], 6)) for p in parts], [(0, 3), (5, 8)])

    def test_sheets_cover_the_surface_and_split_long_ones(self):
        ring = [(0, 0), (250, 0), (250, 12), (0, 12)]
        sheets = geom.sheets("p001", ring)
        self.assertEqual(len(sheets), 3)
        self.assertEqual(sheets[0]["cut0"], 0)
        self.assertAlmostEqual(sheets[-1]["cut1"], 250)
        for s in sheets:
            self.assertLessEqual(max(s["w"], s["h"]), 4096)
            self.assertLessEqual(s["u0"], s["cut0"] - 2.9)  # margin all round
            self.assertGreaterEqual(s["u1"], s["cut1"] + 2.9)

    def test_frame_round_trip(self):
        to_local, to_model = geom.frame((10, 20), 30)
        x, y = to_model(*to_local(3.5, -7.25))
        self.assertAlmostEqual(x, 3.5)
        self.assertAlmostEqual(y, -7.25)


class Paint(unittest.TestCase):
    def test_paint_goes_to_the_surface_you_see(self):
        # a walk whose outline contains the field, and the turf lying over it
        walk = dict(kind="asphalt", ring=[(0, 0), (100, 0), (100, 60), (0, 60)], holes=[])
        turf = dict(kind="turf", ring=[(10, 10), (90, 10), (90, 50), (10, 50)], holes=[])
        lawn = dict(kind="lawn", ring=[(200, 0), (220, 0), (220, 20), (200, 20)], holes=[])
        on_turf = dict(line=[(20, 30), (80, 30)], width=0.1, colour="white", field=True)
        on_lawn = dict(line=[(205, 10), (215, 10)], width=0.1, colour="white")
        self.assertEqual(layout.painted_surfaces([walk, turf, lawn], [on_turf, on_lawn]), {1})
        # a lane line on the walk itself, outside the turf
        on_walk = dict(line=[(2, 2), (2, 58)], width=0.1, colour="yellow")
        self.assertEqual(layout.painted_surfaces([walk, turf, lawn], [on_walk]), {0})
        # football lines never paint asphalt, even where they overrun the turf
        overrun = dict(line=[(5, 30), (95, 30)], width=0.1, colour="white", field=True)
        self.assertEqual(layout.painted_surfaces([walk, turf, lawn], [overrun]), {1})


class PlanFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lay = layout.load(PLAN)

    def test_every_plan_file_is_json_with_a_zone(self):
        for f in PLAN.glob("*.json"):
            data = json.loads(Path(f).read_text())
            if f.name != "edge_heights.json":
                self.assertIn("zone", data, f.name)

    def test_footprint_and_surfaces_are_usable_outlines(self):
        self.assertGreater(abs(geom.area(self.lay["footprint"])), 10000)
        names = set()
        for s in self.lay["surfaces"]:
            self.assertIn(s["kind"], layout.LAYER, s["name"])
            self.assertGreaterEqual(len(s["ring"]), 3, s["name"])
            self.assertGreater(geom.area(s["ring"]), 0.5, s["name"])  # anticlockwise, not a sliver
            self.assertNotIn(s["name"], names, "surface names are unique")
            names.add(s["name"])
            for x, y in s["ring"]:
                self.assertTrue(math.isfinite(x) and math.isfinite(y), s["name"])

    def test_guesses_say_what_was_guessed(self):
        for group in ("surfaces", "curbs", "points", "stands", "fences"):
            for item in self.lay[group]:
                if "unverified" in item:
                    self.assertIsInstance(item["unverified"], str, item.get("name"))
                    self.assertGreater(len(item["unverified"]), 3, item.get("name"))
                self.assertTrue(
                    item.get("evidence") or item.get("unverified"),
                    f"{group}: {item.get('name')} names no source",
                )

    def test_only_paved_surfaces_carry_paint(self):
        for s in self.lay["surfaces"]:
            if s["sheets"]:
                self.assertIn(s["kind"], layout.PAINTABLE, s["name"])
                for sh in s["sheets"]:
                    # the web exporter refuses image names with these words in them
                    self.assertNotRegex(sh["name"], r"(?i)ortho|aerial|photo|mask|skirt|_far|joe")

    def test_football_field_follows_the_rule_book(self):
        ff = self.lay["field_frame"]
        lines = layout.football(ff)
        to_local = geom.frame(ff["centre"], ff["angle"])[0]
        us = sorted(
            {
                round(to_local(*m["line"][0])[0] / 0.9144)
                for m in lines
                if abs(to_local(*m["line"][0])[1]) > 24
            }
        )
        # goal line to goal line, a line every five yards, plus the two end lines at 60 yd
        for yard in range(-50, 51, 5):
            self.assertIn(yard, us)
        ends = [m for m in lines if abs(abs(to_local(*m["line"][0])[0]) - 60 * 0.9144) < 0.1]
        self.assertGreaterEqual(len(ends), 2)
        width = max(abs(to_local(*p)[1]) for m in lines for p in m["line"])
        self.assertAlmostEqual(width, 80 * 0.3048, places=3)  # 53 1/3 yd wide

    def test_edge_heights_lie_on_the_footprint(self):
        f = PLAN / "edge_heights.json"
        if not f.exists():
            self.skipTest("no edge samples yet")
        foot = self.lay["footprint"]
        for x, y, z in json.loads(Path(f).read_text())["samples"][::25]:
            d = min(math.hypot(x - a[0], y - a[1]) for a in geom.resample(foot, 1.0, True))
            self.assertLess(d, 1.01)
            self.assertTrue(90 < z < 160, "NAVD88 metres on this hillside")


if __name__ == "__main__":
    unittest.main()
