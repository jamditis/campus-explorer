"""Building options for the College of Communication and Media shell (massing.py): a tiled ring
roof with a crest set in from the walls and no slope on listed edges, wall openings, window rows at
given floor levels."""

import json
import math
import sys
import unittest
from pathlib import Path

PLAN = Path(__file__).resolve().parents[2] / "blender" / "scripted"
sys.path.insert(0, str(PLAN))

import geom  # noqa: E402
import massing  # noqa: E402

SQ = [(0, 0), (20, 0), (20, 20), (0, 20)]


def _normal(face):
    """Newell normal of a face (x, y, z) list: outward for anticlockwise-from-outside winding."""
    nx = ny = nz = 0.0
    for (x0, y0, z0), (x1, y1, z1) in zip(face, face[1:] + face[:1], strict=True):
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    return nx, ny, nz


class RingRoof(unittest.TestCase):
    def test_inset_rings_follow_each_edge_and_stay_on_flat_edges(self):
        crest = massing.inset(SQ, [7.0, 7.0, 0.0, 7.0])  # edge 2 (the north wall) is shared
        self.assertEqual(len(crest), 4)
        self.assertAlmostEqual(crest[0][0], 7.0)
        self.assertAlmostEqual(crest[0][1], 7.0)
        self.assertAlmostEqual(crest[2][1], 20.0)  # on the north wall: no slope there
        self.assertAlmostEqual(crest[3][0], 7.0)

    def test_slopes_rise_from_the_eave_to_the_crest_and_look_outward(self):
        faces = massing.ring_roof(SQ, 147.7, 151.1, 7.0, 8.0, 147.5)
        slopes = [f for f in faces if {round(p[2], 2) for p in f} == {147.7, 151.1}]
        self.assertEqual(len(slopes), 4)
        for f in slopes:
            n = _normal(f)
            self.assertGreater(n[2], 0)  # faces up
        # the south slope looks south
        south = [f for f in slopes if min(p[1] for p in f) == 0][0]
        self.assertLess(_normal(south)[1], 0)
        # the crest band and the drop to the flat roof inside
        crest = [f for f in faces if {round(p[2], 2) for p in f} == {151.1}]
        drops = [f for f in faces if {round(p[2], 2) for p in f} == {151.1, 147.5}]
        self.assertEqual(len(crest), 4)
        self.assertEqual(len(drops), 4)

    def test_a_flat_edge_gets_no_slope_and_closes_the_ring_ends(self):
        faces = massing.ring_roof(SQ, 147.7, 151.1, 7.0, 8.0, 147.5, flat_edges=[2])
        north = [f for f in faces if all(abs(p[1] - 20) < 1e-6 for p in f)]
        # only end caps lie in the north wall plane, and they are vertical
        for f in north:
            self.assertAlmostEqual(_normal(f)[2], 0.0, places=6)
            self.assertGreater(_normal(f)[1], 0)  # looking north, out of the building
        self.assertEqual(len(north), 2)
        sloped = [f for f in faces if {round(p[2], 2) for p in f} == {147.7, 151.1}]
        self.assertEqual(len(sloped), 3)

    def test_nearly_straight_corners_do_not_run_off(self):
        # a free edge that carries on almost straight from a flat one: the moved corner stays at
        # the free edge's own start, not where the two nearly parallel lines meet far away
        ring = [(0, 0), (20, 0), (20, 20), (10, 20.5), (0, 20)]
        c = massing.inset(ring, [5.0, 5.0, 0.0, 5.0, 5.0])
        for x, y in c:
            self.assertTrue(-1 <= x <= 21 and -1 <= y <= 21, (x, y))

    def test_each_edge_may_set_its_own_crest_distance(self):
        faces = massing.ring_roof(SQ, 10.0, 13.0, [3.0, 3.0, 5.0, 3.0], [4.0, 4.0, 6.0, 4.0], 9.8)
        north = [f for f in faces if {round(p[2], 2) for p in f} == {10.0, 13.0}
                 and all(p[1] == 20 for p in f if p[2] == 10.0)]  # fmt: skip
        self.assertEqual(min(p[1] for p in north[0]), 15.0)

    def test_an_overhang_carries_the_slope_past_the_wall(self):
        faces = massing.ring_roof(SQ, 10.0, 13.0, 3.0, 4.0, 9.8, overhang=[1.0, 0.0, 0.0, 0.0])
        south = [f for f in faces if min(p[1] for p in f) < -0.5]
        self.assertTrue(south)
        low = min(p[2] for f in south for p in f)
        self.assertAlmostEqual(low, 9.0)  # 1 m out at the slope of 1 m per metre
        self.assertAlmostEqual(min(p[1] for f in south for p in f), -1.0)

    def test_caps_run_along_the_crest_and_up_the_hips(self):
        caps = massing.ring_caps(SQ, 10.0, 13.0, 3.0, width=0.3, height=0.15)
        self.assertEqual(len(caps), 8)  # four crest runs, four hips
        for verts, _faces in caps:
            self.assertEqual(len(verts), 8)
            self.assertTrue(all(z >= 10.0 - 1e-9 for _x, _y, z in verts))

    def test_an_eave_course_runs_along_the_listed_walls_only(self):
        beams = massing.eave_course(SQ, [1, 2], 10.0, width=0.45, height=0.2)
        self.assertEqual(len(beams), 2)
        for verts, _f in beams:  # edges 1 and 2: the east and north walls, nothing elsewhere
            for x, y, _z in verts:
                self.assertTrue(x > 19.7 or y > 19.7, (x, y))

    def test_rings_must_nest(self):
        with self.assertRaises(ValueError):
            massing.ring_roof(SQ, 147.7, 151.1, 9.0, 8.0, 147.5)  # inner band outside the crest


