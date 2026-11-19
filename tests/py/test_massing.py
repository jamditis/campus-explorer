"""Roof shapes and window bays of building parts (blender/scripted/massing.py)."""

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

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
