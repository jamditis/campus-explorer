"""tz fix2: darker addition panel + closeup clear of tree."""
import bpy
from mathutils import Vector
m = bpy.data.materials.get('TZ_Cole_add_panel_UNVERIFIED')
if m and m.use_nodes:
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (0.38, 0.41, 0.45, 1)
    b.inputs['Roughness'].default_value = 0.40
    b.inputs['Metallic'].default_value = 0.28
    print('TZ panel darker grey')

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
# from slightly elevated N, clear of plaza trees — aim at curtain centre
loc = Vector((-108.0, -28.0, ground_z(-108, -28) + 5.5))
tgt = Vector((-108.0, -68.0, 140.5))
cam.location = loc
cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = 40
print('TZ closeup', tuple(round(x,2) for x in loc))
bpy.ops.wm.save_mainfile(); print('SAVED')
