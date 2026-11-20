"""Unit tests for the marking types (arrows, crosswalks, words) and paint on a deck's roof.

Run with `python3 -m unittest discover -s tests/py` (no Blender, no third-party packages).
"""

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import geom  # noqa: E402
import layout  # noqa: E402


def extent(rings, angle):
    """(u0, u1, v0, v1) of every point of `rings` in a frame turned by `angle` degrees."""
    to_local = geom.frame((0.0, 0.0), angle)[0]
    pts = [to_local(*p) for r in rings for p in r]
    us, vs = [p[0] for p in pts], [p[1] for p in pts]
    return min(us), max(us), min(vs), max(vs)


class Arrows(unittest.TestCase):
    def rings(self, shape, at=(100.0, 50.0), angle=30.0):
        prims = layout.primitives(dict(type="arrow", at=list(at), angle=angle, shape=shape))
        self.assertTrue(all("ring" in p and p["colour"] == "white" for p in prims))
        return [[(x - at[0], y - at[1]) for x, y in p["ring"]] for p in prims]

    def test_through_arrow_has_the_standard_size_and_points_along_angle(self):
        u0, u1, v0, v1 = extent(self.rings("straight"), 30.0)
        self.assertAlmostEqual(u1 - u0, 3.0)  # tail to tip
        self.assertAlmostEqual(u0, -1.5)  # `at` is the middle of its length
        self.assertAlmostEqual(v1 - v0, 1.0)  # head width
        self.assertAlmostEqual(v0, -0.5)

    def test_turn_arrows_bend_to_their_side_and_mirror(self):
        _, _, lv0, lv1 = extent(self.rings("left"), 30.0)
        _, _, rv0, rv1 = extent(self.rings("right"), 30.0)
        self.assertGreater(lv1, 1.7)  # the head reaches 1.76 m left of the shaft
        self.assertLess(lv0, -0.1)
        self.assertAlmostEqual(lv1, -rv0)
        self.assertAlmostEqual(lv0, -rv1)

    def test_combined_arrow_is_longer_and_bends_one_way(self):
        u0, u1, v0, v1 = extent(self.rings("straight_right"), 30.0)
        self.assertAlmostEqual(u1 - u0, 4.0)
        self.assertLess(v0, -1.7)
        self.assertAlmostEqual(v1, 0.5)

    def test_unknown_shape_is_an_error(self):
        with self.assertRaises(ValueError):
            layout.primitives(dict(type="arrow", at=[0, 0], angle=0, shape="u_turn"))


class Crosswalks(unittest.TestCase):
    line = [[0.0, 0.0], [10.0, 0.0]]  # across a 10 m road; traffic runs along y

    def test_continental_bars_are_parallel_to_traffic_and_centred(self):
        prims = layout.primitives(dict(type="crosswalk", line=self.line, width=3.0))
        self.assertEqual(len(prims), 8)  # 0.6 m bars at 1.2 m centres in 10 m
        for p in prims:
            u0, u1, v0, v1 = extent([p["ring"]], 0.0)
            self.assertAlmostEqual(u1 - u0, 0.6)
            self.assertAlmostEqual(v1 - v0, 3.0)
        first, last = extent([prims[0]["ring"]], 0.0), extent([prims[-1]["ring"]], 0.0)
        self.assertAlmostEqual(first[0], 10.0 - last[1])  # the same margin at both kerbs

    def test_lines_are_two_transverse_lines_on_the_edges(self):
        prims = layout.primitives(dict(type="crosswalk", line=self.line, width=3.0, style="lines"))
        self.assertEqual(len(prims), 2)
        boxes = sorted(extent([p["ring"]], 0.0) for p in prims)
        self.assertEqual([(round(b[2], 6), round(b[3], 6)) for b in boxes][0], (-1.5, -1.2))
        for b in boxes:
            self.assertAlmostEqual(b[1] - b[0], 10.0)

    def test_ladder_is_both(self):
        prims = layout.primitives(
            dict(type="crosswalk", line=self.line, width=3.0, style="ladder", colour="yellow")
        )
        self.assertEqual(len(prims), 10)
        self.assertTrue(all(p["colour"] == "yellow" for p in prims))


