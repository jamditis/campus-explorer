"""The places builder shows the university's own name where OpenStreetMap has another."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "places"))

import build_places  # noqa: E402


class Names(unittest.TestCase):
    def test_the_college_of_communication_and_media_has_its_own_name(self):
        tags = {"name": "School of Communication and Media"}
        self.assertEqual(
            build_places.place_name("way", 1188721159, tags), "College of Communication and Media"
        )
        self.assertEqual(build_places.place_name("way", 1, {"name": " Life Hall "}), "Life Hall")

    def test_the_published_places_carry_the_overrides(self):
        places = json.loads((ROOT / "viewer" / "places.json").read_text())
        items = places["places"] if isinstance(places, dict) else places
        by_osm = {p.get("osm"): p["name"] for p in items}
        for osm, name in build_places.NAMES.items():
            self.assertEqual(by_osm[osm], name)


if __name__ == "__main__":
    unittest.main()
