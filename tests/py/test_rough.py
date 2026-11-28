"""Rough interiors from a footprint and floor levels (blender/scripted/rough.py), and every rough
entry in the plan files."""

import json
import math
import sys
import unittest
from pathlib import Path

SCRIPTED = Path(__file__).resolve().parents[2] / "blender" / "scripted"
sys.path.insert(0, str(SCRIPTED))

import geom  # noqa: E402
import rooms  # noqa: E402
import rough  # noqa: E402

BAR = dict(
    name="T",
    building="Test",
    osm_building="university",
    outline=[[0, 0], [60, 0], [60, 20], [0, 20]],
    levels=[dict(level=1, floor=100.0), dict(level=2, floor=104.0), dict(level=3, floor=108.0)],
    roof=112.0,
    entrances=[dict(at=[30, -0.5], level=1)],
    evidence="test",
    unverified="test",
)


def pieces(f):
    keep = [k["ring"] for k in f["keep_out"]]
    return [
        (w, p)
        for w in f["walls"]
        for p in rooms.run_pieces(w, f["floor"], f["ceiling"], keep, f["inside"])
    ]


def mid(p):
    return ((p["p"][0] + p["q"][0]) / 2, (p["p"][1] + p["q"][1]) / 2)


def crosses(s, t):
    """Do segments s and t ((x, y), (x, y)) cross or touch?"""

    def turn(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    (a, b), (c, d) = s, t
    d1, d2, d3, d4 = turn(c, d, a), turn(c, d, b), turn(a, b, c), turn(a, b, d)
    return d1 * d2 <= 0 and d3 * d4 <= 0 and not (d1 == d2 == 0)


def meet(s, t):
    """The point where segments s and t cross, or None (parallel or apart)."""
    (a, b), (c, d) = s, t
    r = (b[0] - a[0], b[1] - a[1])
    q = (d[0] - c[0], d[1] - c[1])
    den = r[0] * q[1] - r[1] * q[0]
    if abs(den) < 1e-12:
        return None
    t1 = ((c[0] - a[0]) * q[1] - (c[1] - a[1]) * q[0]) / den
    t2 = ((c[0] - a[0]) * r[1] - (c[1] - a[1]) * r[0]) / den
    if -1e-9 <= t1 <= 1 + 1e-9 and -1e-9 <= t2 <= 1 + 1e-9:
        return (a[0] + r[0] * t1, a[1] + r[1] * t1)
    return None


def walkable(test, f, route, label, blocks=()):
    """The route from the corridor to the door stays in the floor until its last leg, crosses the
    lining only in a door's opening (PASS or more inside its edges), and no other wall, stair or
    lift crosses it."""
    legs = list(zip(route, route[1:], strict=False))
    for k, leg in enumerate(legs):
        inside = rooms.clip(leg, inside=f["inside"])
        test.assertTrue(inside, label)
        test.assertLess(math.dist(inside[0][0], leg[0]), 1e-6, label)
        if k < len(legs) - 1:
            test.assertLess(math.dist(inside[0][1], leg[1]), 1e-6, f"{label}: leaves the floor")
    (lining,) = [w for w in f["walls"] if "lining" in w["name"]]
    gaps = [
        ((o["at"][0] + o["to"][0]) / 2, (o["at"][1] + o["to"][1]) / 2) for o in lining["openings"]
    ]
    path = [tuple(v[:2]) for v in lining["path"]]
    hits = []  # where the walk crosses the lining: in a door's opening, clear of its edges
    for leg in legs:
        for a, b in zip(path, path[1:], strict=False):
            x = meet(leg, (a, b))
            if x is not None:
                hits.append(x)
    if not hits:  # a door set in from the outline: the walk ends at it, in the opening
        test.assertLessEqual(
            min(math.dist(route[-1], g) for g in gaps), rough.ENTRANCE / 2, f"{label}: no door"
        )
    for x in hits:
        test.assertLessEqual(
            min(math.dist(x, g) for g in gaps),
            rough.ENTRANCE / 2 - rough.PASS + 1e-6,
            f"{label}: crosses the lining outside its door's opening",
        )
    for w, p in pieces(f):
        if "lining" in w["name"]:
            continue
        for leg in legs:
            test.assertFalse(crosses(leg, (p["p"], p["q"])), f"{label}: {w['name']}")
    for b in blocks:  # no stair or lift stands in the way
        ring = b["ring"]
        for leg in legs:
            for side in zip(ring, ring[1:] + ring[:1], strict=True):
                test.assertFalse(crosses(leg, side), f"{label}: {b['name']}")
            test.assertFalse(geom.inside(ring, *leg[0]), f"{label}: {b['name']}")


def rough_entries():
    for plan in sorted(SCRIPTED.glob("*/*.json")):
        for r in json.loads(plan.read_text()).get("rough", []):
            yield plan, r


class Floors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floors = rough.floors(BAR)

    def test_one_floor_per_level_with_its_ceiling_under_the_next_slab(self):
        self.assertEqual([f["level"] for f in self.floors], [1, 2, 3])
        self.assertEqual([f["ceiling"] for f in self.floors], [103.7, 107.7, 112.0])
        for f in self.floors:
            (slab,) = f["slabs"]
            self.assertEqual((slab["z0"], slab["z1"]), (round(f["floor"] - 0.3, 2), f["floor"]))

    def test_cores_are_one_block_each_from_the_lowest_floor_to_the_roof(self):
        blocks = [b for f in self.floors for b in f["blocks"]]
        self.assertEqual(sorted(b["kind"] for b in blocks), ["lift", "stair", "stair"])
        self.assertEqual(self.floors[1]["blocks"], [])
        for b in blocks:
            self.assertEqual((b["z0"], b["z1"]), (100.0, 112.0))
            for x, y in b["ring"]:
                self.assertTrue(geom.inside(self.floors[0]["inside"], x, y), b["name"])

    def test_the_corridor_runs_along_the_long_side_and_stops_at_the_stairs(self):
        stairs = [b for b in self.floors[0]["blocks"] if b["kind"] == "stair"]
        xs = sorted(sum(x for x, _ in b["ring"]) / 4 for b in stairs)
        self.assertAlmostEqual(xs[0], 0.55 + rough.STAIR[0] / 2, places=2)
        self.assertAlmostEqual(xs[1], 59.45 - rough.STAIR[0] / 2, places=2)
        for b in stairs:
            self.assertAlmostEqual(sum(y for _, y in b["ring"]) / 4, 10.0, places=1)

    def test_the_lift_stands_across_the_corridor_from_the_entrance(self):
        (lift,) = [b for b in self.floors[0]["blocks"] if b["kind"] == "lift"]
        cx = sum(x for x, _ in lift["ring"]) / 4
        cy = sum(y for _, y in lift["ring"]) / 4
        self.assertAlmostEqual(cx, 30.0, places=1)
        self.assertGreater(cy, 10.0 + rough.CORRIDOR / 2)  # the entrance is on the south side

    def test_no_wall_stands_in_a_core_the_corridor_or_the_lobby(self):
        f = self.floors[0]
        cores = [b["ring"] for b in f["blocks"]]
        # the clear zones less 0.1 m all round: the walls that bound them stand on their edges
        x0, x1 = 0.55 + rough.STAIR[0] + 0.1, 59.45 - rough.STAIR[0] - 0.1
        corridor = [(x0, 8.9), (x1, 8.9), (x1, 11.1), (x0, 11.1)]
        lobby = [(27.1, 0.6), (32.9, 0.6), (32.9, 9.9), (27.1, 9.9)]
        for w, p in pieces(f):
            m = mid(p)
            for ring in [*cores, corridor, lobby]:
                self.assertFalse(geom.inside(ring, *m), f"{w['name']} at {m}")

    def test_every_wall_piece_lies_inside_the_shell(self):
        for f in self.floors:
            for w, p in pieces(f):
                self.assertTrue(geom.inside(f["inside"], *mid(p)), w["name"])

    def test_each_room_has_a_door_on_the_corridor(self):
        f = self.floors[1]
        length = 60 - 2 * (0.4 + rough.LINING) - 2 * rough.STAIR[0]
        bays = max(1, round(length / rough.BAY))
        for side in ("L", "R"):
            doors = [
                o
                for w in f["walls"]
                if f"corridor0_{side}" in w["name"]
                for o in w.get("openings", [])
            ]
            self.assertEqual(len(doors), bays, side)
            for o in doors:
                self.assertAlmostEqual(math.dist(o["at"], o["to"]), rough.DOOR, places=1)

    def test_the_lining_opens_at_the_entrance_on_its_level_only(self):
        f1, f2 = self.floors[:2]
        (lining1,) = [w for w in f1["walls"] if "lining" in w["name"]]
        (lining2,) = [w for w in f2["walls"] if "lining" in w["name"]]
        (door,) = lining1["openings"]
        self.assertEqual(door["head"], rough.ENTRANCE_HEAD)
        self.assertAlmostEqual((door["at"][0] + door["to"][0]) / 2, 30.0, places=1)
        self.assertAlmostEqual(math.dist(door["at"], door["to"]), rough.ENTRANCE, places=1)
        self.assertNotIn("openings", lining2)
        # the lining's path is closed and its seam is in the middle of a side, not at the door
        self.assertEqual(lining1["path"][0], lining1["path"][-1])
        self.assertGreater(math.dist(lining1["path"][0], [30, 0.5]), 5)

    def test_no_toilets_and_no_labels_without_evidence(self):
        for f in self.floors:
            self.assertEqual(f["rooms"], [])
            self.assertFalse([w for w in f["walls"] if "toilet" in w["name"]])

    def test_every_object_is_marked_unverified(self):
        for f in self.floors:
            for item in f["walls"] + f["slabs"] + f["blocks"]:
                self.assertIn("UNVERIFIED", item["name"])

    def test_the_floors_are_usable_by_the_interior_builder(self):
        for f in self.floors:
            for key in (
                "name",
                "level",
                "floor",
                "ceiling",
                "outline",
                "inside",
                "keep_out",
                "walls",
                "slabs",
                "blocks",
                "solids",
                "rooms",
                "unverified",
            ):
                self.assertIn(key, f)
            self.assertTrue(pieces(f))


class Options(unittest.TestCase):
    def test_an_open_floor_keeps_only_the_lining_and_the_cores(self):
        f = rough.floors(dict(BAR, open=True))[0]
        self.assertEqual([w["name"] for w in f["walls"]], ["SW_T_F1_lining_UNVERIFIED"])
        self.assertEqual(len(f["blocks"]), 3)

    def test_toilets_where_the_evidence_puts_them_with_a_door_and_no_label(self):
        ring = [[40, 11.2], [46, 11.2], [46, 17], [40, 17]]
        r = dict(BAR, toilets=[dict(level=2, ring=ring, door=[43, 11.2], evidence="sign")])
        f1, f2, _f3 = rough.floors(r)
        self.assertEqual(f1["rooms"], [])
        self.assertEqual(f2["rooms"], [])
        (t,) = [w for w in f2["walls"] if "toilet" in w["name"]]
        (door,) = t["openings"]
        self.assertAlmostEqual((door["at"][0] + door["to"][0]) / 2, 43.0, places=1)
        # no corridor room wall runs through the toilet block
        for w, p in pieces(f2):
            if "room" in w["name"]:
                self.assertFalse(geom.inside(ring, *mid(p)), w["name"])

    def test_given_cores_replace_the_default_ones_and_the_corridor_runs_to_the_shell(self):
        r = dict(BAR, cores=[dict(kind="stair", at=[20, 14]), dict(kind="lift", at=[40, 14])])
        f = rough.floors(r)[0]
        self.assertEqual(sorted(b["kind"] for b in f["blocks"]), ["lift", "stair"])
        walls = [p for w, p in pieces(f) if "corridor0_L" in w["name"]]
        self.assertAlmostEqual(
            min(min(p["p"][0], p["q"][0]) for p in walls), 0.4 + rough.LINING, places=2
        )

    def test_a_second_spine_keeps_its_room_walls_out_of_the_first_ones_rooms(self):
        r = dict(
            BAR,
            outline=[[0, 0], [60, 0], [60, 20], [30, 20], [30, 45], [10, 45], [10, 20], [0, 20]],
            spines=[[[0.6, 10], [59.4, 10]], [[20, 10], [20, 44.4]]],  # stairs inside the shell
        )
        f = rough.floors(r)[0]
        first = rough._rect((6.6, 10), (53.4, 10), rough.CORRIDOR / 2 + rough.DEPTH)
        for w, p in pieces(f):
            if "room1" in w["name"]:
                self.assertFalse(geom.inside(first, *mid(p)), w["name"])

    def test_a_level_with_its_own_outline_keeps_its_walls_and_slab_inside_it(self):
        upper = [[0, 0], [60, 0], [60, 15], [0, 15]]  # holds the cores, not the north rooms
        r = dict(BAR, levels=[*BAR["levels"][:2], dict(level=3, floor=108.0, outline=upper)])
        f1, _f2, f3 = rough.floors(r)
        self.assertEqual(f3["outline"], upper)
        self.assertLess(max(y for _, y in f3["slabs"][0]["ring"]), 15)
        for w, p in pieces(f3):
            self.assertLess(mid(p)[1], 15, w["name"])
        self.assertGreater(max(y for _, y in f1["slabs"][0]["ring"]), 19)

    def test_an_entrance_beyond_the_corridor_end_gets_a_lobby_along_it(self):
        r = dict(
            BAR,
            spines=[[[0.6, 10], [40, 10]]],
            cores=[dict(kind="stair", at=[20, 15]), dict(kind="lift", at=[30, 15])],
            entrances=[dict(at=[60.3, 10], level=1)],
        )
        f = rough.floors(r)[0]
        sides = [p for w, p in pieces(f) if "lobby" in w["name"]]
        self.assertTrue(sides)
        for p in sides:  # the lobby's side walls run along the corridor, either side of it
            self.assertAlmostEqual(p["p"][1], p["q"][1], places=2)
            self.assertAlmostEqual(abs(p["p"][1] - 10), rough.LOBBY / 2, places=2)
        hall = [(40.1, 7.1), (59.4, 7.1), (59.4, 12.9), (40.1, 12.9)]
        for w, p in pieces(f):
            if "lining" not in w["name"]:
                self.assertFalse(geom.inside(hall, *mid(p)), w["name"])

    def test_a_door_beside_the_corridor_end_gets_a_porch_and_a_hall(self):
        # the straight line from the corridor's end to the door would run along the end wall
        r = dict(
            BAR,
            spines=[[[0.6, 10], [59.4, 10]]],
            cores=[dict(kind="stair", at=[20, 15]), dict(kind="lift", at=[30, 15])],
            entrances=[dict(at=[-0.3, 17.5], level=1)],
        )
        ((level, route),) = rough.routes(r)
        self.assertEqual(len(route), 3)
        f = rough.floors(r)[0]
        walkable(self, f, route, "west door", f["blocks"])

    def test_a_way_in_round_a_concave_bend_follows_the_floor(self):
        # a U: the door is on the far wing's outer face, the corridor in the near wing; the
        # straight line crosses the open bay between the wings
        u_shape = [[0, 0], [40, 0], [40, 40], [30, 40], [30, 10], [10, 10], [10, 40], [0, 40]]
        r = dict(
            BAR,
            outline=u_shape,
            spines=[[[5, 15], [5, 35]]],
            cores=[dict(kind="stair", at=[5, 5])],
            entrances=[dict(at=[40.3, 35], level=1)],
        )
        ((_level, route),) = rough.routes(r)
        self.assertGreater(len(route), 3)  # round the bend's corners
        f = rough.floors(r)[0]
        walkable(self, f, route, "far wing door", f["blocks"])

    def test_a_bent_way_in_crosses_the_lining_in_the_middle_of_its_door(self):
        # the door is past the corridor's end and a little off its line: the straight walk would
        # cross the lining 2 cm outside the opening
        r = dict(
            BAR,
            spines=[[[15, 6.25], [45.2, 6.25]]],
            cores=[dict(kind="stair", at=[20, 15])],
            entrances=[dict(at=[50.2, -1], level=1)],
        )
        ((_level, route),) = rough.routes(r)
        f = rough.floors(r)[0]
        walkable(self, f, route, "south door", f["blocks"])
        # the last leg runs square to the side through the opening's middle
        (a, b) = route[-2], route[-1]
        self.assertAlmostEqual(a[0], b[0], places=6)

    def test_a_default_stair_steps_aside_from_a_door_at_the_corridor_end(self):
        r = dict(BAR, entrances=[dict(at=[-0.5, 10], level=1)])
        ((_level, route),) = rough.routes(r)
        f = rough.floors(r)[0]
        walkable(self, f, route, "west door", f["blocks"])
        cores = [b["ring"] for b in f["blocks"]]
        self.assertEqual(len(cores), 3)  # two stairs and the lift, none in another
        for i, a in enumerate(cores):
            for b in cores[i + 1 :]:
                self.assertFalse(rough._overlap(a, b))

    def test_a_stair_that_steps_aside_fits_every_level(self):
        upper = [[0, 0], [60, 0], [60, 14.1], [0, 14.1]]
        r = dict(
            BAR,
            levels=[*BAR["levels"][:2], dict(level=3, floor=108.0, outline=upper)],
            entrances=[dict(at=[-0.5, 10], level=1)],
        )
        ((_level, route),) = rough.routes(r)
        fs = rough.floors(r)
        self.assertEqual(len(fs), 3)
        walkable(self, fs[0], route, "west door", fs[0]["blocks"])

    def test_a_door_on_its_corridor_needs_no_walk(self):
        r = dict(
            BAR,
            spines=[[[0.475, 10], [59, 10]]],
            cores=[dict(kind="stair", at=[20, 15])],
            entrances=[dict(at=[0.475, 10], level=1)],
        )
        self.assertEqual(len(rough.floors(r)), 3)

    def test_a_door_inside_a_stair_is_refused(self):
        r = dict(
            BAR,
            spines=[[[0.6, 10], [59, 10]]],
            cores=[dict(kind="stair", at=[3.5, 10])],
            entrances=[dict(at=[0.6, 10], level=1)],
        )
        with self.assertRaisesRegex(ValueError, "stands in a stair"):
            rough.floors(r)

    def test_default_stairs_of_two_close_corridors_step_apart(self):
        r = dict(BAR, entrances=[], spines=[[[1, 8], [59, 8]], [[1, 10.9], [59, 10.9]]])
        fs = rough.floors(r)
        cores = [b["ring"] for b in fs[0]["blocks"]]
        self.assertEqual(len(cores), 4)
        for i, a in enumerate(cores):
            for b in cores[i + 1 :]:
                self.assertFalse(rough._overlap(a, b))

    def test_overlapping_cores_are_refused(self):
        # a narrow bar: the default stair finds no clear side and the lift stands in it
        r = dict(
            BAR,
            outline=[[0, 0], [60, 0], [60, 9], [0, 9]],
            entrances=[dict(at=[7, -0.5], level=1)],
        )
        with self.assertRaisesRegex(ValueError, "overlap"):
            rough.floors(r)
        r = dict(BAR, cores=[dict(kind="stair", at=[20, 15]), dict(kind="lift", at=[21, 15])])
        with self.assertRaisesRegex(ValueError, "overlap"):
            rough.floors(r)

    def test_a_way_in_through_a_lift_is_refused(self):
        r = dict(
            BAR,
            spines=[[[0.6, 10], [59.4, 10]]],
            cores=[dict(kind="stair", at=[10, 15]), dict(kind="lift", at=[30, 4])],
        )
        with self.assertRaisesRegex(ValueError, "passes a lift"):
            rough.floors(r)

    def test_a_core_outside_an_upper_level_is_refused(self):
        upper = [[0, 0], [60, 0], [60, 12], [0, 12]]
        r = dict(
            BAR,
            levels=[*BAR["levels"][:2], dict(level=3, floor=108.0, outline=upper)],
            cores=[dict(kind="stair", at=[20, 15])],
        )
        with self.assertRaisesRegex(ValueError, "outside level 3"):
            rough.floors(r)

    def test_a_short_spine_without_given_cores_is_refused(self):
        with self.assertRaises(ValueError):
            rough.floors(dict(BAR, outline=[[0, 0], [16, 0], [16, 10], [0, 10]]))


class Check(unittest.TestCase):
    def test_housing_is_refused(self):
        for tag in ("dormitory", "apartments"):
            self.assertIn("housing", " ".join(rough.check(dict(BAR, osm_building=tag))))

    def test_a_dining_hall_in_housing_gets_its_open_dining_floor_and_entrance_only(self):
        hall = dict(
            BAR,
            osm_building="dormitory",
            use="dining",
            open=True,
            levels=[dict(level=1, floor=100.0)],
            roof=104.0,
        )
        self.assertEqual(rough.check(hall), [])
        (f,) = rough.floors(hall)
        self.assertEqual([w["name"] for w in f["walls"]], ["SW_T_F1_lining_UNVERIFIED"])
        self.assertEqual(len(f["walls"][0]["openings"]), 1)
        self.assertEqual((f["blocks"], f["rooms"]), ([], []))
        self.assertEqual(rough.routes(hall), [])
        for extra, word in (
            (dict(levels=BAR["levels"], roof=112.0), "dining floor only"),
            (dict(open=False), "open"),
            (dict(cores=[dict(kind="stair", at=[20, 15])]), "no cores"),
            (dict(spines=[[[0.6, 10], [59.4, 10]]]), "no spines"),
            (dict(rooms=[dict(level=1, number="101", at=[30, 5], evidence="sign")]), "no rooms"),
            (dict(use="flats"), "use is"),
        ):
            self.assertIn(word, " ".join(rough.check(dict(hall, **extra))), word)

    def test_a_usable_entry_has_no_problems(self):
        self.assertEqual(rough.check(BAR), [])

    def test_problems_are_named(self):
        bad = dict(
            BAR,
            levels=[dict(level=1, floor=104.0), dict(level=2, floor=100.0)],
            roof=101.0,
            entrances=[dict(at=[30, -9], level=4)],
            toilets=[dict(level=1, ring=[[1, 1], [2, 1], [2, 2]])],
            rooms=[dict(level=1, number="Front desk", at=[30, 5], evidence="sign")],
        )
        text = " ".join(rough.check(bad))
        for word in (
            "rise",
            "2.4 m",
            "outside the outline",
            "level 4",
            "evidence",
            "not a room number",
        ):
            self.assertIn(word, text)
        self.assertIn(
            "no roof", " ".join(rough.check({k: v for k, v in BAR.items() if k != "roof"}))
        )


class Plans(unittest.TestCase):
    """Every rough entry in blender/scripted: it builds, its walls stay in its shell and out of
    its cores."""

    def test_every_rough_entry_builds_inside_its_shell(self):
        for plan, r in rough_entries():
            self.assertEqual(rough.check(r), [], plan)
            floors = rough.floors(r)
            cores = [b["ring"] for f in floors for b in f["blocks"]]
            for f in floors:
                for w, p in pieces(f):
                    m = mid(p)
                    self.assertTrue(geom.inside(f["inside"], *m), f"{plan}: {w['name']}")
                    if "lining" not in w["name"]:
                        for ring in cores:
                            self.assertFalse(geom.inside(ring, *m), f"{plan}: {w['name']}")
                for b in f["blocks"]:
                    for x, y in b["ring"]:
                        self.assertTrue(geom.inside(f["inside"], x, y), f"{plan}: {b['name']}")
                for lab in f["rooms"]:
                    self.assertTrue(geom.inside(f["inside"], *lab["at"]), f"{plan}: {lab}")
            by_level = {f["level"]: f for f in floors}
            for level, route in rough.routes(r):
                walkable(
                    self,
                    by_level[level],
                    route,
                    f"{plan}: entrance on level {level}",
                    floors[0]["blocks"],
                )
