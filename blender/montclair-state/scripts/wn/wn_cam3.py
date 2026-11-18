"""wn: place closeup as a high oblique over the new south-wood LiDAR hillside."""
import bpy, json, math
from mathutils import Vector, Euler

ROOT = '/workspace/nj-scenes/montclair-state'
dg = bpy.context.evaluated_depsgraph_get()

def look_rot(loc, tgt):
    d = Vector(tgt) - Vector(loc)
    return Euler((math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                  math.atan2(d.y, d.x) - math.pi / 2))

obliques = [
    ((178, 242, 146), (170, 258, 134), 32),
    ((185, 240, 148), (172, 258, 133), 30),
    ((190, 245, 145), (172, 258, 134), 32),
    ((168, 238, 150), (172, 258, 134), 35),
    ((200, 250, 142), (176, 258, 132), 28),
    ((175, 235, 152), (172, 260, 133), 40),
    ((210, 235, 155), (175, 258, 130), 32),
    ((160, 230, 155), (172, 258, 134), 35),
    ((182, 230, 160), (172, 260, 132), 36),
    ((220, 240, 150), (180, 258, 128), 30),
    ((240, 230, 160), (175, 258, 128), 35),
    ((195, 225, 158), (174, 258, 132), 34),
    ((170, 220, 165), (172, 258, 134), 38),
]
tried = []
picked = None
for loc, tgt, lens in obliques:
    locV, tgtV = Vector(loc), Vector(tgt)
    rot = look_rot(locV, tgtV)
    look = rot.to_matrix() @ Vector((0, 0, -1))
    hits = []
    for pitch in (0.0, 0.12, 0.25, 0.4):
        lp = look.copy()
        lp.z -= pitch
        lp.normalize()
        h = bpy.context.scene.ray_cast(dg, locV, lp, distance=80)
        name = h[4].name if h[0] and h[4] else None
        pt = [round(c, 2) for c in h[1]] if h[0] else None
        hits.append({'pitch': pitch, 'name': name, 'pt': pt})
    sees = any((h['name'] or '').startswith('WN_south_wood_LiDAR') for h in hits)
    rec = {'loc': list(loc), 'tgt': list(tgt), 'lens': lens, 'hits': hits, 'sees_wn': sees}
    tried.append(rec)
    print('TRY', loc, 'sees_wn', sees, [h['name'] for h in hits], flush=True)
    if sees and picked is None:
        picked = rec
        picked_loc, picked_rot, picked_lens = locV, rot, lens

print('PICKED', json.dumps({k: picked[k] for k in ('loc', 'tgt', 'lens', 'sees_wn', 'hits')} if picked else None))
if picked:
    cam = bpy.data.objects['WN_CAM_closeup_south_wood_ground']
    cam.location = picked_loc
    cam.rotation_euler = picked_rot
    cam.data.lens = picked_lens
    bpy.ops.wm.save_mainfile()
    print('SAVED')
json.dump({'tried': tried, 'picked': picked}, open(f'{ROOT}/data/wn/cam3.json', 'w'), indent=1)
