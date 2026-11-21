"""Build every scripted area into one new .blend from the plan files in the area folders here.

usage: blender -b --factory-startup --python blender/scripted/build.py -- DATA_DIR OUT.blend
           [--assets MAIN.blend] [--adopt-from RELEASE.blend|DIR] [--areas NAME,NAME]
           [--preview DIR]

DATA_DIR holds one evidence folder per area, named as the area (tools/evidence/fetch.py writes its
lidar.npz), and authored/*.png from blender/scripted/paint.py. OUT.blend must be outside the
repository. The previews show the last area built. An area's `adopt.json` names objects of a
main-model release file to take over (adopt.py): the file is found with --adopt-from (the file or
its folder), else in the folder of --assets.
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


def adopted(lay, adopt_from, assets):
    """The objects an area takes over from a main-model release file (its adopt.json)."""
    if not lay["adopt"]:
        return []
    import adopt  # noqa: PLC0415 (bpy only)

    out = []
    for plan in lay["adopt"]:
        out += adopt.build(plan, adopt.source(plan, adopt_from, assets), kit.collection())
    return out


def build_groundless(lay, plan_dir, data, assets, adopt_from):
    """An area that owns no ground (no `footprint`, no supersede footprint): interiors, building
    parts and adopted objects on another model's site. No ground mesh is made; building parts and
    points stand on the raw LiDAR ground of <area>/lidar.npz (no edge blend, no grading)."""
    if not (lay["interiors"] or lay["buildings"] or lay["adopt"]):
        sys.exit(f"{plan_dir.name}: no plan file defines the footprint")
    terrain = None
    if any(lay[k] for k in ("buildings", "points", "stands", "fences")):
        lidar = data / plan_dir.name / "lidar.npz"
        if not lidar.exists():
            sys.exit(f"{plan_dir.name}: its building parts need ground heights from {lidar}")
        terrain = ground.Terrain(lidar)
    authored = data / "authored"
    lay["image_dir"] = str(authored) if authored.exists() else None
    import place  # noqa: PLC0415

    return lay, terrain, place.build(lay, terrain, assets) + adopted(lay, adopt_from, assets)


def build_area(plan_dir, data, assets, built, adopt_from=None):
    """Ground and objects of one area. `data` holds <area>/lidar.npz and authored/*.png."""
    lay = layout.load(plan_dir)
    if not lay["footprint"]:
        return build_groundless(lay, plan_dir, data, assets, adopt_from)
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
    # paving a plan marks `"road": true` may ramp down to a lower neighbour at the edge; lots and
    # other paving are only raised (AGENTS rule 6)
    roads = [s["ring"] for s in lay["surfaces"] if s.get("road")]
    terrain = ground.Terrain(
        lidar, edge, lay["lifts"], lay["footprint"], paved, voids, caps=caps, roads=roads
    )
    authored = data / "authored"
    lay["image_dir"] = str(authored) if authored.exists() else None  # paint sheets, also on roofs
    objects = ground.build(lay, terrain, lay["image_dir"])
    try:
        import place  # object builders; optional while the ground is being worked on
    except ImportError:
        place = None
    if place:
        objects += place.build(lay, terrain, assets)
    return lay, terrain, objects + adopted(lay, adopt_from, assets)


def view_box(lay, terrain, objects):
    """Plan box [x0, y0, x1, y1] and a height for the previews of one area: its footprint, else
    the box of what was built for it (an area without ground)."""
    from mathutils import Vector  # noqa: PLC0415

    if lay["footprint"]:
        ring = lay["footprint"]
        return [min(p[0] for p in ring), min(p[1] for p in ring),
                max(p[0] for p in ring), max(p[1] for p in ring)], None  # fmt: skip
    pts = [o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    if not pts:
        sys.exit(f"{lay['area']}: nothing was built")
    xs, ys, zs = ([p[i] for p in pts] for i in range(3))
    return [min(xs), min(ys), max(xs), max(ys)], min(zs)


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    data, out = Path(args[0]), Path(args[1]).resolve()
    preview = Path(args[args.index("--preview") + 1]) if "--preview" in args else None
    # a main-model .blend to take the tree asset from (a release file will do); without it, no trees
    assets = Path(args[args.index("--assets") + 1]) if "--assets" in args else None
    adopt_from = Path(args[args.index("--adopt-from") + 1]) if "--adopt-from" in args else None
    if HERE.parents[1] in out.parents:
        sys.exit("refusing to write a .blend inside the repository")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objects = []
    built = layout.areas(args)
    for plan_dir in built:
        lay, terrain, obs = build_area(plan_dir, data, assets, built, adopt_from)
        objects += obs
    tris = 0
    for ob in objects:
        n = 0
        if ob.type == "MESH":  # an adopted text or collection instance is counted by the export
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
        b, cz = view_box(lay, terrain, obs)
        cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
        span = max(b[2] - b[0], b[3] - b[1])
        cz = terrain.at(cx, cy) if terrain and lay["footprint"] else cz
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
