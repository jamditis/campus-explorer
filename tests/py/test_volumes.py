"""Volume rules of an area without ground (blender/scripted/supersede.py): what the rules file says,
and what it refuses."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import layout  # noqa: E402
import supersede  # noqa: E402

SQ = [[0, 0], [10, 0], [10, 10], [0, 10]]


class Volumes(unittest.TestCase):
    def test_a_ring_volume_keeps_its_ring_level_and_patterns(self):
        v = supersede.check_volumes(
            [dict(name="band", ring=SQ, drop="all", above=146.8, keep=["(?i)lawn|walk"], why="x")]
        )[0]
        self.assertEqual(v["ring"], [[0, 0], [10, 0], [10, 10], [0, 10]])
        self.assertEqual(v["above"], 146.8)
        self.assertEqual(v["keep"], ["(?i)lawn|walk"])
        self.assertNotIn("why", v)  # the reason is for people: it does not change the hash

    def test_a_clockwise_ring_and_an_arc_corner_are_fine(self):
        v = supersede.check_volumes([dict(name="a", ring=[[0, 0], [0, 10], [10, 10, 2], [10, 0]])])
        self.assertGreater(len(v[0]["ring"]), 4)  # the arc is drawn as points

    def test_a_mesh_volume_names_meshes(self):
        v = supersede.check_volumes([dict(name="sign", meshes=["SCMSIGN"], drop="all")])[0]
        self.assertEqual(v, dict(name="sign", meshes=["SCMSIGN"], drop="all"))

    def test_what_a_volume_must_not_be(self):
        bad = [
            dict(name="a", ring=SQ, meshes=["x"]),  # both
            dict(name="a"),  # neither
            dict(name="a", ring=SQ, drop="ground"),  # only "all"
            dict(name="a", ring=SQ, below=3),  # unknown key
            dict(name="a", ring=SQ, keep=["(unclosed"]),
            dict(name="a", ring=SQ, above="146"),
            dict(name="a", ring=[[0, 0], [10, 0]]),
            dict(name="a", ring=[[0, 0], [10, 0], [0, 10], [10, 10]]),  # crosses itself
            # a spike: an offset ring's miter at the end of a shared wall (3.5 degrees)
            dict(name="a", ring=[[29.67, -5.78], [33.05, -6.6], [41.65, 28.68], [34.56, 5.71],
                                 [12.62, 10.74]]),  # fmt: skip
        ]
        for v in bad:
            with self.assertRaises(ValueError, msg=v):
                supersede.check_volumes([v])
        with self.assertRaises(ValueError):
            supersede.check_volumes([dict(name="a", ring=SQ), dict(name="a", ring=SQ)])

    def test_an_area_with_volumes_only_writes_no_footprint(self):
        with tempfile.TemporaryDirectory() as d:
            area = Path(d) / "cc"
            area.mkdir()
            (area / "footprint.json").write_text(
                json.dumps(dict(zone="cc", supersede=dict(volumes=[dict(name="in", ring=SQ)])))
            )
            r = supersede.area_rules(area, True)
            self.assertEqual(r["name"], "cc")
            self.assertNotIn("footprint", r)
            self.assertEqual(r["volumes"][0]["name"], "in")
            self.assertFalse(r["skip"])

    def test_an_area_with_ground_writes_what_it_wrote_before(self):
        r = supersede.area_rules(ROOT / "blender" / "scripted" / "southwest", False)
        self.assertEqual(sorted(r), ["clip", "drop", "footprint", "name", "skip", "tuck"])
        self.assertTrue(r["skip"])

    def test_every_plan_volume_is_usable(self):
        for d in layout.areas():
            f = d / "footprint.json"
            if f.exists():
                vols = json.loads(f.read_text())["supersede"].get("volumes", [])
                supersede.check_volumes(vols)


if __name__ == "__main__":
    unittest.main()