class Openings(unittest.TestCase):
    def test_a_wall_with_an_opening_is_cut_round_it(self):
        pieces = massing.wall_pieces(10.0, 100.0, 110.0, [(3.0, 5.0, 100.0, 104.0)])
        area = sum((s1 - s0) * (z1 - z0) for s0, s1, z0, z1 in pieces)
        self.assertAlmostEqual(area, 100.0 - 8.0)
        for s0, s1, z0, z1 in pieces:  # nothing inside the opening
            self.assertFalse(s0 < 4.0 < s1 and z0 < 102.0 < z1)

    def test_no_openings_is_one_piece(self):
        self.assertEqual(massing.wall_pieces(10.0, 0.0, 3.0, []), [(0.0, 10.0, 0.0, 3.0)])

    def test_openings_are_found_on_the_ring_edge_they_lie_on(self):
        ops = massing.edge_openings(SQ, [dict(at=[0, 15], to=[0, 5], z0=1.0, z1=4.0)])
        self.assertEqual(list(ops), [3])
        (s0, s1, z0, z1), = ops[3]
        self.assertAlmostEqual(s0, 5.0)  # edge 3 runs from (0, 20) to (0, 0)
        self.assertAlmostEqual(s1, 15.0)
        with self.assertRaises(ValueError):
            massing.edge_openings(SQ, [dict(at=[5, 5], to=[6, 6], z0=0, z1=1)])


class WindowCells(unittest.TestCase):
    def test_cells_sit_on_bays_and_floor_levels_of_the_listed_edges(self):
        cells = massing.window_cells(
            SQ, lambda x, y: 0.0, wall_top=10.0, width=2.0, height=2.0, spacing=4.0, sill=0.9,
            levels=[0.0, 4.0], edges=[0],
        )  # fmt: skip
        self.assertEqual({c["edge"] for c in cells}, {0})
        self.assertEqual(sorted({c["z0"] for c in cells}), [0.9, 4.9])
        self.assertEqual(len(cells), 2 * len(massing.bays(20.0, 4.0)))
        for c in cells:
            self.assertAlmostEqual(c["s1"] - c["s0"], 2.0)


