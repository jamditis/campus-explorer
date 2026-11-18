"""ue cameras for College Hall east WIPs."""
import bpy, os
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
TAG = 'ue_obj'

def revert_cams():
    for o in [o for o in list(bpy.data.objects) if o.get(TAG) and o.type == 'CAMERA']:
        cam = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if cam and cam.users == 0:
            bpy.data.cameras.remove(cam)
    print('UE cams REVERTED')

if REV:
    revert_cams()
    if SAVE:
        bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# replace existing UE cams
revert_cams()

def ground_z(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    best = None
    for nm in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km', 'Susan A. Cole Hall walls'):
        o = bpy.data.objects.get(nm)
        if not o:
            continue
        e = o.evaluated_get(dg)
        iw = o.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (o.matrix_world @ r[1]).z
            if best is None or z > best:
                best = z
    return best if best is not None else 132.0

def add_cam(name, loc, target, lens=50):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam.clip_end = 60000
    o = bpy.data.objects.new(name, cam)
    bpy.context.scene.collection.objects.link(o)
    o.location = Vector(loc)
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    o[TAG] = 1
    o['ue_source'] = '20261105ue'
    return o

# E long face mid ~ (-62, -105); south wing door ~ (-67, -128)
add_cam('UE_CAM_oblique_CollegeHall_from_SE', (-5, -175, 168), (-80, -110, 140), lens=30)
gzE = ground_z(-35, -118)
add_cam('UE_CAM_eye_CollegeHall_from_E', (-35.0, -118.0, gzE + 1.7), (-64, -115, 136), lens=35)
gzS = ground_z(-90, -155)
add_cam('UE_CAM_eye_CollegeHall_from_S', (-90.0, -155.0, gzS + 1.7), (-90, -105, 139), lens=38)
gzC = ground_z(-48, -122)
add_cam('UE_CAM_closeup_CollegeHall_east_arches', (-48.0, -122.0, gzC + 2.0), (-64, -118, 134.5), lens=32)
print('UE cams', [o.name for o in bpy.data.objects if o.get(TAG) and o.type == 'CAMERA'])
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
