"""The CCOM correction list for the main model (blender/ccom_main_fixes.py): names it hides."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "blender"))

import ccom_main_fixes as fixes  # noqa: E402


class Plan(unittest.TestCase):
    def test_the_wrong_sign_text_and_the_conflicting_walls_are_hidden(self):
        names = [
            "Campus sign lettering",
            "Campus sign lettering.001",
            "Campus building ID sign panel (UNVERIFIED)",
            "dd_SOUTH0_back_wall",
            "dd_SOUTH0_back_base",
            "dd_SOUTH0_floor_terrazzo",
            "NG connector W wall",
            "NG connector N end wall (behind east facade)",
            "NG connector LED 1",
            "NG link ceiling",
            "NG 1F open floor connector terrazzo (gentle 1.5% slope down to",
            "NG atrium N wall (tower face)",
        ]
        hidden = [n for n, _why in fixes.plan(names)]
        self.assertEqual(
            hidden,
            [
                "Campus sign lettering",
                "Campus sign lettering.001",
                "dd_SOUTH0_back_wall",
                "dd_SOUTH0_back_base",
                "NG connector W wall",
                "NG connector N end wall (behind east facade)",
                "NG connector LED 1",
                "NG link ceiling",
            ],
        )

    def test_every_change_gives_a_reason(self):
        for _pattern, why in fixes.HIDE:
            self.assertGreater(len(why), 20)


if __name__ == "__main__":
    unittest.main()