class WindowLevels(unittest.TestCase):
    def test_rows_stand_on_the_given_floors_and_skip_rows_below_ground(self):
        rows = massing.window_rows(147.7, 137.2, 2.6, 0.9, levels=[134.85, 137.40, 141.85])
        self.assertEqual([z0 for z0, _ in rows], [137.40 + 0.9, 141.85 + 0.9])
        self.assertTrue(all(abs(z1 - z0 - 2.6) < 1e-9 for z0, z1 in rows))
        rows = massing.window_rows(147.7, 134.6, 2.6, 0.9, levels=[134.85, 137.40, 141.85])
        self.assertEqual(len(rows), 3)

    def test_without_levels_rows_count_down_from_the_wall_top(self):
        h = massing.storey(12.0, 0.0, 3)
        self.assertEqual(
            massing.window_rows(12.0, 0.0, 1.5, 0.9, floors=3, storey_h=h),
            [(12.0 - (f + 1) * h + 0.9, 12.0 - (f + 1) * h + 2.4) for f in range(3)],
        )

    def test_a_row_whose_head_passes_the_wall_top_is_left_out(self):
        self.assertEqual(
            massing.window_rows(10.0, 0.0, 2.6, 0.9, levels=[0.0, 7.0]), [(0.9, 0.9 + 2.6)]
        )

    def test_explicit_rows_keep_their_own_heights_and_the_same_ground_rule(self):
        rows = [(135.3, 137.0), (137.5, 140.1), (141.7, 144.3)]
        self.assertEqual(massing.window_rows(147.8, 134.6, 2.6, 0.9, rows=rows), rows)
        # a higher ground drops the basement row; rows win over levels
        got = massing.window_rows(147.8, 136.7, 2.6, 0.9, levels=[134.85], rows=rows)
        self.assertEqual(got, rows[1:])

    def test_ccom_east_rows_line_up_with_the_adopted_south_windows(self):
        shell = json.loads((PLAN / "ccom" / "ccom_shell.json").read_text())["buildings"][0]
        rows = shell["windows"]["rows"]
        # the adopted window units on the south face: glass 137.5..140.1 and 141.7..144.3
        self.assertIn([137.5, 140.1], rows)
        self.assertIn([141.7, 144.3], rows)
        for (_a0, a1), (b0, _b1) in zip(rows, rows[1:], strict=False):
            self.assertLess(a1, b0)  # rows never run into each other


class PlanRings(unittest.TestCase):
    def test_inset_keeps_the_outline_sense(self):
        crest = massing.inset(SQ, [2.0] * 4)
        self.assertGreater(geom.area(crest), 0)
        self.assertAlmostEqual(geom.area(crest), 16 * 16)
        self.assertTrue(math.isfinite(crest[0][0]))


class CcomShellPlan(unittest.TestCase):
    """The shell part of blender/scripted/ccom: openings on edges, a ring roof that nests."""

    @classmethod
    def setUpClass(cls):
        import layout

        cls.part = [
            b
            for b in layout.load(Path(massing.__file__).parent / "ccom")["buildings"]
            if b["name"] == "CCOM_main"
        ][0]

    def test_outline_runs_anticlockwise_and_every_opening_lies_on_an_edge(self):
        ring = [tuple(p) for p in self.part["ring"]]
        self.assertGreater(geom.area(ring), 2000)
        ops = massing.edge_openings(ring, self.part["openings"])
        # the loading dock's two doors on the south wall, and the tower's line (its own part)
        self.assertEqual(sorted(ops), [2, 15])
        arches = massing.edge_openings(ring, self.part["arches"])
        self.assertEqual(sorted(arches), [14, 17, 19])  # west facade windows and the main entry
        self.assertEqual(sorted(massing.edge_openings(ring, self.part["curtains"])), [7])

    def test_the_ring_roof_stays_inside_the_walls_and_below_the_crest(self):
        ring = [tuple(p) for p in self.part["ring"]]
        r = self.part["ring_roof"]
        faces = massing.ring_roof(
            ring, self.part["top"], r["crest"], r["crest_in"], r["inner_in"],
            self.part["top"] - self.part["parapet"], r["flat_edges"], overhang=r.get("overhang"),
        )  # fmt: skip
        grown = geom.offset(ring, -max(r.get("overhang") or [0]) - 0.01, True)
        for f in faces:
            for x, y, z in f:
                self.assertTrue(geom.inside(grown, x, y), (x, y))
                self.assertTrue(147.0 <= z <= r["crest"] + 1e-9)


