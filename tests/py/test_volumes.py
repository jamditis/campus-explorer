"""Volume rules of an area without ground (blender/scripted/supersede.py): what the rules file says,
and what it refuses."""

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

    def test_a_door_volume_keeps_both_levels(self):
        v = supersede.check_volumes([dict(name="door", ring=SQ, above=140.2, below=142.6)])[0]
        self.assertEqual((v["above"], v["below"]), (140.2, 142.6))

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
            dict(name="a", ring=SQ, under=3),  # unknown key
            dict(name="a", ring=SQ, above=5, below=3),  # a band upside down
            dict(name="a", ring=SQ, below=True),
            dict(name="a", ring=SQ, keep=["(unclosed"]),
            dict(name="a", ring=SQ, above="146"),
            dict(name="a", ring=[[0, 0], [10, 0]]),
            dict(name="a", ring=[[0, 0], [10, 0], [0, 10], [10, 10]]),  # crosses itself
            # a spike: an offset ring's miter at the end of a shared wall (3.5 degrees)
            dict(
                name="a",
                ring=[[29.67, -5.78], [33.05, -6.6], [41.65, 28.68], [34.56, 5.71], [12.62, 10.74]],
            ),  # fmt: skip
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
        # area's cut now runs OVERLAP into the other's ground there and nowhere else
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, -5), (20, -5), (20, 30), (10, 30)]
        d = supersede.OVERLAP
        for ring in (a, a[::-1]):
            out = supersede.grow_shared(ring, [b])
            xs = sorted({round(p[0], 6) for p in out})
            ys = sorted({round(p[1], 6) for p in out})
            self.assertEqual(xs, [0, 10 + d])
            self.assertEqual(ys, [0, 10])
        self.assertEqual(supersede.grow_shared(a, []), a)

    def test_a_partly_shared_edge_grows_on_the_shared_stretch_only(self):
        # b's edge x 10 runs from y -5 to 30; a holds y 0 to 10 of it: b reaches into a there,
        # the rest of the edge (far field on the other side) stays where it was
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, -5), (20, -5), (20, 30), (10, 30)]
        d = supersede.OVERLAP
        out = supersede.grow_shared(b, [a])
        self.assertIn((10.0, -5.0), [tuple(p) for p in out])
        self.assertIn((10.0, 30.0), [tuple(p) for p in out])
        self.assertTrue(geom.inside(out, 10 - d / 2, 5))  # inside a, now cut by b too
        self.assertFalse(geom.inside(out, 10 - d / 2, -1))  # far field: not cut
        self.assertFalse(geom.inside(out, 10 - d / 2, 11))
        self._grown_ok("b", b, out, [a])

    def test_a_narrow_notch_in_a_shared_edge_leaves_no_loop(self):
        # webster's outline round Blanton Hall's east corner, shared with the blanton area: short
        # runs (0.3 to 0.6 m) round the corner stay where they are, the runs either side move 0.6 m
        # out past them, and the grown outline crossed itself at (191.7, 472.4)
        chain = [(178.89, 442.4), (191.26, 469.87), (191.88, 470.96), (192.82, 471.9),
                 (192.27, 472.13), (196.3, 480.69), (196.02, 480.82), (196.14, 481.08),
                 (182.16, 486.75)]  # fmt: skip
        west = [*chain, (170.0, 486.75), (170.0, 442.4)][::-1]  # the hall's side, anticlockwise
        east = [*chain, (182.16, 500.0), (215.0, 500.0), (215.0, 442.4)]
        for ring, other in ((east, west), (west, east)):
            self._grown_ok("notch", ring, supersede.grow_shared(ring, [other]), [other])

    def test_a_corner_where_the_neighbour_ends_takes_no_far_field(self):
        # a three-way corner: a and b share x 10 from y 0 to 10; past (10, 10) the far field lies
        # north of a and west of b's slanted edge. Grown by lines alone, a's corner would reach
        # past b into the far field and leave a hole in the ground there
        a = [(0, 0), (10, 0), (10, 10), (0, 10)]
        b = [(10, 0), (20, 0), (20, 20), (10, 10)]  # b's edge leaves (10, 10) at 45 degrees
        for ring, other in ((a, b), (b, a)):
            self._grown_ok("corner", ring, supersede.grow_shared(ring, [other]), [other])
        # an acute corner of the neighbour (b's outline leaves the shared line at 30 degrees)
        c = [(10, -10), (20, -10), (15, 10 - 5 * 3**0.5), (10, 10)]
        for ring, other in ((a, c), (c, a)):
            self._grown_ok("acute", ring, supersede.grow_shared(ring, [other]), [other])

    def _grown_ok(self, name, old, grown, others, step=0.02):
        """The grown outline holds the old one, takes no ground that no area owns (every point of
        it lies in the old outline or in another area), and does not cross itself."""
        for p in supersede.uncovered(old, [grown], step):
            self.fail(f"{name}: the old outline at {p} is outside the grown one")
        for p in supersede.uncovered(grown, [old, *others], step):
            self.fail(f"{name}: the grown outline takes ground no area owns at {p}")
        n = len(grown)
        for i in range(n):
            for j in range(i + 2, n):
                if (j + 1) % n != i:
                    a, b, c, e = grown[i], grown[(i + 1) % n], grown[j], grown[(j + 1) % n]
                    crosses = supersede._crosses(a, b, c, e)
                    self.assertFalse(crosses, f"{name}: crosses itself at {a}")

    def test_an_area_that_asks_for_overlap_cuts_round_all_of_its_own_ground(self):
        feet = {d.name: layout.load(d)["footprint"] for d in layout.areas()}
        for d in layout.areas():
            f = d / "footprint.json"
            if not f.exists() or not json.loads(f.read_text())["supersede"].get("overlap"):
                continue
            others = supersede.grow_into(d.name)
            r = supersede.area_rules(d, True, others)
            grown = [tuple(p) for p in r["footprint"]]
            self.assertNotEqual(grown, [tuple(round(v, 3) for v in p) for p in feet[d.name]])
            self._grown_ok(d.name, [tuple(p[:2]) for p in feet[d.name]], grown, others, 0.05)

    def test_every_edge_two_areas_share_is_cut_past_by_one_of_them(self):
        # the sliver of far field between two areas' cuts goes only where one of them reaches past
        # the shared line: every area that shares an edge asks for overlap. Near the ends of a
        # stretch (END metres) a grown corner may step back so as not to take far field
        END = 2.0
        feet = {d.name: layout.load(d)["footprint"] for d in layout.areas()}
        feet = {k: [tuple(p[:2]) for p in f] for k, f in feet.items() if f}
        grown = {}
        for d in layout.areas():
            if d.name in feet:
                rules = supersede.area_rules(d, True, supersede.grow_into(d.name))
                grown[d.name] = [tuple(p) for p in rules["footprint"]]
        h = supersede.OVERLAP / 2
        names = sorted(feet)
        for k in names:
            others = [feet[o] for o in names if o != k]
            for a, b, j in supersede.shared_stretches(feet[k], others):
                o = [n for n in names if n != k][j]
                ln = math.hypot(b[0] - a[0], b[1] - a[1])
                if ln < supersede.MIN_SHARED + 2 * END:
                    continue
                ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
                sign = 1.0 if geom.area(feet[k]) > 0 else -1.0
                nx, ny = sign * uy, -sign * ux  # outward
                t = END
                while t <= ln - END:
                    x, y = a[0] + ux * t, a[1] + uy * t
                    past = geom.inside(grown[k], x + nx * h, y + ny * h) or geom.inside(
                        grown[o], x - nx * h, y - ny * h
                    )
                    self.assertTrue(past, f"{k} / {o} at {(round(x, 2), round(y, 2))}")
                    t += 0.5

    def test_an_area_added_beside_published_ones_leaves_their_rules_as_they_were(self):
        # `neighbours_keep_cuts`: the neighbours' rules, and so the marks their cuts left in the
        # published tiles, are the same as with the new area left out; the new area alone cuts
        # past the edges it shares with them (test_every_edge_two_areas_share_is_cut_past_...)
        areas = {d.name: d for d in layout.areas() if (d / "footprint.json").exists()}
        rules = {k: json.loads((d / "footprint.json").read_text()) for k, d in areas.items()}
        new = [k for k, r in rules.items() if r["supersede"].get("neighbours_keep_cuts")]
        for k in new:
            rest = {n: d for n, d in areas.items() if n != k}
            for n, d in rest.items():
                with_it = supersede.area_rules(d, True, supersede.grow_into(n, areas))
                without = supersede.area_rules(d, True, supersede.grow_into(n, rest))
                self.assertEqual(with_it, without, f"{k} changes {n}'s rules")

    def test_every_plan_volume_is_usable(self):
        for d in layout.areas():
            f = d / "footprint.json"
            if f.exists():
                vols = json.loads(f.read_text())["supersede"].get("volumes", [])
                supersede.check_volumes(vols)


if __name__ == "__main__":
    unittest.main()
