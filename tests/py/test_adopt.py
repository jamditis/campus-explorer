"""The pure parts of blender/scripted/adopt.py: names, the group transform, the plan check."""

import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import adopt  # noqa: E402
import layout  # noqa: E402

SHA = "0" * 64


def plan(**over):
    p = dict(
        file="main.blend",
        sha256=SHA,
        groups=[
            dict(name="as_is", objects=["Desk", "Chair"]),
            dict(
                name="atrium",
                objects=["Stair"],
                transform=dict(rotate_z_deg=-13.7, about=[0.0, 0.0], translate=[0.15, -2.764, 0.0]),
            ),
            dict(name="sign", objects=["Panel", "Lettering"], text={"Lettering": "NEW\nTEXT"}),
        ],
    )
    p.update(over)
    return p


class Names(unittest.TestCase):
    def test_a_short_name_takes_the_prefix(self):
        n = adopt.adopt_name("CCOM newsroom bay glass (mw)", set())
        self.assertEqual(n, "SW_adopt_CCOM newsroom bay glass (mw)")

    def test_a_long_name_is_cut_to_63_bytes_and_stays_unique(self):
        a = "NG 2F CCM old offices door frosted glass panel left leaf (mw) A"
        b = "NG 2F CCM old offices door frosted glass panel left leaf (mw) B"
        taken = set()
        na = adopt.adopt_name(a, taken)
        taken.add(na)
        nb = adopt.adopt_name(b, taken)
        for n in (na, nb):
            self.assertLessEqual(len(n.encode()), 63)
            self.assertTrue(n.startswith("SW_adopt_NG 2F CCM old offices"))
        self.assertNotEqual(na, nb)

    def test_a_cut_name_keeps_its_unverified_label(self):
        n = adopt.adopt_name("NQ smoke detector N classroom 0 LED, ceiling (UNVERIFIED)", set())
        self.assertLessEqual(len(n.encode()), 63)
        self.assertTrue(n.endswith("_UNVERIFIED"), n)
        # a source name already cut by Blender inside the label still counts as unverified
        n = adopt.adopt_name("ef tower bed whiteflower 00 (photo; species UNVERI", set())
        self.assertIn("UNVERIFIED", n)

    def test_a_cut_never_splits_a_character(self):
        n = adopt.adopt_name("Café " * 20, set())
        self.assertLessEqual(len(n.encode()), 63)
        n.encode().decode()  # valid UTF-8

    def test_the_same_source_name_gives_the_same_name_every_run(self):
        a = "x" * 70
        self.assertEqual(adopt.adopt_name(a, set()), adopt.adopt_name(a, set()))


class Transform(unittest.TestCase):
    def apply(self, m, p):
        return [sum(m[i][j] * v for j, v in enumerate([*p, 1.0])) for i in range(3)]

    def test_no_transform_is_the_identity(self):
        m = adopt.group_matrix(None)
        self.assertEqual(self.apply(m, (3.0, 4.0, 5.0)), [3.0, 4.0, 5.0])

    def test_rotate_about_a_point_then_translate(self):
        m = adopt.group_matrix(dict(rotate_z_deg=90, about=[10.0, 0.0], translate=[1.0, 2.0, 3.0]))
        x, y, z = self.apply(m, (11.0, 0.0, 7.0))  # 1 m east of `about` turns to 1 m north of it
        self.assertAlmostEqual(x, 11.0)
        self.assertAlmostEqual(y, 3.0)
        self.assertAlmostEqual(z, 10.0)

    def test_t1_moves_the_atrium_stair_as_the_study_says(self):
        m = adopt.group_matrix(dict(rotate_z_deg=-13.7, about=[0, 0], translate=[0.15, -2.764, 0]))
        x, y, _ = self.apply(m, (-11.25, 15.0, 0.0))
        c, s = math.cos(math.radians(13.7)), math.sin(math.radians(13.7))
        # building frame a = x cos - y sin, b = x sin + y cos (ccom_volume_ring.json); the stair
        # centre lands within a few centimetres of the floor 1 sign's stair (a -10.45, b 12.35)
        self.assertAlmostEqual(x * c - y * s, -10.45, delta=0.05)
        self.assertAlmostEqual(x * s + y * c, 12.35, delta=0.05)

    def test_an_unknown_transform_key_is_an_error(self):
        with self.assertRaises(ValueError):
            adopt.group_matrix(dict(rotate_z_deg=10, then_translate=[0, 0, 0]))