if __name__ == "__main__":
    unittest.main()


class CurtainWalls(unittest.TestCase):
    def test_a_window_cell_across_an_opening_is_left_out(self):
        cells = [
            dict(edge=7, s0=1.0, s1=3.0, z0=138.0, z1=140.0),
            dict(edge=7, s0=4.0, s1=6.0, z0=138.0, z1=140.0),
            dict(edge=7, s0=4.0, s1=6.0, z0=135.3, z1=137.0),  # under the opening: kept
            dict(edge=5, s0=4.0, s1=6.0, z0=138.0, z1=140.0),  # another edge: kept
        ]
        holes = {7: [(2.9, 7.5, 138.3, 144.3)]}
        self.assertEqual(massing.clear_of(cells, holes), [cells[2], cells[3]])

    def test_bars_split_the_opening_into_equal_lights(self):
        bars = massing.curtain_bars(0.0, 4.0, 0.0, 6.0, cols=4, rows=3, bar=0.1)
        self.assertEqual(len(bars), 4 + 3 + 2)
        mullions = sorted((a + b) / 2 for a, b, za, zb in bars if zb - za == 6.0 and b - a < 1)
        self.assertEqual(mullions, [0.05, 1.0, 2.0, 3.0, 3.95])
        transoms = sorted((za + zb) / 2 for a, b, za, zb in bars if b - a == 4.0)
        self.assertEqual(transoms, [0.05, 2.0, 4.0, 5.95])

    def test_the_ccom_east_bay_window_lies_on_the_east_wall(self):
        shell = json.loads((PLAN / "ccom" / "ccom_shell.json").read_text())["buildings"][0]
        holes = massing.edge_openings(shell["ring"], shell["curtains"])
        self.assertEqual(list(holes), [7])


class Arches(unittest.TestCase):
    @staticmethod
    def area(poly):
        return sum(
            x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1], strict=True)
        ) / 2

    def test_opening_and_spandrels_fill_the_cut_rectangle(self):
        s0, s1, z0, z1 = 2.0, 5.0, 1.0, 8.0
        hole = massing.arch_outline(s0, s1, z0, z1, n=48)
        left, right = massing.arch_spandrels(s0, s1, z1, n=48)
        for poly in (hole, left, right):
            self.assertGreater(self.area(poly), 0)  # anticlockwise
        total = self.area(hole) + self.area(left) + self.area(right)
        self.assertAlmostEqual(total, (s1 - s0) * (z1 - z0), places=6)
        r = (s1 - s0) / 2  # the opening is a rectangle up to the springing line and a half disc
        self.assertAlmostEqual(self.area(hole), (s1 - s0) * (z1 - r - z0) + math.pi * r * r / 2, 1)

    def test_bars_stay_inside_the_opening(self):
        s0, s1, z0, z1 = 0.0, 3.0, 0.0, 7.0
        rects, head = massing.arch_bars(s0, s1, z0, z1, cols=3, rows=5)
        r, spring = 1.5, 5.5
        for sa, sb, _za, zb in rects:
            self.assertGreaterEqual(sa, s0 - 1e-9)
            self.assertLessEqual(sb, s1 + 1e-9)
            for s in (sa, sb):  # every bar's top stays under the head
                d = min(abs(s - 1.5), r)
                self.assertLessEqual(zb, spring + math.sqrt(r * r - d * d) + 0.05)
        self.assertEqual(len(head), 12)


