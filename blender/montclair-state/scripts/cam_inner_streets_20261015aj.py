"""tag 20261015aj: close-up cam over the new inner-band OSM streets (Haddenfield / Rolling Hills Rd, ~0.95 km ESE) + carpet."""
import bpy, sys
from mathutils import Vector
sc = bpy.context.scene
G = [bpy.data.objects[n] for n in ("Context_skirt_3DEP_ortho_4km", "BD_farfield_3DEP_ortho")]
def gz(x, y):
    for o in G:
        mi = o.matrix_world.inverted()
        ok, loc, *_ = o.ray_cast(mi @ Vector((x, y, 3000)), (mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if ok: return (o.matrix_world @ loc).z
    return 0.0
tx, ty = 890.0, -430.0; cx, cy = 760.0, -300.0
tgt = Vector((tx, ty, gz(tx, ty) + 2.0)); loc = Vector((cx, cy, gz(cx, cy) + 48.0))
name = "CAM_closeup_inner_streets_aj"
o = bpy.data.objects.get(name) or bpy.data.objects.new(name, bpy.data.cameras.new(name))
if o.name not in sc.collection.objects: sc.collection.objects.link(o)
o.location = loc; o.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
o.data.lens = 35; o.data.clip_start = 0.1; o.data.clip_end = 60000
print("CAM", name, tuple(round(v, 1) for v in loc), "->", tuple(round(v, 1) for v in tgt))
if "--save" in sys.argv: bpy.ops.wm.save_mainfile(); print("SAVED")
