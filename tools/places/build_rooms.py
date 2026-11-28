"""Build viewer/rooms.json: room numbers and the volumes of the buildings that have a real interior.

Reads every scripted interior plan (blender/scripted/<area>/interior.json, its rough entries made
into floors by blender/scripted/rough.py) whose objects are in the published tiles, through the
plan's own label rule (blender/scripted/rooms.py `labels`), so no Blender is needed. Each area with
an interior gives one volume: the floor outline, from the lowest floor up to the top of the shell
building that holds it (the highest ceiling when there is none), with the floor levels and the
highest interior ceiling. The building's name is the viewer place (viewer/places.json) that lies
inside the outline.

Coordinates are written in the viewer frame: x east, y up, z = -model y, metres.

Usage:
    python3 tools/places/build_rooms.py            # writes viewer/rooms.json
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTED = ROOT / "blender" / "scripted"
sys.path.insert(0, str(SCRIPTED))

import rooms  # noqa: E402
import rough  # noqa: E402


def tile_names(tiles):
    """Object names in the published tiles (`tiles`: models/main): each .glb's node names, read
    from its JSON chunk only."""
    out = set()
    for f in sorted(Path(tiles).glob("**/*.glb")):
        with open(f, "rb") as h:
            size = struct.unpack("<I", h.read(20)[12:16])[0]
            out.update(n.get("name", "") for n in json.loads(h.read(size)).get("nodes", []))
    return out


def exported(floors, names):
    """Are an interior plan's objects in the tiles? interior.py names each floor's objects
    SW_<floor name>_...; the exporter joins some of them, so any one of them is enough."""
    return any(n.startswith(f"SW_{f['name']}_") for f in floors for n in names)


# The university's own short names (Joe's usage and the building's signs), for search
SHORT = {"College of Communication and Media": "CCOM"}


def inside(ring, x, y):
    """Is (x, y) inside the closed ring [[x, y], ...]? Even-odd rule."""
    hit = False
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1], strict=True):
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            hit = not hit
    return hit


def _view(ring):
    return [[round(p[0], 2), round(-p[1], 2) + 0.0] for p in ring]


def area(name, floors, places, buildings, short=SHORT):
    """Volume and rooms of one area's interior plan (`floors`: the plan's `interiors` list).

    `places`: viewer places ({name, kind, x, z}); `buildings`: the area's shell buildings
    ({ring, top}) in model metres. Returns {"volumes": [one], "rooms": [...]}.
    """
    floors = sorted(floors, key=lambda f: f["level"])
    outline = [p[:2] for p in floors[0]["outline"]]
    building = next(
        (
            p["name"]
            for p in places
            if p.get("kind") == "building" and inside(outline, p["x"], -p["z"])
        ),
        name,
    )
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    tops = [b["top"] for b in buildings if "top" in b and inside(b["ring"], cx, cy)]
    level_y = {f["level"]: f["floor"] for f in floors}
    volume = dict(
        id=name,
        building=building,
        short=short.get(building, ""),
        ring=_view(outline),
        y0=floors[0]["floor"],
        y1=max(tops) if tops else max(f["ceiling"] for f in floors),
        ceiling=max(f["ceiling"] for f in floors),
        levels=[dict(floor=f["level"], y=f["floor"]) for f in floors],
        unverified=sorted({f["unverified"] for f in floors if f.get("unverified")}),
    )
    out = []
    for lab in rooms.labels(floors):
        out.append(
            dict(
                name=lab["name"],
                x=lab["x"],
                z=round(-lab["y"], 2) + 0.0,
                y=level_y[lab["floor"]],
                floor=lab["floor"],
                building=building,
                unverified=bool(lab["unverified"]),
            )
        )
    return dict(volumes=[volume], rooms=out)


def build(
    scripted=SCRIPTED, places_file=ROOT / "viewer" / "places.json", tiles=ROOT / "models" / "main"
):
    """Volumes and rooms of every interior plan whose objects the tiles carry: a plan not yet built
    and exported gives no volume and no room, so the viewer never names an interior it cannot
    show."""
    places = json.loads(Path(places_file).read_text())["places"]
    names = tile_names(tiles)
    out = dict(
        source="blender/scripted/<area>/interior.json: room numbers from the floor signs",
        builder="tools/places/build_rooms.py",
        frame="three.js viewer metres: x east, y up, z = -model y (grid north is -z)",
        volumes=[],
        rooms=[],
    )
    for plan in sorted(Path(scripted).glob("*/interior.json")):
        floors = rough.expand(json.loads(plan.read_text()))
        if not floors or not exported(floors, names):
            continue
        buildings = []
        for other in sorted(plan.parent.glob("*.json")):
            buildings += json.loads(other.read_text()).get("buildings", [])
        one = area(plan.parent.name, floors, places, buildings)
        out["volumes"] += one["volumes"]
        out["rooms"] += one["rooms"]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / "viewer" / "rooms.json")
    args = parser.parse_args(argv)
    out = build()
    args.out.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(f"{args.out}: {len(out['volumes'])} volumes, {len(out['rooms'])} rooms")
    return 0


if __name__ == "__main__":
    sys.exit(main())
