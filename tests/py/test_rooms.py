"""Interior geometry from a sign plan (blender/scripted/rooms.py) and the CCOM interior plan."""

import json
import math
import sys
import unittest
from pathlib import Path

SCRIPTED = Path(__file__).resolve().parents[2] / "blender" / "scripted"
sys.path.insert(0, str(SCRIPTED))

import geom  # noqa: E402
import layout  # noqa: E402
import rooms  # noqa: E402

SQUARE = [(0, 0), (10, 0), (10, 10), (0, 10)]


class Clip(unittest.TestCase):
    def test_a_run_through_a_keep_out_loses_the_part_inside(self):
        keep = [(4, -1), (6, -1), (6, 1), (4, 1)]
        parts = rooms.clip(((0, 0), (10, 0)), keep_out=[keep])
        self.assertEqual(len(parts), 2)
        self.assertAlmostEqual(parts[0][1][0], 4.0)
        self.assertAlmostEqual(parts[1][0][0], 6.0)

    def test_a_run_keeps_only_what_lies_inside_the_bounds(self):
        parts = rooms.clip(((-3, 5), (13, 5)), inside=SQUARE)
        self.assertEqual(len(parts), 1)
        (a, b) = parts[0]
        self.assertAlmostEqual(a[0], 0.0)
        self.assertAlmostEqual(b[0], 10.0)

    def test_a_run_wholly_in_a_keep_out_is_gone(self):
        self.assertEqual(rooms.clip(((1, 1), (2, 2)), keep_out=[SQUARE]), [])


class Runs(unittest.TestCase):
    def test_an_opening_leaves_a_lintel_and_two_full_pieces(self):
        run = dict(path=[[0, 0], [6, 0]], openings=[dict(at=[2, 0], to=[3, 0])])
        parts = rooms.run_pieces(run, 100.0, 103.0)
        full = [p for p in parts if p["z0"] == 100.0]
        lintel = [p for p in parts if p["z0"] > 100.0]
        self.assertEqual(len(full), 2)
        self.assertEqual(len(lintel), 1)
        self.assertAlmostEqual(lintel[0]["z0"], 100.0 + rooms.DOOR_HEAD)
        self.assertAlmostEqual(lintel[0]["p"][0], 2.0)
        self.assertAlmostEqual(lintel[0]["q"][0], 3.0)
        # the two full pieces leave the door clear
        self.assertAlmostEqual(full[0]["q"][0], 2.0)
        self.assertAlmostEqual(full[1]["p"][0], 3.0)

    def test_an_opening_to_the_ceiling_has_no_lintel(self):
        run = dict(path=[[0, 0], [6, 0]], openings=[dict(at=[2, 0], to=[3, 0], head=None)])
        parts = rooms.run_pieces(run, 100.0, 103.0)
        self.assertEqual(len(parts), 2)

    def test_corners_overlap_by_half_the_thickness(self):
        run = dict(path=[[0, 0], [4, 0], [4, 4]], thickness=0.2)
        a, b = rooms.run_pieces(run, 0.0, 3.0)
        self.assertAlmostEqual(a["q"][0], 4.1)  # carried on past the corner
        self.assertAlmostEqual(b["p"][1], -0.1)

    def test_a_box_is_the_run_widened_by_its_thickness(self):
        corners = rooms.box(dict(p=(0, 0), q=(4, 0), t=0.2, z0=1.0, z1=3.0))
        xs = sorted({round(c[0], 6) for c in corners})
        ys = sorted({round(c[1], 6) for c in corners})
        zs = sorted({c[2] for c in corners})
        self.assertEqual(xs, [0.0, 4.0])
        self.assertEqual(ys, [-0.1, 0.1])
        self.assertEqual(zs, [1.0, 3.0])
        verts, faces = rooms.box_mesh(corners)
        self.assertEqual(len(verts), 8)
        self.assertEqual(len(faces), 6)

    def test_prism_faces_close_the_solid(self):
        verts, faces = rooms.prism(SQUARE, 0.0, 1.0)
        self.assertEqual(len(verts), 8)
        self.assertEqual(len(faces), 6)  # four sides, top and bottom
        edges = {}
        for f in faces:
            for i, j in zip(f, f[1:] + f[:1], strict=True):
                edges[(i, j)] = edges.get((i, j), 0) + 1
        for (i, j) in edges:  # every edge is used once in each direction: a closed, outward shell
            self.assertIn((j, i), edges)

    def test_overlap_finds_a_shared_area(self):
        self.assertTrue(rooms.overlaps(SQUARE, [[(9, 9), (12, 9), (12, 12), (9, 12)]]))
        self.assertFalse(rooms.overlaps(SQUARE, [[(11, 0), (12, 0), (12, 1), (11, 1)]]))


