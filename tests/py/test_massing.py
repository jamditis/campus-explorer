"""Roof shapes and window bays of building parts (blender/scripted/massing.py)."""

import json
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import geom  # noqa: E402
import massing  # noqa: E402

RECT = [(0, 0), (30, 0), (30, 10), (0, 10)]


def normal_z(face):
    """Z of the face normal (Newell): positive when the face is anticlockwise seen from above."""
    return sum(
        (a[0] - b[0]) * (a[1] + b[1]) for a, b in zip(face, face[1:] + face[:1], strict=True)
    )


class Roofs(unittest.TestCase):
    def test_flat_roof_has_level_walls_and_no_faces(self):
        tops, slopes, gables = massing.roof(RECT, "flat", 50.0)
        self.assertEqual(tops, [50.0] * 4)
        self.assertEqual((slopes, gables), ([], []))

    def test_gable_ridge_runs_along_the_long_side_at_the_top_height(self):
        tops, slopes, gables = massing.roof(RECT, "gable", 54.0, eave=50.0)
        self.assertEqual(tops, [50.0] * 4)
        self.assertEqual((len(slopes), len(gables)), (2, 2))
        ridge = sorted({p for f in slopes for p in f if p[2] == 54.0})
        self.assertEqual(ridge, [(0.0, 5.0, 54.0), (30.0, 5.0, 54.0)])
        for f in slopes:
            self.assertGreater(normal_z(f), 0, "roof faces look up")

    def test_gable_ridge_follows_the_given_angle(self):
        _tops, slopes, _g = massing.roof(RECT, "gable", 54.0, eave=50.0, ridge_angle=90.0)
        ridge = sorted({p for f in slopes for p in f if p[2] == 54.0})
        self.assertEqual(ridge, [(15.0, 0.0, 54.0), (15.0, 10.0, 54.0)])

    def test_hip_ridge_is_shorter_by_the_half_width_at_each_end(self):
        _tops, slopes, gables = massing.roof(RECT, "hip", 54.0, eave=50.0)
        self.assertEqual(gables, [])
        ridge = sorted({p for f in slopes for p in f if p[2] == 54.0})
        self.assertEqual(ridge, [(5.0, 5.0, 54.0), (25.0, 5.0, 54.0)])
        self.assertEqual(len(slopes), 4)
        for f in slopes:
            self.assertGreater(normal_z(f), 0)

    def test_square_hip_is_a_pyramid(self):
        sq = [(0, 0), (10, 0), (10, 10), (0, 10)]
        _tops, slopes, _g = massing.roof(sq, "hip", 54.0, eave=50.0)
        self.assertTrue(all(len(f) == 3 for f in slopes))
        self.assertEqual({p for f in slopes for p in f if p[2] == 54.0}, {(5.0, 5.0, 54.0)})

    def _eaves_ok(self, ring, kind, top, eave, ridge_angle=None, d=1.0, convex=True):
        _tops, slopes, _gables = massing.roof(ring, kind, top, eave, ridge_angle)
        eaves = massing.overhang_roof(ring, slopes, d)
        self.assertTrue(eaves, kind)
        for face in eaves:
            self.assertGreater(normal_z(face), 0, "faces up")
            # each eave face lies in the plane of a roof face it touches along the wall line
            fits = []
            for s_face in slopes:
                z, _n = massing._plane(s_face)
                fits.append(max(abs(z(x, y) - q) for x, y, q in face))
            self.assertLess(min(fits), 1e-6, f"{kind}: an eave face leaves its roof plane")
        # where eave faces meet off the wall line they meet at one height: no step
        heights = {}
        for face in eaves:
            for x, y, z in face:
                heights.setdefault((round(x, 5), round(y, 5)), []).append(z)
        for zs in heights.values():
            self.assertLess(max(zs) - min(zs), 1e-6, kind)
        if convex:  # roof and eaves together cover the outline moved out, once
            plan = sum(abs(geom.area([q[:2] for q in f])) for f in slopes + eaves)
            self.assertAlmostEqual(plan, abs(geom.area(geom.offset(ring, -d, True))), 6)
        return slopes, eaves

    def test_an_overhang_carries_each_face_out_in_its_own_plane(self):
        for kind in ("hip", "gable"):
            self._eaves_ok(RECT, kind, 18.0, 12.0)
        # a hip with its ridge across the short side: long and end faces of different pitch
        self._eaves_ok(RECT, "hip", 18.0, 12.0, ridge_angle=90)
        # a narrow mansard, its slopes steeper than 45 degrees; an L-shaped one with a reflex corner
        self._eaves_ok([(0, 0), (30, 0), (30, 2), (0, 2)], "hip", 18.0, 12.0)
        ell = [(0, 0), (30, 0), (30, 2), (15, 2), (15, 4), (0, 4)]
        self._eaves_ok(ell, "hip", 18.0, 12.0, convex=False)

    def test_an_overhang_leaves_a_mansard_top_and_its_wells_alone(self):
        ring = [(0, 0), (20, 0), (20, 20), (10, 26), (0, 20)]
        slopes, eaves = self._eaves_ok(ring, "hip", 30.0, 26.0)
        cap = slopes[-1]
        for face in eaves:  # nothing reaches in to the flat top
            for x, y, _z in face:
                self.assertFalse(geom.inside([q[:2] for q in cap], x, y))

    def test_shed_is_high_on_the_left_of_the_ridge_direction(self):
        tops, slopes, _g = massing.roof(RECT, "shed", 53.0, eave=50.0, ridge_angle=0.0)
        self.assertEqual(tops, [50.0, 50.0, 53.0, 53.0])  # ridge runs east: north side is high
        self.assertEqual(len(slopes), 1)

    def test_other_outlines_get_a_mansard_inside_the_outline(self):
        ell = [(0, 0), (30, 0), (30, 10), (12, 10), (12, 24), (0, 24)]
        tops, slopes, _g = massing.roof(ell, "hip", 53.0, eave=50.0)
        self.assertEqual(tops, [50.0] * 6)
        cap = slopes[-1]
        self.assertTrue(all(p[2] == 53.0 for p in cap))
        self.assertTrue(all(0 < p[0] < 30 and 0 < p[1] < 24 for p in cap))

    def test_mansard_gives_up_gently_on_a_narrow_part(self):
        thin = [(0, 0), (30, 0), (30, 2), (0, 2)]
        inner = massing.mansard(thin, 6.0)
        self.assertTrue(all(0 < p[1] < 2 for p in inner), "moved in, by less than the rise")
        self.assertLess(max(p[1] for p in inner) - min(p[1] for p in inner), 2)

    def test_pitched_roof_without_an_eave_is_an_error(self):
        with self.assertRaises(ValueError):
            massing.roof(RECT, "gable", 54.0)


