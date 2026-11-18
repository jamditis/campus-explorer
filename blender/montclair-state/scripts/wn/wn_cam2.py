"""wn: place closeup from the open E-eye lawn / a high oblique; save if a downward ray hits the new patch."""
import bpy, json, math
from mathutils import Vector
from mathutils import Euler

ROOT = '/workspace/nj-scenes/montclair-state'
dg = bpy.context.evaluated_depsgraph_get()
cams = {}
for n in ('WJ_CAM_eye_south_gully_from_E', 'WJ_CAM_closeup_south_gully_oblique_SE',
          'WF_CAM_eye_east_slope_from_SE', 'WN_CAM_closeup_south_wood_ground',
          'TI_CAM_oblique_east_dorms_from_SW'):
    o = bpy.data.objects.get(n)
    if not o:
        cams[n] = None
        continue
    # forward = -Z in camera space
    fwd = o.matrix_world.to_3x3() @ Vector((0, 0, -1))
    cams[n] = {
        'loc': [round(c, 2) for c in o.location],
        'fwd': [round(c, 3) for c in fwd],
        'lens': o.data.lens,
    }
print('CAMS', json.dumps(cams, indent=1))

# try positions: along E-eye forward, and high obliques over the west hillside
e = bpy.data.objects['WJ_CAM_eye_south_gully_from_E']
efwd = (e.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
candidates = []
for dist in (8, 14, 20, 26, 32):
    loc = e.location + efwd * dist
    candidates.append(('eeve_fwd_%.0f' % dist, loc, e.rotation_euler.copy(), 35))
# high obliques looking down at tree_00 hillside
# tree_00 169.5, 256.5, 136
obliques = [
    ((178, 242, 146), (170, 258, 134), 32),
    ((185, 240, 148), (172, 258, 133), 30),
    ((190, 245, 145), (172, 258, 134), 32),
    ((168, 238, 150), (172, 258, 134), 35),
    ((200, 250, 142), (176, 258, 132), 28),
    ((175, 235, 152), (172, 260, 133), 40),
]
for loc, tgt, lens in obliques:
    loc = Vector(loc)
    tgt = Vector(tgt)
    d = tgt - loc
    rot = Euler((math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                 math.atan2(d.y, d.x) - math.pi / 2))
    candidates.append(('oblique', loc, rot, lens))

tried = []
picked = None
for tag, loc, rot, lens in candidates:
    # downward and look rays
    look = Euler(rot).to_matrix() @ Vector((0, 0, -1))
    sh = bpy.context.scene.ray_cast(dg, loc, look, distance=80)
    dn = bpy.context.scene.ray_cast(dg, loc, Vector((0, 0, -1)), distance=40)
    # a few extra look rays lower in the frame (pitch down)
    extra = []
    for pitch in (0.15, 0.30, 0.45):
        # rotate look downward a bit
        lp = look.copy()
        lp.z -= pitch
        lp.normalize()
        h = bpy.context.scene.ray_cast(dg, loc, lp, distance=80)
        extra.append(h[4].name if h[0] and h[4] else None)
    rec = {
        'tag': tag,
        'loc': [round(c, 2) for c in loc],
        'look_hit': sh[4].name if sh[0] and sh[4] else None,
        'look_at': [round(c, 2) for c in sh[1]] if sh[0] else None,
        'down_hit': dn[4].name if dn[0] and dn[4] else None,
        'extra': extra,
    }
    groundish = any(
        (n or '').startswith('WN_south_wood_LiDAR') or (n or '').startswith('WJ_south_gully')
        or (n or '').startswith('WF_east_dorm')
        for n in [rec['look_hit'], rec['down_hit']] + extra
    )
    rec['sees_lidar'] = groundish
    tried.append(rec)
    if groundish and picked is None:
        picked = rec
        picked['_loc'] = loc
        picked['_rot'] = rot
        picked['_lens'] = lens

rep = {'picked': {k: picked[k] for k in picked if not k.startswith('_')} if picked else None,
       'tried': tried}
print('PICKED', json.dumps(rep['picked'], indent=1))
print('TRIED', json.dumps(tried, indent=1))
if picked:
    cam = bpy.data.objects['WN_CAM_closeup_south_wood_ground']
    cam.location = picked['_loc']
    cam.rotation_euler = picked['_rot']
    cam.data.lens = picked['_lens']
    bpy.ops.wm.save_mainfile()
    print('SAVED')
    rep['saved'] = True
json.dump({'cams': cams, 'tried': tried,
           'picked': {k: picked[k] for k in picked if not k.startswith('_')} if picked else None},
          open(f'{ROOT}/data/wn/cam2.json', 'w'), indent=1)
