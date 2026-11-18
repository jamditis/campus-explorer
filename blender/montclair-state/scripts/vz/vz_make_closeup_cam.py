"""Create VZ_CAM_closeup_Blanton_infill aimed at cream infill S face (material-only session; cam only)."""
import bpy, math
from mathutils import Vector, Euler

name='VZ_CAM_closeup_Blanton_infill'
# Prefer cloning TR eye cam and pulling closer; fall back to world coords near Blanton S
src = bpy.data.objects.get('TR_CAM_eye_Blanton_infill_from_S')
ref = bpy.data.objects.get('TI_Blanton_Hall_313029108_lower_UNVERIFIED')
if name in bpy.data.objects:
    cam_obj = bpy.data.objects[name]
    print('exists', name)
else:
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    print('created', name)

if ref:
    bb = [ref.matrix_world @ Vector(c) for c in ref.bound_box]
    cx = sum(v.x for v in bb)/8
    cy = sum(v.y for v in bb)/8
    cz = sum(v.z for v in bb)/8
    # S face ≈ smaller Y; stand south of mid-height cream band
    ymin = min(v.y for v in bb)
    zmin = min(v.z for v in bb); zmax = max(v.z for v in bb)
    target = Vector((cx, ymin, zmin + 0.45*(zmax-zmin)))
    loc = Vector((cx, ymin - 9.5, target.z + 0.8))
    cam_obj.location = loc
    direction = target - loc
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_obj.data.lens = 50
    print('aimed at', [round(x,2) for x in target], 'from', [round(x,2) for x in loc], 'zspan', round(zmax-zmin,2))
elif src:
    cam_obj.location = src.location.copy()
    cam_obj.rotation_euler = src.rotation_euler.copy()
    cam_obj.data.lens = getattr(src.data, 'lens', 35) * 1.4
    # pull closer along -local Z
    import mathutils
    forward = cam_obj.matrix_world.to_quaternion() @ mathutils.Vector((0,0,-1))
    cam_obj.location = cam_obj.location + forward * 8.0
    print('cloned from TR eye, pulled closer')
else:
    raise SystemExit('no ref')

cam_obj['vz_cam']=1
bpy.ops.wm.save_mainfile()
print('saved cam', name, 'objs', len(bpy.data.objects))
