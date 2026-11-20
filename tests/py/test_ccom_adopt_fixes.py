"""Fixes on adopted CCOM objects (blender/ccom_adopt_fixes.py): which faces go."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "blender"))

import ccom_adopt_fixes as fx  # noqa: E402


class LowFaces(unittest.TestCase):
    def test_faces_below_the_eave_band_go(self):
        cents = [(0, 0, 147.2), (1, 0, 145.5), (2, 0, 146.59), (3, 0, 146.61)]
        self.assertEqual(fx.low_faces(cents, 146.6), [1, 2])

    def test_every_rule_names_an_object_and_says_why(self):
        for name, below, why in fx.LOW:
            self.assertTrue(name and below > 140 and len(why) > 20)


if __name__ == "__main__":
    unittest.main()
