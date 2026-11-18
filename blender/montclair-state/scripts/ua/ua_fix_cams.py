"""Fix UA cameras that rendered empty/black; reframe onto the Normal Ave ribbon."""
import bpy, os, math
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'

# Find Normal Ave ribbon bbox for aiming
road = bpy.data.objects.get('UA_NormalAve_CR618_583841725_727_729_UNVERIFIED')
walk = bpy.data.objects.get('UA_NormalAve_N_sidewalk_583841727_UNVERIFIED')
spur = bpy.data.objects.get('UA_CollegeAve_spur_1557427669_UNVERIFIED')

def wbbox(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    return lo, hi, (lo+hi)/2

lo, hi, mid = wbbox(road)
print('ROAD bbox', tuple(lo), '->', tuple(hi), 'mid', tuple(mid))
if walk:
    wlo, whi, wmid = wbbox(walk); print('WALK mid', tuple(wmid))
if spur:
    slo, shi, smid = wbbox(spur); print('SPUR mid', tuple(smid), 'len-ish', (shi-slo).length)

def aim(ob, loc, target, lens=None):
    ob.location = Vector(loc)
    direction = Vector(target) - ob.location
    ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if lens is not None:
        ob.data.lens = lens
    print('CAM', ob.name, 'loc', tuple(round(x,2) for x in ob.location), '->', tuple(round(x,2) for x in target))

# Eye from campus north of road — stand on walk, look SE along Normal Ave
# mid is roughly centre of ribbon; place cam ~12 m north, 1.65 m above road z
cam = bpy.data.objects.get('UA_CAM_eye_NormalAve_from_N')
if cam:
    z = mid.z
    aim(cam, (mid.x - 10, mid.y + 14, z + 1.65),
        (mid.x + 25, mid.y - 8, z + 0.8), lens=35)

# Oblique: from south of Normal Ave looking north across the ribbon toward College Hall
cam = bpy.data.objects.get('UA_CAM_oblique_NormalAve_from_SW')
if cam:
    aim(cam, (mid.x - 40, mid.y - 70, mid.z + 45),
        (mid.x + 30, mid.y + 40, mid.z + 5), lens=28)

# Closeup: right at the walk/road join, looking along the curb
cam = bpy.data.objects.get('UA_CAM_closeup_NormalAve_N_sidewalk')
if cam and walk:
    wlo, whi, wmid = wbbox(walk)
    # pick a point near mid of walk
    aim(cam, (wmid.x - 3, wmid.y + 4.5, wmid.z + 1.8),
        (wmid.x + 6, wmid.y - 1.5, wmid.z + 0.15), lens=40)

# College Ave spur eye: stand on spur looking south to Normal Ave junction
cam = bpy.data.objects.get('UA_CAM_eye_CollegeAve_spur_to_Normal')
if cam and spur:
    slo, shi, smid = wbbox(spur)
    # junction is south end of spur ≈ (slo.x-ish / south)
    jx, jy = -256.1, -271.6
    jz = mid.z
    aim(cam, (-235, -210, jz + 1.7),
        (jx, jy, jz + 0.5), lens=35)

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', len(bpy.data.objects))
