"""The solid seating bowl: its row profile and its hand-wound block (stand.py, pure parts)."""

import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "blender" / "scripted"))

import stand  # noqa: E402

WALK = [0.6, 110.8]
TIERS = [{"rows": 5, "first": 111.0, "rise": 0.2}, {"rows": 10, "first": 113.1, "rise": 0.2}]
AISLES = [{"width": 2.5, "level": 112.2}]


class BowlProfile(unittest.TestCase):
    def test_walk_rows_aisle_rows_back(self):
        flats = stand.bowl_profile(WALK, TIERS, AISLES, back=115.5, depth=17.0, tread=0.85)
        kinds = [f["kind"] for f in flats]
        self.assertEqual(kinds, ["walk"] + ["row"] * 5 + ["aisle"] + ["row"] * 10 + ["back"])
        self.assertEqual(flats[0]["v"], (0.0, 0.6))
        self.assertAlmostEqual(flats[5]["level"], 111.8)
        aisle = flats[6]
        self.assertAlmostEqual(aisle["v"][0], 0.6 + 5 * 0.85)
        self.assertAlmostEqual(aisle["v"][1] - aisle["v"][0], 2.5)
        self.assertAlmostEqual(aisle["level"], 112.2)
        self.assertAlmostEqual(flats[7]["level"], 113.1)
        self.assertAlmostEqual(flats[-2]["level"], 114.9)
        self.assertEqual(flats[-1]["level"], 115.5)
        self.assertAlmostEqual(flats[-1]["v"][1], 17.0)
        # rows are numbered through both tiers, the aisle and walkways carry no row number
        self.assertEqual([f["row"] for f in flats if f["kind"] == "row"], list(range(15)))
        self.assertEqual([f["tier"] for f in flats if f["kind"] == "row"], [0] * 5 + [1] * 10)
        for a, b in zip(flats, flats[1:], strict=False):  # contiguous from the front to the back
            self.assertAlmostEqual(a["v"][1], b["v"][0])

    def test_no_back_flat_when_the_rows_fill_the_depth(self):
        depth = 0.6 + 15 * 0.85 + 2.5
        flats = stand.bowl_profile(WALK, TIERS, AISLES, back=115.5, depth=depth, tread=0.85)
        self.assertEqual(flats[-1]["kind"], "row")

    def test_refuses_rows_past_the_depth_and_a_missing_aisle(self):
        with self.assertRaises(ValueError):
            stand.bowl_profile(WALK, TIERS, AISLES, back=115.5, depth=14.0, tread=0.85)
        with self.assertRaises(ValueError):
            stand.bowl_profile(WALK, TIERS, [], back=115.5, depth=17.0, tread=0.85)


def closed_and_outward(verts, faces):
    """Every edge used once each way (a closed, consistently wound shell) and the signed volume."""
    edges = Counter()
    for f in faces:
        for i in range(len(f)):
            edges[(f[i], f[(i + 1) % len(f)])] += 1
    closed = all(n == 1 and edges.get((b, a)) == 1 for (a, b), n in edges.items())
    vol = 0.0
    for f in faces:
        a = verts[f[0]]
        for i in range(1, len(f) - 1):
            b, c = verts[f[i]], verts[f[i + 1]]
            vol += (
                a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])
            ) / 6
    return closed, vol


class BowlBlock(unittest.TestCase):
    def profile_area(self, flats, base):
        return sum((f["v"][1] - f["v"][0]) * (f["level"] - base) for f in flats)

    def test_block_is_closed_and_wound_outward(self):
        flats = stand.bowl_profile(WALK, TIERS, AISLES, back=115.5, depth=17.0, tread=0.85)
        verts, faces = stand.bowl_block(12.0, flats, base=109.3)
        closed, vol = closed_and_outward(verts, faces)
        self.assertTrue(closed)
        self.assertAlmostEqual(vol, 12.0 * self.profile_area(flats, 109.3), places=6)

    def test_a_step_down_is_closed_too(self):
        flats = stand.bowl_profile(
            [1.0, 111.5],
            [{"rows": 1, "first": 111.7, "rise": 0.2}, TIERS[1]],
            [{"width": 2.0, "level": 111.6}],
            back=115.0,
            depth=14.0,
            tread=0.85,
        )
        verts, faces = stand.bowl_block(5.0, flats, base=109.3)
        closed, vol = closed_and_outward(verts, faces)
        self.assertTrue(closed)
        self.assertAlmostEqual(vol, 5.0 * self.profile_area(flats, 109.3), places=6)

    def test_few_faces(self):
        flats = stand.bowl_profile(WALK, TIERS, AISLES, back=115.5, depth=17.0, tread=0.85)
        _, faces = stand.bowl_block(12.0, flats, base=109.3)
        # a tread and a riser per flat, one end strip each side per flat, front, back and bottom
        self.assertLessEqual(len(faces), 4 * len(flats) + 3)


class SeatRows(unittest.TestCase):
    def test_seat_spec_by_row_range_and_section(self):
        seats = [
            {"rows": [0, 4], "type": "chairs", "colour": "#a3322c"},
            {"rows": [5, 14], "type": "bench", "sections": [1]},
        ]
        self.assertEqual(stand.seat_for(seats, 3, 0)["type"], "chairs")
        self.assertEqual(stand.seat_for(seats, 7, 1)["type"], "bench")
        self.assertIsNone(stand.seat_for(seats, 7, 0))
        self.assertIsNone(stand.seat_for([], 0, 0))


if __name__ == "__main__":
    unittest.main()