class CcomPlan(unittest.TestCase):
    """The CCOM interior plan: nothing over the main model's own interior, nothing through the
    shell, every guess said."""

    @classmethod
    def setUpClass(cls):
        cls.lay = layout.load(SCRIPTED / "ccom")
        cls.floors = cls.lay["interiors"]

    def test_there_are_two_floors_with_levels_from_the_main_model(self):
        self.assertEqual(len(self.floors), 2)
        for f in self.floors:
            self.assertLess(f["floor"], f["ceiling"])
            self.assertTrue(130 < f["floor"] < 150)
            self.assertIn("unverified", f)

    def test_nothing_is_built_in_a_keep_out_or_outside_the_shell(self):
        for f in self.floors:
            keep = [k["ring"] for k in f["keep_out"]]
            for run in f["walls"]:
                for p in rooms.run_pieces(run, f["floor"], f["ceiling"], keep, f["inside"]):
                    mid = ((p["p"][0] + p["q"][0]) / 2, (p["p"][1] + p["q"][1]) / 2)
                    self.assertTrue(geom.inside(f["inside"], *mid), run["name"])
                    self.assertFalse(any(geom.inside(k, *mid) for k in keep), run["name"])
            for item in f["blocks"] + f["solids"]:
                self.assertFalse(rooms.overlaps(item["ring"], keep), item["name"])
                for x, y in item["ring"]:
                    self.assertTrue(geom.inside(f["inside"], x, y), item["name"])
            # slabs reach the walls (the other sources' ground is taken out of the building), so
            # they only have to stay inside the outline; lobby items stand inside it too
            for item in f["slabs"] + f.get("items", []):
                for x, y in item["ring"]:
                    self.assertTrue(geom.inside(f["outline"], x, y), item["name"])
            for item in f["slabs"]:  # `under`: keep-outs whose adopted objects stand on the slab
                rest = [k["ring"] for k in f["keep_out"] if k["name"] not in item.get("under", ())]
                self.assertFalse(rooms.overlaps(item["ring"], rest), item["name"])

    def test_every_object_says_its_source_and_what_is_a_guess(self):
        for f in self.floors:
            for group in ("walls", "slabs", "blocks", "solids", "items"):
                for item in f.get(group, []):
                    self.assertTrue(item["name"].endswith("_UNVERIFIED"), item["name"])
            for k in f["keep_out"]:
                self.assertTrue(k.get("why") and k.get("objects"), k["name"])

    def test_room_numbers_are_unique_and_inside_the_building(self):
        seen = set()
        for f in self.floors:
            for r in f["rooms"]:
                self.assertNotIn(r["number"], seen)
                seen.add(r["number"])
                self.assertTrue(math.isfinite(r["at"][0]) and math.isfinite(r["at"][1]))
                self.assertTrue(geom.inside(f["outline"], *r["at"]), r["number"])

    def test_room_labels_file_matches_the_plan(self):
        labels = rooms.labels(self.floors)
        self.assertEqual(len(labels), sum(len(f["rooms"]) for f in self.floors))
        for lab in labels:
            self.assertEqual(set(lab), {"name", "x", "y", "z", "floor", "unverified"})
        json.dumps(labels)  # plain data


if __name__ == "__main__":
    unittest.main()
