"""Join the exported scenes into one campus manifest: models/manifest.json.

The viewer shows a single campus. Today the campus is modelled in two Blender files
(main and north) that share one origin and overlap in the middle. Each is exported to
its own folder of 160 m tiles. This step lists every tile once, so the viewer can load
them as one scene.

Where both scenes have a tile for the same square, one scene owns the square. The
default owner is the scene with more geometry there (bytes of the tile); OWNERS pins
squares where that default was checked by eye and is wrong. This is a seam at tile
boundaries, not a merge: an object that only the other scene has in an owned square is
not shown. UNVERIFIED until the two Blender files are merged and exported as one scene.

usage: python3 tools/web-export/unify.py [--models models]
"""

import argparse
import json
import os
import sys

# Scenes in priority order: on a tie the first one wins.
SCENES = ("main", "north")
# The far-field ground comes from one scene only; two copies would fight in the depth buffer.
SKIRT_FROM = "main"
# Squares pinned by hand: "t_i_j" -> scene. Checked in the viewer's top view.
OWNERS = {}


def load(models, scene):
    path = os.path.join(models, scene, "manifest.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def unify(models):
    manifests = {s: load(models, s) for s in SCENES}
    squares = {}
    shared = []
    for scene in SCENES:
        for t in manifests[scene]["tiles"]:
            entry = dict(t, file=f"{scene}/{t['file']}", scene=scene)
            if "center" not in t:
                if t["file"] == "skirt.glb" and scene != SKIRT_FROM:
                    continue
                shared.append(entry)
                continue
            squares.setdefault(t["file"][:-4], []).append(entry)
    tiles = []
    overlaps = []
    for name in sorted(squares):
        options = squares[name]
        pinned = OWNERS.get(name)
        owner = next((o for o in options if o["scene"] == pinned), None)
        if owner is None:
            owner = max(options, key=lambda o: o["bytes"])  # stable: first scene wins ties
        tiles.append(owner)
        if len(options) > 1:
            overlaps.append(
                dict(
                    square=name,
                    owner=owner["scene"],
                    pinned=pinned is not None,
                    dropped=[
                        dict(scene=o["scene"], bytes=o["bytes"]) for o in options if o is not owner
                    ],
                )
            )
    order = {"skirt.glb": 0, "context.glb": 1}
    shared.sort(key=lambda t: (order.get(os.path.basename(t["file"]), 2), SCENES.index(t["scene"])))
    tiles = shared + tiles
    paint = [
        dict(p, file=f"{scene}/{p['file']}") for scene in SCENES for p in manifests[scene]["paint"]
    ]
    return dict(
        tiles=tiles,
        paint=paint,
        sources=[
            dict(
                scene=s,
                source_saved=manifests[s].get("source_saved", ""),
                source_version=manifests[s].get("source_version", ""),
                exported=manifests[s].get("exported", ""),
            )
            for s in SCENES
        ],
        overlaps=overlaps,
        total_bytes=sum(t["bytes"] for t in tiles),
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--models", default="models")
    args = ap.parse_args()
    out = unify(args.models)
    path = os.path.join(args.models, "manifest.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print(
        f"unify: {len(out['tiles'])} tiles, {out['total_bytes'] / 1e6:.0f} MB, "
        f"{len(out['overlaps'])} squares in both scenes"
    )
    for o in out["overlaps"]:
        lost = ", ".join(f"{d['scene']} {d['bytes'] / 1e6:.1f} MB" for d in o["dropped"])
        print(f"  {o['square']}: {o['owner']} owns it, not shown: {lost}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
