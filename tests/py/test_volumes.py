"""Volume rules of an area without ground (blender/scripted/supersede.py): what the rules file says,
and what it refuses."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import geom  # noqa: E402
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

    def test_an_edge_shared_with_another_area_reaches_a_little_into_it(self):
        # two areas side by side both cut the far field on x 10: the two cuts left a sliver of it
        # standing between them (up to 0.9 m above the ground, a dark line along the seam); one
        # area's cut now runs 0.25 m into the other's ground there and nowhere else
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, -5), (20, -5), (20, 30), (10, 30)]
        for ring in (a, a[::-1]):
            out = supersede.grow_shared(ring, [b])
            xs = sorted({round(p[0], 6) for p in out})
            ys = sorted({round(p[1], 6) for p in out})
            self.assertEqual(xs, [0, supersede.OVERLAP + 10])
            self.assertEqual(ys, [0, 10])
        # b's edge x 10 is only partly shared: its outline stays as it is
        self.assertEqual(supersede.grow_shared(b, [a]), b)
        self.assertEqual(supersede.grow_shared(a, []), a)

    def test_an_area_that_asks_for_overlap_cuts_round_all_of_its_own_ground(self):
        feet = {d.name: layout.load(d)["footprint"] for d in layout.areas()}
        for d in layout.areas():
            f = d / "footprint.json"
            if not f.exists() or not json.loads(f.read_text())["supersede"].get("overlap"):
                continue
            others = [g for k, g in feet.items() if k != d.name and g]
            r = supersede.area_rules(d, True, others)
            grown = [tuple(p) for p in r["footprint"]]
            self.assertNotEqual(grown, [tuple(round(v, 3) for v in p) for p in feet[d.name]])
            for x, y in feet[d.name]:  # the old outline lies inside the grown one, or on it
                on = geom.inside(grown, x, y) or supersede._near_ring(grown, x, y)
                self.assertTrue(on, d.name)

    def test_every_plan_volume_is_usable(self):
        for d in layout.areas():
            f = d / "footprint.json"
            if f.exists():
                vols = json.loads(f.read_text())["supersede"].get("volumes", [])
                supersede.check_volumes(vols)


if __name__ == "__main__":
    unittest.main()
