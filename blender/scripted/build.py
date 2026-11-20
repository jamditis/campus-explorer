"""Build every scripted area into one new .blend from the plan files in the area folders here.

usage: blender -b --factory-startup --python blender/scripted/build.py -- DATA_DIR OUT.blend
           [--assets MAIN.blend] [--areas NAME,NAME] [--preview DIR]

DATA_DIR holds one evidence folder per area, named as the area (tools/evidence/fetch.py writes its
lidar.npz), and authored/*.png from blender/scripted/paint.py. OUT.blend must be outside the
repository. The previews show the last area built.
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


def _near(ring, x, y, d):
    """Is (x, y) inside the closed outline `ring` or within `d` metres of it?"""
    if geom.inside(ring, x, y):
        return True
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1], strict=True):
        vx, vy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / ((vx * vx + vy * vy) or 1.0)))
        if (x - ax - t * vx) ** 2 + (y - ay - t * vy) ** 2 < d * d:
            return True
    return False


def build_area(plan_dir, data, assets, built):
    """Ground and objects of one area. `data` holds <area>/lidar.npz and authored/*.png."""
    lay = layout.load(plan_dir)
    if not lay["footprint"]:
        if not lay["interiors"]:
            sys.exit(f"{plan_dir.name}: no plan file defines the footprint")
        import place  # an area of interiors only: no ground, no terrain

        return lay, None, place.build(lay, None, assets)
    edge = (
        json.loads(Path(plan_dir / "edge_heights.json").read_text())["samples"]
        if (plan_dir / "edge_heights.json").exists()
        else None
    )
    # the other areas of this build (an area left out with --areas is not a neighbour here)
    others = [layout.load(d) for d in built if d.name != plan_dir.name]
    if edge:
        edge = [e for e in edge if layout.meets_neighbour(lay, e[0], e[1])]
        # along an edge shared with another scripted area there is no other model to meet: both
        # areas take that ground from the same LiDAR, so samples of the old ground there are dropped
        edge = [
            e
            for e in edge
            if not any(o["footprint"] and _near(o["footprint"], e[0], e[1], 2.0) for o in others)
        ]
    # Paving is graded from paved cells only. A road or lot that runs on into another scripted
    # area is one paved surface on the ground: the other areas' paving is part of that set, or the
    # grade would be cut off at the shared edge and the two areas would meet with a step.
    paved = [
        s["ring"]
        for area in [lay, *others]
        for s in area["surfaces"]
        if s["kind"] in ground.PAVED and s.get("grade", True)
    ]
    # a solid stand reads as ground in the LiDAR: its outline, grown by 1.5 m, is left out of the
    # ground
    voids, caps = [], []
    for st in lay["stands"]:
        ring = geom.expand(st["ring"], True)
        voids.append(geom.offset(ring, -1.5 if geom.area(ring) > 0 else 1.5, True))
        if st.get("style") == "bowl":
            # the filled gap would rise above a bowl's rows: under the bowl's block (and on its
            # outline) the ground is held below the block's top, hidden; outside nothing changes
            import place  # noqa: PLC0415 (bpy only: imported where a bowl needs its frame)
            import stand  # noqa: PLC0415

            at, angle, length, depth = place._front_frame(ring, st["front"])
            top = stand.bowl_top(st, at, angle, length, depth)
            block = stand.bowl_outline(st, at, angle, length, depth)  # may reach past the ring
            lines = stand.step_lines(block, at, angle, top.steps)
            caps.append(dict(ring=block, top=top, lines=lines))
    # ground.triangulate puts edges on these outlines and risers: no ground triangle spans a step
    lay["caps"] = [c["ring"] for c in caps]
    lay["cap_lines"] = [ln for c in caps for ln in c["lines"]]
    lidar = data / plan_dir.name / "lidar.npz"
    terrain = ground.Terrain(lidar, edge, lay["lifts"], lay["footprint"], paved, voids, caps=caps)
    authored = data / "authored"
    lay["image_dir"] = str(authored) if authored.exists() else None  # paint sheets, also on roofs
    objects = ground.build(lay, terrain, lay["image_dir"])
    try:
        import place  # object builders; optional while the ground is being worked on
    except ImportError:
        place = None
    if place:
        objects += place.build(lay, terrain, assets)
    return lay, terrain, objects


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    data, out = Path(args[0]), Path(args[1]).resolve()
    preview = Path(args[args.index("--preview") + 1]) if "--preview" in args else None
    # a main-model .blend to take the tree asset from (a release file will do); without it, no trees
    assets = Path(args[args.index("--assets") + 1]) if "--assets" in args else None
    if HERE.parents[1] in out.parents:
        sys.exit("refusing to write a .blend inside the repository")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objects = []
    built = layout.areas(args)
    for plan_dir in built:
        lay, terrain, obs = build_area(plan_dir, data, assets, built)
        objects += obs
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
        ring = lay["footprint"] or lay["interiors"][0]["outline"]  # interiors only: no ground
        b = [
            min(p[0] for p in ring),
            min(p[1] for p in ring),
            max(p[0] for p in ring),
            max(p[1] for p in ring),
        ]
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        span = max(b[2] - b[0], b[3] - b[1])
        cz = terrain.at(cx, cy) if terrain else lay["interiors"][0]["floor"]
        kit.preview(
            str(preview / f"{lay['area']}_sw.png"),
            (cx, cy, cz),
            span * 1.1,
            215,
            40,
        )
        kit.preview(
            str(preview / f"{lay['area']}_top.png"),
            (cx, cy, cz),
            span * 1.3,
            180,
            89,
        )


if __name__ == "__main__":
    main()