class Check(unittest.TestCase):
    def test_a_good_plan_lists_every_object_with_its_group(self):
        rows = adopt.check(plan())
        self.assertEqual([r[0] for r in rows], ["Desk", "Chair", "Stair", "Panel", "Lettering"])
        self.assertEqual(rows[2][1]["name"], "atrium")

    def test_an_object_in_two_groups_is_an_error(self):
        p = plan()
        p["groups"][1]["objects"].append("Desk")
        with self.assertRaisesRegex(ValueError, "Desk"):
            adopt.check(p)

    def test_text_for_an_object_outside_its_group_is_an_error(self):
        p = plan()
        p["groups"][2]["text"] = {"Desk": "x"}
        with self.assertRaisesRegex(ValueError, "Desk"):
            adopt.check(p)

    def test_a_bad_hash_or_an_empty_group_is_an_error(self):
        with self.assertRaises(ValueError):
            adopt.check(plan(sha256="abc"))
        p = plan()
        p["groups"][0]["objects"] = []
        with self.assertRaises(ValueError):
            adopt.check(p)

    def test_the_file_is_a_base_name(self):
        with self.assertRaises(ValueError):
            adopt.check(plan(file="/workspace/dl/main.blend"))


class Source(unittest.TestCase):
    def test_the_file_is_found_beside_the_assets_or_where_adopt_from_says(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "main.blend"
            f.write_bytes(b"blend")
            sha = hashlib.sha256(b"blend").hexdigest()
            p = plan(sha256=sha)
            self.assertEqual(adopt.source(p, None, Path(d) / "trees.blend"), f)
            self.assertEqual(adopt.source(p, Path(d), None), f)
            self.assertEqual(adopt.source(p, f, None), f)

    def test_a_wrong_hash_or_a_missing_file_stops_the_build_with_a_message(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "main.blend"
            f.write_bytes(b"other")
            with self.assertRaisesRegex(SystemExit, "sha256"):
                adopt.source(plan(), f, None)
            with self.assertRaisesRegex(SystemExit, "not found"):
                adopt.source(plan(), Path(d) / "nothing.blend", None)
            with self.assertRaisesRegex(SystemExit, "--adopt-from"):
                adopt.source(plan(), None, None)


class Skip(unittest.TestCase):
    def test_what_the_web_export_leaves_out_of_every_tile_is_not_adopted(self):
        self.assertTrue(adopt.export_skips("CCOM newsroom task chairs (mx, GN instances)"))
        self.assertTrue(adopt.export_skips("CCOM newsroom seated people placeholders (my)"))
        self.assertFalse(adopt.export_skips("CCOM newsroom anchor desk (mw)"))


class Layout(unittest.TestCase):
    def test_an_area_folder_with_an_adopt_file_and_volumes_only_loads(self):
        with tempfile.TemporaryDirectory() as d:
            area = Path(d) / "ccom"
            area.mkdir()
            (area / "adopt.json").write_text(json.dumps(dict(zone="cc_adopt", adopt=plan())))
            vol = dict(name="inside", ring=[[0, 0], [10, 0], [10, 10]], drop="all")
            (area / "footprint.json").write_text(
                json.dumps(dict(zone="cc", supersede=dict(volumes=[vol])))
            )
            lay = layout.load(area)
            self.assertIsNone(lay["footprint"])
            self.assertEqual(len(lay["adopt"]), 1)
            self.assertEqual(lay["adopt"][0]["zone"], "cc_adopt")
            self.assertEqual(lay["volumes"][0]["name"], "inside")


if __name__ == "__main__":
    unittest.main()
