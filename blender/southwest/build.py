"""Build the southwest corner into a new .blend from the plan files in this folder.

usage: blender -b --factory-startup --python blender/southwest/build.py -- DATA_DIR OUT.blend
[--assets MAIN.blend]
[--plan DIR] [--preview DIR]

DATA_DIR is the evidence folder written by tools/evidence/fetch.py (lidar.npz) and by
blender/southwest/paint.py (authored/*.png). OUT.blend must be outside the repository.
"""

import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import geom  # noqa: E402
import ground  # noqa: E402
import kit  # noqa: E402
import layout  # noqa: E402


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    data, out = Path(args[0]), Path(args[1]).resolve()
    plan_dir = Path(args[args.index("--plan") + 1]) if "--plan" in args else HERE / "plan"
    preview = Path(args[args.index("--preview") + 1]) if "--preview" in args else None
    # a main-model .blend to take the tree asset from (a release file will do); without it, no trees
    assets = Path(args[args.index("--assets") + 1]) if "--assets" in args else None
    if HERE.parents[1] in out.parents:
        sys.exit("refusing to write a .blend inside the repository")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    lay = layout.load(plan_dir)
    if not lay["footprint"]:
        sys.exit("no plan file defines the footprint")
    edge = (
        json.loads(Path(plan_dir / "edge_heights.json").read_text())["samples"]
        if (plan_dir / "edge_heights.json").exists()
        else None
    )
    paved = [
        s["ring"] for s in lay["surfaces"] if s["kind"] in ground.PAVED and s.get("grade", True)
    ]
    # a solid stand reads as ground in the LiDAR: its outline, grown by 1.5 m, is left out of the
    # ground
    voids = []
    for st in lay["stands"]:
        ring = geom.expand(st["ring"], True)
        voids.append(geom.offset(ring, -1.5 if geom.area(ring) > 0 else 1.5, True))
    terrain = ground.Terrain(data / "lidar.npz", edge, lay["lifts"], lay["footprint"], paved, voids)
    authored = data / "authored"
    objects = ground.build(lay, terrain, str(authored) if authored.exists() else None)
    try:
        import place  # object builders; optional while the ground is being worked on
    except ImportError:
        place = None
    if place:
        objects += place.build(lay, terrain, assets)
    tris = 0
    for ob in objects:
        ob.data.calc_loop_triangles()
        n = len(ob.data.loop_triangles)
        tris += n
        print(f"SW {n:8d} tris  {ob.name}")
    print("SW objects", len(objects), "triangles", tris)
    out.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
    print("SW saved", out)
    if preview:
        preview.mkdir(parents=True, exist_ok=True)
        b = [
            min(p[0] for p in lay["footprint"]),
            min(p[1] for p in lay["footprint"]),
            max(p[0] for p in lay["footprint"]),
            max(p[1] for p in lay["footprint"]),
        ]
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        span = max(b[2] - b[0], b[3] - b[1])
        kit.preview(str(preview / "all_sw.png"), (cx, cy, terrain.at(cx, cy)), span * 1.1, 215, 40)
        kit.preview(str(preview / "all_top.png"), (cx, cy, terrain.at(cx, cy)), span * 1.3, 180, 89)


if __name__ == "__main__":
    main()
