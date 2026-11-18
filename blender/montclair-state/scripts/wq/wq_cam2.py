"""wq: reframe the NW eye camera — first pick sat inside large crown bboxes
just south of Stone. Place it west of Stone, south of the building, looking SE.
"""
import bpy, json, math, numpy as np
from mathutils import Vector, Euler

ROOT = '/workspace/nj-scenes/montclair-state'
g = np.load(f'{ROOT}/data/wo/chm_grid_sw_1m.npz')
DTM = g['USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz__dtm']


def dtm(x, y):
    i = int(round(x - 40.0))
    j = int(round(y - 140.0))
    if 0 <= j < DTM.shape[0] and 0 <= i < DTM.shape[1] and np.isfinite(DTM[j, i]):
        return float(DTM[j, i])
    return None


def look_rot(loc, tgt):
    d = Vector(tgt) - Vector(loc)
    return Euler((math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                  math.atan2(d.y, d.x) - math.pi / 2))


crowns = []
for o in bpy.data.objects:
    n = o.name
    if not (n.startswith('WQ_south_wood_tree_') or n.startswith('T_')):
        continue
    t = o.matrix_world.translation
    if not (100 <= t.x <= 230 and 120 <= t.y <= 240):
        continue
    xs = [(o.matrix_world @ Vector(c)).x for c in o.bound_box]
    ys = [(o.matrix_world @ Vector(c)).y for c in o.bound_box]
    zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    r = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
    crowns.append((t.x, t.y, min(zs), max(zs), min(r, 14.0), n))  # cap radius so huge leaf cards don't ban half the hillside


def inside(x, y, z, margin=2.0):
    hits = []
    for cx, cy, z0, z1, r, n in crowns:
        if (x - cx) ** 2 + (y - cy) ** 2 <= (r + margin) ** 2 and (z0 - 1) <= z <= (z1 + 1):
            hits.append(n)
    return hits


def near_blocked(loc, tgt, near=8.0):
    locV, tgtV = Vector(loc), Vector(tgt)
    d = tgtV - locV
    if d.length < 1e-6:
        return True, ['zero']
    dn = d.normalized()
    who = []
    for s in np.linspace(0.4, near, 14):
        p = locV + dn * s
        hs = inside(p.x, p.y, p.z, margin=1.0)
        if hs:
            who.extend(hs)
    return (len(who) > 0), list(dict.fromkeys(who))


# (xy, zoff, txy, tzoff, lens)
raw = [
    ((118, 200), 1.7, (172, 180), 6, 32),
    ((120, 205), 1.7, (170, 182), 6, 32),
    ((115, 190), 1.8, (170, 185), 5, 30),
    ((112, 195), 1.8, (170, 182), 6, 32),
    ((122, 198), 1.7, (175, 178), 5, 35),
    ((110, 180), 2.0, (168, 185), 6, 30),
    ((125, 208), 1.7, (175, 180), 5, 32),
    ((108, 205), 1.8, (170, 185), 6, 32),
    ((210, 228), 1.8, (175, 185), 6, 32),
    ((218, 220), 1.8, (180, 190), 5, 30),
    ((215, 205), 1.7, (175, 185), 5, 32),
    ((130, 160), 1.8, (170, 185), 6, 32),
]
cands = []
for xy, zoff, txy, tzoff, lens in raw:
    z = dtm(*xy) or 130.0
    tz = dtm(*txy) or (z - 8)
    cands.append(((xy[0], xy[1], z + zoff), (txy[0], txy[1], tz + tzoff), lens))

picked = None
tried = []
for loc, tgt, lens in cands:
    inn = inside(*loc, margin=2.0)
    blk, who = near_blocked(loc, tgt, near=8.0)
    rec = {'loc': [round(c, 2) for c in loc], 'tgt': [round(c, 2) for c in tgt],
           'lens': lens, 'inside': inn, 'near_blocked': blk, 'blocked_by': who}
    tried.append(rec)
    print('TRY', rec['loc'], 'inside', inn[:3], 'blocked', who[:3], flush=True)
    if not inn and not blk and picked is None:
        picked = rec

if picked is None:
    opts = [t for t in tried if not t['inside']]
    picked = opts[0] if opts else tried[0]
    print('FALLBACK', picked)

cam = bpy.data.objects.get('WQ_CAM_eye_south_wood_from_NW')
if cam is None:
    cd = bpy.data.cameras.new('WQ_CAM_eye_south_wood_from_NW')
    cam = bpy.data.objects.new('WQ_CAM_eye_south_wood_from_NW', cd)
    bpy.context.scene.collection.objects.link(cam)
cam.location = Vector(picked['loc'])
cam.rotation_euler = look_rot(picked['loc'], picked['tgt'])
cam.data.lens = picked['lens']
cam.data.clip_end = 30000
cam['wq_obj'] = 1
print('PICKED', picked, flush=True)
bpy.ops.wm.save_mainfile()
print('SAVED', flush=True)
json.dump({'picked': picked, 'tried': tried}, open(f'{ROOT}/data/wq/cam2.json', 'w'), indent=1)
