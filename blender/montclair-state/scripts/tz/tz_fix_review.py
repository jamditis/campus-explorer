"""tz self-review fixes: cooler addition panel + reframe closeup cam. Idempotent on live scene."""
import bpy
from mathutils import Vector

SAVE = True
TAG = 'tz_obj'

# 1) cooler/darker contemporary panel (distinct from Mission cream 0.86/0.835/0.78)
m = bpy.data.materials.get('TZ_Cole_add_panel_UNVERIFIED')
if m and m.use_nodes:
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (0.55, 0.58, 0.62, 1)
    b.inputs['Roughness'].default_value = 0.42
    b.inputs['Metallic'].default_value = 0.22
    print('TZ panel tone cooled')

# 2) slightly stronger mullion
m2 = bpy.data.materials.get('TZ_Cole_add_mullion_UNVERIFIED')
if m2 and m2.use_nodes:
    b = m2.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (0.08, 0.085, 0.09, 1)
    b.inputs['Metallic'].default_value = 0.7
    print('TZ mullion darkened')

# 3) reframe closeup to NE corner of addition (show curtain + E side + historic junction)
def ground_z(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    best = None
    for nm in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
        o = bpy.data.objects.get(nm)
        if not o: continue
        e = o.evaluated_get(dg); iw = o.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (o.matrix_world @ r[1]).z
            if best is None or z > best: best = z
    return best if best is not None else 133.0

cam = bpy.data.objects.get('TZ_CAM_closeup_CollegeHall_north_addition')
if cam:
    # from NNE looking at NE corner of addition ~ (-100, -68)
    loc = Vector((-88.0, -42.0, ground_z(-88, -42) + 3.5))
    tgt = Vector((-105.0, -70.0, 141.5))
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 45
    print('TZ closeup reframed', tuple(round(x,2) for x in loc))

# also nudge N eye a bit east so E wing windows + addition both read
camN = bpy.data.objects.get('TZ_CAM_eye_CollegeHall_from_N')
if camN:
    loc = Vector((-95.0, -18.0, ground_z(-95, -18) + 1.65))
    tgt = Vector((-108.0, -72.0, 141.0))
    camN.location = loc
    camN.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
    print('TZ N eye nudged', tuple(round(x,2) for x in loc))

if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
print('TZ FIX DONE')
