"""Unit tests for the pure parts of the scripted builds: plan geometry, the plan files, the layout.

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

SCRIPTED = ROOT / "blender" / "scripted"
PLAN = SCRIPTED / "southwest"


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


class Paintable(unittest.TestCase):
    def test_natural_grass_takes_paint_only_when_the_plan_says_so(self):
        ring = [(0, 0), (20, 0), (20, 20), (0, 20)]
        line = dict(line=[(2, 10), (18, 10)], width=0.1, colour="white")
        plain = dict(kind="lawn", ring=ring, holes=[], name="Lawn")
        field = dict(plain, paint=True, name="Ball_field")
        self.assertEqual(layout.painted_surfaces([plain], [line]), set())
        self.assertEqual(layout.painted_surfaces([field], [line]), {0})
        self.assertTrue(layout.paintable(dict(kind="gravel")))
        self.assertFalse(layout.paintable(dict(kind="concrete")))


class PlanFiles(unittest.TestCase):
    """Checks that hold for the plan files of every area."""

    @classmethod
    def setUpClass(cls):
        cls.areas = {d.name: layout.load(d) for d in layout.areas()}

    def each(self):
        return [(SCRIPTED / name, lay) for name, lay in self.areas.items()]

    def test_every_plan_file_is_json_with_a_zone_of_its_own(self):
        zones = {}
        for plan, _lay in self.each():
            for f in plan.glob("*.json"):
                data = json.loads(Path(f).read_text())
                if f.name != "edge_heights.json":
                    self.assertIn("zone", data, f.name)
                    # object names are made from the zone: two areas must not share one
                    self.assertNotIn(data["zone"], zones, f"{f} and {zones.get(data['zone'])}")
                    zones[data["zone"]] = f

    def test_footprint_and_surfaces_are_usable_outlines(self):
        for _plan, lay in self.each():
            if lay["footprint"] is None:
                self.assertTrue(lay["interiors"], "an area without ground holds interiors")
                continue
            self.assertGreater(abs(geom.area(lay["footprint"])), 10000)
            names = set()
            for s in lay["surfaces"]:
                self.assertIn(s["kind"], layout.LAYER, s["name"])
                self.assertGreaterEqual(len(s["ring"]), 3, s["name"])
                self.assertGreater(geom.area(s["ring"]), 0.5, s["name"])  # anticlockwise, no sliver
                self.assertNotIn(s["name"], names, "surface names are unique")
                names.add(s["name"])
                for x, y in s["ring"]:
                    self.assertTrue(math.isfinite(x) and math.isfinite(y), s["name"])

    def test_guesses_say_what_was_guessed(self):
        for _plan, lay in self.each():
            for group in ("surfaces", "curbs", "points", "stands", "fences", "buildings"):
                for item in lay[group]:
                    if "unverified" in item:
                        self.assertIsInstance(item["unverified"], str, item.get("name"))
                        self.assertGreater(len(item["unverified"]), 3, item.get("name"))
                    self.assertTrue(
                        item.get("evidence") or item.get("unverified"),
                        f"{group}: {item.get('name')} names no source",
                    )

    def test_only_paved_surfaces_carry_paint(self):
        for _plan, lay in self.each():
            for s in lay["surfaces"]:
                if s["sheets"]:
                    self.assertTrue(layout.paintable(s), s["name"])
                    for sh in s["sheets"]:
                        # the web exporter refuses image names with these words in them
                        self.assertNotRegex(
                            sh["name"], r"(?i)ortho|aerial|photo|mask|skirt|_far|joe"
                        )

    def test_edge_heights_lie_on_the_footprint(self):
        for plan, lay in self.each():
            f = plan / "edge_heights.json"
            if not f.exists():
                continue  # no edge samples yet
            foot = geom.resample(lay["footprint"], 1.0, True)
            for x, y, z in json.loads(Path(f).read_text())["samples"][::25]:
                d = min(math.hypot(x - a[0], y - a[1]) for a in foot)
                self.assertLess(d, 1.01)
                self.assertTrue(90 < z < 190, "NAVD88 metres on this hillside")


class Southwest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lay = layout.load(PLAN)

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

    def test_lacrosse_and_hockey_lines_follow_the_rule_book(self):
        plan = json.loads((PLAN / "field.json").read_text())
        ff = plan["field_frame"]
        to_local = geom.frame(ff["centre"], ff["angle"])[0]
        marks = {m["name"]: m for m in plan["markings"] if "name" in m}
        yd, ft = 0.9144, 0.3048

        def local(name, closed=False):
            return [to_local(*p) for p in geom.expand(marks[name]["path"], closed)]

        def assert_circle(name, cu, r):
            for u, v in local(name, True):
                self.assertAlmostEqual(math.hypot(u - cu, v), r, delta=0.02, msg=name)

        assert_circle("Lax_W_centre_circle", 0.0, 9.0)  # women: 9 m centre circle
        for end, s in (("N", 1), ("S", -1)):
            g = s * 50 * yd  # women's goals and the hockey back lines: on the football goal lines
            assert_circle(f"Lax_W_goal_circle_{end}", g, 2.6)
            assert_circle(f"Lax_M_crease_{end}", s * 40 * yd, 9 * ft)  # men: goals 80 yd apart
            for u, v in local(f"Lax_W_12m_fan_{end}"):  # 14.6 m semicircle, flat on the goal line
                on_line = abs(u - g) < 0.02 and 2.59 < abs(v) < 14.61
                self.assertTrue(on_line or abs(math.hypot(u - g, v) - 14.6) < 0.02, (u, v))
            for u, v in local(f"FH_circle_{end}"):  # 16 yd from the inside of the posts
                d = math.hypot(u - g, abs(v) - 2 * yd) if abs(v) > 2 * yd else abs(u - g)
                self.assertAlmostEqual(d, 16 * yd, delta=0.02)
            self.assertAlmostEqual(abs(local(f"Lax_M_end_line_{end}")[0][0]), 55 * yd, places=2)
        pitch = local("FH_pitch_outline", True)  # 100 x 60 yd
        self.assertAlmostEqual(max(u for u, _ in pitch), 50 * yd, places=2)
        self.assertAlmostEqual(max(v for _, v in pitch), 30 * yd, places=2)


class FreeEdges(unittest.TestCase):
    def test_a_sample_inside_a_free_edge_ring_does_not_count(self):
        lay = dict(free_edges=[[(0, 0), (4, 0), (4, 4), (0, 4)]])
        self.assertFalse(layout.meets_neighbour(lay, 2, 2))
        self.assertTrue(layout.meets_neighbour(lay, 6, 2))
        self.assertTrue(layout.meets_neighbour(dict(free_edges=[]), 2, 2))


if __name__ == "__main__":
    unittest.main()
