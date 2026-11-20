"""The Alumni Green corrections to the main model (blender/alumni_green_fixes.py): pure geometry."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "blender"))

import alumni_green_fixes as g  # noqa: E402


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def area(ring):
    return 0.5 * abs(
        sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:] + ring[:1], strict=True))
    )


class Band(unittest.TestCase):
    def setUp(self):
        self.outer, self.inner = g.band_rings()

    def test_four_tips_reach_the_tip_radius_and_the_rest_lies_on_the_circles(self):
        r = sorted(dist(p, g.C) for p in self.outer)
        self.assertEqual(sum(abs(x - g.BAND_TIP) < 1e-6 for x in r), 4)
        for x in r:
            self.assertTrue(abs(x - g.BAND_OUT) < 1e-6 or abs(x - g.BAND_TIP) < 1e-6, x)
        for p in self.inner:
            self.assertAlmostEqual(dist(p, g.C), g.BAND_IN, places=6)

    def test_tips_sit_on_the_diagonals_of_the_gable_axis(self):
        tips = [p for p in self.outer if abs(dist(p, g.C) - g.BAND_TIP) < 1e-6]
        want = sorted((g.ANG + a) % 360 for a in (45, 135, 225, 315))
        got = sorted(math.degrees(math.atan2(p[1] - g.C[1], p[0] - g.C[0])) % 360 for p in tips)
        for a, b in zip(got, want, strict=True):
            self.assertAlmostEqual(a, b, places=6)

    def test_band_area_is_the_ring_plus_four_tips(self):
        ring = math.pi * (g.BAND_OUT**2 - g.BAND_IN**2)
        got = area(self.outer) - area(self.inner)
        self.assertGreater(got, ring * 0.99)
        self.assertLess(got, ring + 4 * g.BAND_TIP * g.BAND_OUT * math.radians(g.TIP_HALF))

    def test_the_rebuilt_square_holds_the_band_and_stays_inside_the_paver_field(self):
        x0, y0, x1, y1 = g.hole_square()
        self.assertTrue(all(float(v).is_integer() for v in (x0, y0, x1, y1)))
        for p in self.outer:
            self.assertTrue(x0 < p[0] < x1 and y0 < p[1] < y1)
        for p in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
            self.assertLess(dist(p, g.C), g.R - g.RING)


class Inlay(unittest.TestCase):
    def test_bent_text_follows_the_arc_and_reads_clockwise_for_a_reader_facing_out(self):
        th = math.radians(g.ANG + 90)
        p0 = g.bend(0, 0, g.INLAY_R, th)
        self.assertAlmostEqual(dist(p0, g.C), g.INLAY_R, places=6)
        p1 = g.bend(1.0, 0, g.INLAY_R, th)
        self.assertAlmostEqual(dist(p1, g.C), g.INLAY_R, places=6)
        # moving along the text turns clockwise seen from above
        a0 = math.atan2(p0[1] - g.C[1], p0[0] - g.C[0])
        a1 = math.atan2(p1[1] - g.C[1], p1[0] - g.C[0])
        self.assertLess(a1, a0)
        self.assertAlmostEqual(dist(g.bend(0, 0.2, g.INLAY_R, th), g.C), g.INLAY_R + 0.2)

    def test_panel_lies_in_the_brick_edge_course(self):
        self.assertGreaterEqual(g.INLAY_R - g.INLAY_DEPTH / 2, g.R - g.RING - 1e-9)
        self.assertLessEqual(g.INLAY_R + g.INLAY_DEPTH / 2, g.R + 1e-9)

    def test_panel_strip_has_two_rows_of_points_on_the_arc(self):
        pts = g.arc_strip(g.INLAY_R, g.INLAY_DEPTH, math.radians(g.ANG + 90), g.INLAY_LEN, 0.1)
        n = len(pts) // 2
        self.assertGreaterEqual(n, int(g.INLAY_LEN / 0.1))
        for p in pts[:n]:
            self.assertAlmostEqual(dist(p, g.C), g.INLAY_R - g.INLAY_DEPTH / 2, places=6)
        for p in pts[n:]:
            self.assertAlmostEqual(dist(p, g.C), g.INLAY_R + g.INLAY_DEPTH / 2, places=6)
        chord = dist(pts[0], pts[n - 1])
        self.assertAlmostEqual(chord, 2 * (g.INLAY_R - g.INLAY_DEPTH / 2) * math.sin(
            g.INLAY_LEN / (2 * g.INLAY_R)), places=6)


class Places(unittest.TestCase):
    def test_hatch_inside_the_field_lamp_outside_the_plaza(self):
        p = g.places()
        hx, hy, _ = p["hatch"]
        self.assertLess(dist((hx, hy), g.C) + math.hypot(*g.HATCH) / 2, g.R - g.RING)
        self.assertGreater(dist((hx, hy), g.C) - math.hypot(*g.HATCH) / 2, g.BAND_TIP)
        lx, ly, _ = p["lamp"]
        self.assertGreater(dist((lx, ly), g.C), g.R + 0.3)
        # the lamp stands west of the inlay, the hatch between them (Joe's photos 1 and 2)
        ix, iy, _ = p["inlay"]
        self.assertLess(lx, ix)
        self.assertTrue(lx < hx < ix)


if __name__ == "__main__":
    unittest.main()