class Words(unittest.TestCase):
    def test_text_keeps_its_place_and_marks_the_surface_under_it(self):
        (p,) = layout.primitives(dict(type="text", at=[5, 5], angle=90, text="STOP"))
        self.assertEqual((p["text"], p["height"], p["colour"]), ("STOP", 2.4, "white"))
        self.assertAlmostEqual(p["right_angle"], 0.0)  # read from the south: left to right is east
        u0, u1, v0, v1 = extent([p["box"]], 0.0)
        self.assertAlmostEqual(v1 - v0, 2.4)  # letters run up the lane
        self.assertAlmostEqual(u1 - u0, p["width"])
        road = dict(kind="asphalt", ring=[(0, 0), (10, 0), (10, 10), (0, 10)], holes=[])
        self.assertEqual(layout.painted_surfaces([road], [p]), {0})


class DeckRoof(unittest.TestCase):
    def test_a_deck_roof_gets_a_sheet_of_its_own(self):
        ring = [[0, 0], [60, 0], [60, 30], [0, 30]]
        plan = dict(
            zone="z",
            footprint=[[-10, -10], [80, -10], [80, 50], [-10, 50]],
            surfaces=[
                dict(name="Lot", kind="asphalt", ring=[[-5, 35], [70, 35], [70, 45], [-5, 45]])
            ],
            markings=[dict(type="line", path=[[0, 40], [60, 40]])],
            buildings=[
                dict(name="Shed", ring=ring, roof="flat", top=10),
                dict(
                    name="Deck",
                    ring=ring,
                    roof="flat",
                    top=10,
                    style="deck",
                    markings=[dict(type="stalls", line=[[2, 2], [52, 2]], count=20, depth=5)],
                ),
            ],
        )
        with tempfile.TemporaryDirectory() as d:
            area = Path(d) / "demo"
            area.mkdir()
            (area / "plan.json").write_text(json.dumps(plan))
            lay = layout.load(area)
        shed, deck = lay["buildings"]
        self.assertNotIn("sheets", shed)
        (sheet,) = deck["sheets"]  # one sheet: the roof deck is one face
        self.assertEqual(sheet["name"], "authored_demo_d001_0")
        self.assertEqual(len(deck["paint"]), 21)
        self.assertEqual(lay["surfaces"][0]["sheets"][0]["name"], "authored_demo_p000_0")
        # the roof's paint stays off the ground's list
        self.assertEqual(tuple(lay["markings"][0]["line"][0]), (0.0, 40.0))
        u, v = layout.sheet_uv(sheet, 30, 15)
        self.assertTrue(0 < u < 1 and 0 < v < 1)
        corners = [layout.sheet_uv(sheet, *p) for p in ring]
        self.assertTrue(all(0 < a < 1 and 0 < b < 1 for a, b in corners))

    def test_markings_on_a_pitched_roof_are_an_error(self):
        part = dict(name="Barn", ring=[[0, 0], [9, 0], [9, 9]], roof="gable", markings=[])
        with self.assertRaises(ValueError):
            layout.roof_paint(part, "demo_d000")


class Standards(unittest.TestCase):
    def test_turn_arrow_follows_the_sheet(self):
        # SHS metric sheet 10-10: tip 1.7 m from the tail, head 0.8 m above and 1.1 m below it
        ring = layout.primitives(dict(type="arrow", at=[0, 0], angle=90, shape="left"))[0]["ring"]
        tip = min(ring, key=lambda p: p[0])
        top = max(ring, key=lambda p: p[1])
        self.assertAlmostEqual(tip[1] + 1.25, 1.7, places=2)  # `at` is 1.25 m from the tail
        self.assertAlmostEqual(top[1] - tip[1], 0.8, places=2)
        self.assertTrue(math.isclose(min(p[1] for p in ring), -1.25))


if __name__ == "__main__":
    unittest.main()
