"""The rooms builder (tools/places/build_rooms.py): room labels and interior volumes for the viewer,
from the scripted interior plans, in the viewer frame (x east, y up, z = -model y)."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "places"))

import build_rooms  # noqa: E402

RING = [[0, 0], [20, 0], [20, 10], [0, 10]]


def floor(level, z, ceiling, rooms):
    return dict(
        name=f"T_F{level}",
        level=level,
        floor=z,
        ceiling=ceiling,
        unverified="positions from a sign",
        outline=RING,
        rooms=[dict(number=n, at=at) for n, at in rooms],
    )


PLAN = [
    floor(2, 104.0, 107.0, [("2001", [5, 5])]),
    floor(1, 100.0, 103.6, [("1001", [5, 5]), ("1002", [15, 2])]),
]
PLACES = [
    dict(name="Far Hall", kind="building", x=500, z=500),
    dict(name="Test Hall", kind="building", x=10, z=-5),
]
SHELL = [dict(name="T_main", ring=RING, top=110.5)]


class Build(unittest.TestCase):
    def setUp(self):
        self.out = build_rooms.area("t", PLAN, PLACES, SHELL, short={"Test Hall": "TH"})

    def test_the_volume_is_the_outline_in_the_viewer_frame_with_its_floor_levels(self):
        (vol,) = self.out["volumes"]
        self.assertEqual(vol["id"], "t")
        self.assertEqual(vol["building"], "Test Hall")
        self.assertEqual(vol["short"], "TH")
        self.assertEqual(vol["ring"], [[0, 0], [20, 0], [20, -10], [0, -10]])
        self.assertEqual(vol["levels"], [dict(floor=1, y=100.0), dict(floor=2, y=104.0)])
        self.assertEqual(vol["y0"], 100.0)
        self.assertEqual(vol["ceiling"], 107.0)  # the highest interior ceiling

    def test_the_volume_reaches_the_top_of_the_shell_that_holds_it(self):
        self.assertEqual(self.out["volumes"][0]["y1"], 110.5)
        alone = build_rooms.area("t", PLAN, PLACES, [])
        self.assertEqual(alone["volumes"][0]["y1"], 107.0)  # no shell: the highest ceiling

    def test_rooms_carry_their_floor_level_building_and_unverified_flag(self):
        rooms = {r["name"]: r for r in self.out["rooms"]}
        self.assertEqual(set(rooms), {"1001", "1002", "2001"})
        r = rooms["1002"]
        self.assertEqual((r["x"], r["z"], r["y"], r["floor"]), (15, -2, 100.0, 1))
        self.assertEqual(r["building"], "Test Hall")
        self.assertIs(r["unverified"], True)
        self.assertEqual(rooms["2001"]["y"], 104.0)

    def test_no_place_inside_the_outline_falls_back_to_the_area_name(self):
        out = build_rooms.area("t", PLAN, PLACES[:1], SHELL)
        self.assertEqual(out["volumes"][0]["building"], "t")
        self.assertEqual(out["volumes"][0]["short"], "")


class Published(unittest.TestCase):
    def test_the_viewer_file_holds_rooms_inside_their_volumes(self):
        data = json.loads((ROOT / "viewer" / "rooms.json").read_text())
        vols = {v["building"]: v for v in data["volumes"]}
        self.assertTrue(data["rooms"])
        for r in data["rooms"]:
            v = vols[r["building"]]
            self.assertIn(r["floor"], [lv["floor"] for lv in v["levels"]])
            self.assertTrue(build_rooms.inside(v["ring"], r["x"], r["z"]), r["name"])
            self.assertTrue(v["y0"] <= r["y"] < v["y1"])


class Exported(unittest.TestCase):
    """An interior plan reaches viewer/rooms.json only once its objects are in the tiles."""

    FLOORS = [dict(name="T_F1"), dict(name="T_F2")]

    def test_any_one_object_of_any_floor_is_enough(self):
        self.assertTrue(build_rooms.exported(self.FLOORS, {"SW_T_F2_slab_UNVERIFIED", "x"}))

    def test_a_plan_without_objects_in_the_tiles_is_left_out(self):
        self.assertFalse(build_rooms.exported(self.FLOORS, {"SW_T_F10_slab", "SW_CCOM_F1_piers"}))

    def test_no_tiles_no_volumes(self):
        import tempfile

        with tempfile.TemporaryDirectory() as empty:
            out = build_rooms.build(tiles=empty)
        self.assertEqual((out["volumes"], out["rooms"]), ([], []))


if __name__ == "__main__":
    unittest.main()
