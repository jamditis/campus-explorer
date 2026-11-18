# Step 1 of the web export: open main, list renderable objects with world bbox, mesh data, tris, mods -> objects.json
import json
import os

import bpy
from mathutils import Vector

F = os.environ.get("FILE", "/workspace/nj-scenes/montclair-state/montclair_state.blend")
bpy.ops.wm.open_mainfile(filepath=F, load_ui=False)
vl = bpy.context.view_layer
out = {}


def vis(o):
    try:
        return o.visible_get(view_layer=vl) or (
            not o.hide_render and o.name in vl.objects and not o.hide_get()
        )
    except Exception:
        return not o.hide_render


for o in bpy.context.scene.objects:
    if o.type not in ("MESH", "CURVE", "FONT", "EMPTY"):
        continue
    if o.hide_render:
        continue
    if o.name not in vl.objects:
        continue
    # collection exclusion
    if not vl.objects[o.name].visible_get() and o.hide_viewport == False and o.hide_get() == False:
        ex = True
    try:
        v = o.visible_get()
    except Exception:
        v = True
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in bb]
    ys = [p.y for p in bb]
    zs = [p.z for p in bb]
    tri = sum(len(p.vertices) - 2 for p in o.data.polygons) if o.type == "MESH" else 0
    out[o.name] = dict(
        t=o.type,
        v=v,
        bb=[min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)],
        tri=tri,
        data=o.data.name if o.data else None,
        inst=o.instance_collection.name
        if o.instance_type == "COLLECTION" and o.instance_collection
        else None,
        mods=[(m.type, m.name) for m in o.modifiers if m.show_render],
        mats=[s.material.name for s in getattr(o, "material_slots", []) if s.material],
        parent=o.parent.name if o.parent else None,
    )
json.dump(out, open("/workspace/nj-scenes/scripts/web/objects.json", "w"))
print("N", len(out), "visible", sum(1 for v in out.values() if v["v"]))
for l in open("/proc/self/status"):
    if l.startswith("VmHWM"):
        print("MEM", l.strip())