def tri_area(pts, tri):
    a, b, c = (pts[i] for i in tri)
    return ((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2


def ring_area(ring):
    return normal_z(ring) / 2


class Wells(unittest.TestCase):
    def check_cover(self, outer, holes):
        tris = massing.deck_triangles(outer, holes)
        pts = list(outer) + [p for h in holes for p in h]
        for t in tris:
            self.assertGreater(tri_area(pts, t), 1e-6, "every triangle looks up, none is flat")
        want = ring_area(outer) - sum(abs(ring_area(h)) for h in holes)
        self.assertAlmostEqual(sum(tri_area(pts, t) for t in tris), want, places=6)
        return tris, pts

    def test_deck_without_holes_is_the_outline(self):
        tris, _pts = self.check_cover(RECT, [])
        self.assertEqual(len(tris), 2)

    def test_deck_with_a_well_leaves_the_well_open(self):
        hole = [(5, 3), (12, 3), (12, 7), (5, 7)]
        tris, pts = self.check_cover(RECT, [hole])
        self.assertEqual(len(tris), 4 + 4 + 2 - 2)  # n + h + 2 per hole - 2
        for t in tris:  # no triangle covers the middle of the well
            cx = sum(pts[i][0] for i in t) / 3
            cy = sum(pts[i][1] for i in t) / 3
            self.assertFalse(5 < cx < 12 and 3 < cy < 7)

    def test_deck_takes_a_concave_outline_and_two_wells_of_either_sense(self):
        ell = [(0, 0), (30, 0), (30, 10), (12, 10), (12, 24), (0, 24)]
        a = [(2, 2), (8, 2), (8, 8), (2, 8)]
        b = [(3, 20), (9, 20), (9, 14), (3, 14)]  # clockwise
        self.check_cover(ell, [a, b])

    def test_a_cut_to_one_well_does_not_pass_through_another(self):
        # the corners nearest the east well are in the west, behind the west well
        long = [(0, 0), (200, 5), (0, 10)]
        east = [(20, 4.5), (24, 4.5), (24, 5.5), (20, 5.5)]
        west = [(5, 2), (15, 2), (15, 8), (5, 8)]
        self.check_cover(long, [east, west])

    def test_a_mansard_cap_with_a_rim_keeps_a_thin_deck(self):
        octagon = [(10, 0), (20, 0), (30, 10), (30, 20), (20, 30), (10, 30), (0, 20), (0, 10)]
        cap = massing.mansard(octagon, 3.0)
        well = massing.mansard(octagon, 3.5)
        massing.check_wells(cap, [well])
        self.check_cover(cap, [well])

    def test_wells_must_lie_inside_the_part_and_apart(self):
        inside = [(2, 2), (8, 2), (8, 8), (2, 8)]
        massing.check_wells(RECT, [inside])
        for bad in (
            [[(25, 2), (35, 2), (35, 8), (25, 8)]],  # crosses the outline
            [[(40, 2), (45, 2), (45, 8), (40, 8)]],  # outside
            [[(0, 2), (8, 2), (8, 8), (0, 8)]],  # on the outline: no deck left between
            [inside, [(6, 4), (12, 4), (12, 6), (6, 6)]],  # wells overlap
            [inside, [(3, 3), (4, 3), (4, 4), (3, 4)]],  # one well inside another
        ):
            with self.assertRaises(ValueError):
                massing.check_wells(RECT, bad)

    def test_a_well_round_a_concave_corner_is_refused(self):
        ell = [(0, 0), (40, 0), (40, 10), (10, 10), (10, 40), (0, 40)]
        with self.assertRaises(ValueError):
            massing.check_wells(ell, [[(8, 8), (12, 9.6), (9.6, 12)]])

    def test_every_plan_well_lies_inside_its_deck(self):
        for path in sorted((ROOT / "blender" / "scripted").glob("*/*.json")):
            plan = json.loads(path.read_text())
            for p in plan.get("buildings", []):
                if not p.get("wells"):
                    continue
                ring = geom.expand(p["ring"], True)
                ring = ring if geom.area(ring) > 0 else ring[::-1]
                deck = massing.well_deck(
                    ring, p.get("roof", "flat"), p["top"], p.get("eave"), p.get("ridge_angle")
                )
                with self.subTest(part=p["name"]):
                    self.assertIsNotNone(deck, "wells need a flat roof or a mansard top")
                    wells = [geom.expand(w["ring"], True) for w in p["wells"]]
                    massing.check_wells(deck, wells)
                    # the same limit as building._deck: under the roof deck, which lies a
                    # parapet below the top on a flat roof
                    flat = p.get("roof", "flat") == "flat"
                    drop = massing.PARAPET.get(p.get("style", "shed"), 0.4) if flat else 0.0
                    self.assertTrue(all(w["floor"] < p["top"] - drop - 0.05 for w in p["wells"]))


class Facade(unittest.TestCase):
    def test_bays_are_centred_and_evenly_spaced(self):
        b = massing.bays(20.0, 3.0)
        self.assertEqual(len(b), 6)
        self.assertAlmostEqual(b[0], 20.0 - b[-1])
        self.assertTrue(all(math.isclose(b[i + 1] - b[i], 3.0) for i in range(5)))
        self.assertEqual(massing.bays(3.0, 3.0), [])

    def test_storey_height_stays_plausible(self):
        self.assertAlmostEqual(massing.storey(120.0, 102.0, 6), 3.0)
        self.assertEqual(massing.storey(120.0, 80.0, 3), 4.6)
        self.assertEqual(massing.storey(120.0, 118.0, 3), 2.7)


if __name__ == "__main__":
    unittest.main()
