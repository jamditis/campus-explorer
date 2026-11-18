"""tz cameras for College Hall E/N + north addition WIPs."""
import bpy, os
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
TAG = 'tz_obj'

def revert():
    for o in [o for o in list(bpy.data.objects) if o.get(TAG) and o.type == 'CAMERA']:
        cam = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if cam and cam.users == 0:
            bpy.data.cameras.remove(cam)
    print('TZ cams REVERTED')

if REV:
    revert()
    if SAVE:
        bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

revert()

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
    o['tz_source'] = '20261105tz'
    return o

# addition centre ~ (-108, -72); east face ~ (-60, -105); north ~ (-108, -60)
add_cam('TZ_CAM_oblique_CollegeHall_from_NE', (-20, 40, 185), (-110, -90, 145), lens=35)
gzE = ground_z(-30, -105)
add_cam('TZ_CAM_eye_CollegeHall_from_E', (-30.0, -105.0, gzE + 1.65), (-90, -100, 140), lens=40)
gzN = ground_z(-95, -18)
add_cam('TZ_CAM_eye_CollegeHall_from_N', (-95.0, -18.0, gzN + 1.65), (-108, -72, 141), lens=40)
gzC = ground_z(-108, -28)
add_cam('TZ_CAM_closeup_CollegeHall_north_addition', (-108.0, -28.0, gzC + 5.5), (-108, -68, 140.5), lens=40)
print('TZ cams', [o.name for o in bpy.data.objects if o.get(TAG) and o.type == 'CAMERA'])
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
