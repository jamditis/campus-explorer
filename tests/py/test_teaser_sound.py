"""The pure parts of tools/teaser/sound/mix.py: anchors, fades, pan, envelopes, ducking, cues."""

import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOUND = ROOT / "tools" / "teaser" / "sound"
sys.path.insert(0, str(SOUND))

import mix  # noqa: E402

TL = {
    "fps": 30,
    "total": 20.0,
    "shots": [
        {"name": "ui", "start": 0.0, "duration": 5.0},
        {"name": "dawn", "start": 5.0, "duration": 10.0,
         "graphics": [{"id": "title", "kind": "text", "in": 2.0, "inDur": 1.0, "out": 8.0}]},
        {"name": "end", "start": 15.0, "duration": 5.0},
    ],
    "markers": {"glass": 7.25},
}


class Anchors(unittest.TestCase):
    def setUp(self):
        self.shots = mix.shot_table(TL, {"open": "ui"})
        self.gr = mix.graphic_table(TL)

    def test_shot_offsets(self):
        self.assertEqual(mix.resolve(["dawn", 1.5], self.shots), 6.5)
        self.assertEqual(mix.resolve(["dawn", "end"], self.shots), 15.0)
        self.assertEqual(mix.resolve(["dawn", "end-2"], self.shots), 13.0)
        self.assertEqual(mix.resolve(["dawn", "50%"], self.shots), 10.0)
        self.assertEqual(mix.resolve(3.0, self.shots), 3.0)

    def test_role_names_map_to_storyboard_names(self):
        self.assertEqual(mix.resolve(["open", "end"], self.shots), 5.0)

    def test_graphic_edges(self):
        self.assertEqual(mix.resolve({"graphic": "title"}, self.shots, self.gr), 7.0)
        land = {"graphic": "title", "edge": "land"}
        out = {"graphic": "title", "edge": "out", "offset": -1}
        self.assertAlmostEqual(mix.resolve(land, self.shots, self.gr), 7.85)
        self.assertEqual(mix.resolve(out, self.shots, self.gr), 12.0)

    def test_graphic_carried_into_a_later_shot_keeps_its_first_landing(self):
        tl = dict(TL, shots=TL["shots"] + [{"name": "after", "start": 20.0, "duration": 4.0,
                                             "graphics": [{"id": "title", "in": -5}]}])
        self.assertAlmostEqual(mix.graphic_table(tl)["title"]["land"], 7.85)

    def test_marker(self):
        at = {"marker": "glass", "offset": 0.25}
        self.assertEqual(mix.resolve(at, self.shots, self.gr, TL["markers"]), 7.5)

    def test_unknown_shot_fails(self):
        with self.assertRaises(KeyError):
            mix.resolve(["nope", 0], self.shots)


class Signal(unittest.TestCase):
    def test_equal_power_fades_sum_to_unit_power(self):
        a, b = mix.fade_curve(480, "in"), mix.fade_curve(480, "out")
        self.assertTrue(np.allclose(a ** 2 + b ** 2, 1.0, atol=1e-6))
        self.assertLess(a[0], 0.01)
        self.assertGreater(a[-1], 0.99)

    def test_pan_constant_power(self):
        for p in (-1, -0.3, 0, 0.7, 1):
            left, right = mix.pan_gains(p)
            self.assertAlmostEqual(left ** 2 + right ** 2, 1.0)
        self.assertAlmostEqual(mix.pan_gains(-1)[1], 0.0)

    def test_envelope_interpolates_in_db(self):
        g = mix.envelope(None, [[0, 0], [1, -20]], 48001)
        self.assertAlmostEqual(float(g[0]), 1.0, places=5)
        self.assertAlmostEqual(float(g[24000]), 10 ** (-10 / 20), places=4)
        self.assertAlmostEqual(float(g[-1]), 0.1, places=4)

    def test_duck_dips_only_while_key_is_loud(self):
        key = np.zeros(48000 * 3, np.float32)
        key[48000:48000 + 4800] = 0.5
        g = mix.duck_gain(key, 6.0)
        self.assertAlmostEqual(float(g[1000]), 1.0, places=4)
        self.assertLess(float(g[48000 + 4000]), 10 ** (-3 / 20))
        self.assertGreater(float(g[-1]), 0.99)
        self.assertGreaterEqual(float(g.min()), 10 ** (-6 / 20) - 1e-4)


class CueSheet(unittest.TestCase):
    def test_a_zero_db_duck_still_ducks(self):
        self.assertEqual(mix.duck_key({"duck": 0}), 1.0)
        self.assertAlmostEqual(mix.duck_key({"duck": -6}), 0.501, places=3)
        self.assertIsNone(mix.duck_key({}))

    def test_every_cue_names_a_known_source_and_bus(self):
        sheet = json.loads((SOUND / "cues.json").read_text())
        for c in sheet["cues"]:
            self.assertIn(c["key"], sheet["sources"], c)
            self.assertIn(c.get("bus", "fx"), mix.BUSES, c)
            self.assertTrue("dur" in c or "until" in c, c)

    def test_every_source_is_credited(self):
        sheet = json.loads((SOUND / "cues.json").read_text())
        credits = (SOUND / "CREDITS.md").read_text()
        used = {c["key"] for c in sheet["cues"] if not c.get("off")}
        for k in used:
            self.assertIn(f"`{k}`", credits, k)

    def test_default_shots_resolve_every_anchor(self):
        sheet = json.loads((SOUND / "cues.json").read_text())
        tl = json.loads((SOUND / "shots.default.json").read_text())
        shots = mix.shot_table(tl, sheet.get("shots", {}))
        gr = mix.graphic_table(tl)
        for c in sheet["cues"]:
            mix.resolve(c["at"], shots, gr, tl.get("markers", {}))
            if "until" in c:
                mix.resolve(c["until"], shots, gr, tl.get("markers", {}))


if __name__ == "__main__":
    unittest.main()