class Soffits(unittest.TestCase):
    def test_only_overhanging_edges_get_a_soffit_and_a_fascia(self):
        faces = massing.ring_soffits(SQ, 10.0, 13.0, 6.0, overhang=[0.8, 0, 0.8, 0])
        self.assertEqual(len(faces), 4)
        low = 10.0 - 0.8 * 3.0 / 6.0
        soffit = faces[0]
        self.assertTrue(all(abs(z - low) < 1e-9 for _x, _y, z in soffit))
        self.assertAlmostEqual(min(z for f in faces for _x, _y, z in f), low - 0.35)

    def test_no_overhang_no_soffit(self):
        self.assertEqual(massing.ring_soffits(SQ, 10.0, 13.0, 6.0), [])
        self.assertEqual(massing.ring_eave_trim(SQ, 10.0, 13.0, 6.0), ([], []))

    def test_rafter_tails_and_a_tile_course_under_each_overhang(self):
        rafters, course = massing.ring_eave_trim(SQ, 10.0, 13.0, 6.0, overhang=[0.8, 0, 0.8, 0])
        self.assertEqual(len(course), 2)  # one course per overhanging edge
        self.assertEqual(len(rafters), 2 * (int(20.0 / 0.75) - 1))
        low = 10.0 - 0.8 * 3.0 / 6.0
        for verts, _faces in rafters:  # tucked under the soffit
            self.assertTrue(all(z <= low + 1e-9 for _x, _y, z in verts))


class Doors(unittest.TestCase):
    def test_a_leaf_turns_out_of_the_building(self):
        # a wall facing south (outward normal -y), a leaf from x 0 to 1 hinged at x 0:
        # +90 degrees would turn it north, into the building, so it opens by -90
        hinge, angle = massing.door_swing((0, 0), (1, 0), "at", (0, -1))
        self.assertEqual((hinge, angle), ((0, 0), -90))
        hinge, angle = massing.door_swing((0, 0), (1, 0), "to", (0, -1))
        self.assertEqual((hinge, angle), ((1, 0), 90))

    def test_every_ccom_leaf_lies_inside_its_entrance_and_pairs_open_together(self):
        shell = json.loads((PLAN / "ccom" / "ccom_shell.json").read_text())["buildings"][0]
        dr = shell["doors"]
        span = massing.edge_openings(shell["ring"], [dr])
        ((edge, (s0, s1, _z0, _z1)),) = [(e, h[0]) for e, h in span.items()]
        pairs = {}
        for lf in dr["leaves"]:
            self.assertTrue(lf["name"].startswith("DOOR_"))
            found = massing.edge_openings(shell["ring"], [dict(lf, z0=0, z1=1)])
            ((e, (a, b, _za, _zb)),) = [(k, h[0]) for k, h in found.items()]
            self.assertEqual(e, edge)
            self.assertTrue(s0 - 1e-6 <= a < b <= s1 + 1e-6)
            pairs.setdefault(lf["pair"], []).append(lf)
        self.assertTrue(all(len(v) == 2 for v in pairs.values()))


class EaveTrimOnTheShell(unittest.TestCase):
    def test_every_rafter_tail_ends_under_the_soffit(self):
        shell = json.loads((PLAN / "ccom" / "ccom_shell.json").read_text())["buildings"][0]
        r = shell["ring_roof"]
        ring = [tuple(p) for p in shell["ring"]]
        ov = [0.0 if k in r["flat_edges"] else v for k, v in enumerate(r["overhang"])]
        outer = massing.inset(ring, [-v for v in ov])
        n = len(ring)
        quads = [
            [ring[k], outer[k], outer[(k + 1) % n], ring[(k + 1) % n]]
            for k in range(n)
            if ov[k] > 0
        ]
        rafters, _course = massing.ring_eave_trim(
            ring, shell["top"], r["crest"], r["crest_in"], r["flat_edges"], overhang=r["overhang"]
        )
        self.assertTrue(rafters)
        for verts, _faces in rafters:
            # the tail's far end: its two corners furthest from the outline's centre
            cx = sum(p[0] for p in ring) / n
            cy = sum(p[1] for p in ring) / n
            far = sorted(verts, key=lambda p: -math.hypot(p[0] - cx, p[1] - cy))[:1]
            for x, y, _z in far:
                mid_ok = any(geom.inside(q, x, y) for q in quads)
                self.assertTrue(mid_ok, (x, y))
