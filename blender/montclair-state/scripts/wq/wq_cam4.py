"""Diagnose black NW eye cam; reframe onto open lawn south/west of Stone."""
import bpy, json, math
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree

ROOT = '/workspace/nj-scenes/montclair-state'
dg = bpy.context.evaluated_depsgraph_get()
sc = bpy.context.scene

def look_rot(loc, tgt):
    d = Vector(tgt) - Vector(loc)
    return Euler((math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                  math.atan2(d.y, d.x) - math.pi / 2))

cam = bpy.data.objects['WQ_CAM_eye_south_wood_from_NW']
loc = cam.location.copy()
print('CAM', list(loc), 'lens', cam.data.lens, flush=True)

# what's around the camera
around = []
pt = loc
for o in bpy.data.objects:
    if o.type != 'MESH' or not o.data:
        continue
    try:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    except Exception:
        continue
    xs = [p.x for p in bb]; ys = [p.y for p in bb]; zs = [p.z for p in bb]
    if min(xs)-1 <= pt.x <= max(xs)+1 and min(ys)-1 <= pt.y <= max(ys)+1 and min(zs)-1 <= pt.z <= max(zs)+1:
        around.append([o.name, round(min(xs),1), round(max(xs),1), round(min(ys),1), round(max(ys),1),
                       round(min(zs),1), round(max(zs),1)])
print('AROUND', len(around), flush=True)
for a in around[:30]:
    print(' ', a, flush=True)

# forward ray
fwd = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
hit = sc.ray_cast(dg, loc, fwd, distance=80)
print('FWD', fwd, 'hit', hit[0], hit[4].name if hit[0] and hit[4] else None,
      [round(c,2) for c in hit[1]] if hit[0] else None, flush=True)

# ground at a few candidate spots via Terrain + QG
def gnd(x, y):
    best = None
    bestn = None
    for n in ('Terrain_LiDAR_DTM_1m', 'QG_north_strip_LiDAR_terrain_patch',
              'QH_east_fan_LiDAR_terrain_patch', 'QI_east_edge_LiDAR_terrain_patch'):
        o = bpy.data.objects.get(n)
        if not o:
            continue
        e = o.evaluated_get(dg)
        m = e.to_mesh()
        vs = [o.matrix_world @ v.co for v in m.vertices]
        b = BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in m.polygons])
        e.to_mesh_clear()
        h = b.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)))
        if h[0] is not None and (best is None or h[0].z > best):
            best = h[0].z
            bestn = n
    return best, bestn

cands = [
    ((145, 208), (175, 175), 32),
    ((142, 206), (172, 178), 32),
    ((138, 205), (175, 180), 30),
    ((218, 220), (180, 190), 30),
    ((215, 205), (175, 185), 32),
    ((210, 155), (175, 185), 32),
    ((125, 195), (172, 180), 32),
    ((130, 190), (170, 185), 30),
]
tried = []
picked = None
for xy, txy, lens in cands:
    zg, gn = gnd(*xy)
    tz, tn = gnd(*txy)
    if zg is None:
        print('NOGND', xy, flush=True)
        continue
    loc2 = Vector((xy[0], xy[1], zg + 1.7))
    tgt2 = Vector((txy[0], txy[1], (tz if tz is not None else zg) + 5.0))
    rot = look_rot(loc2, tgt2)
    look = rot.to_matrix() @ Vector((0, 0, -1))
    h = sc.ray_cast(dg, loc2, look, distance=80)
    hname = h[4].name if h[0] and h[4] else None
    hpt = [round(c, 2) for c in h[1]] if h[0] else None
    dist = (Vector(h[1]) - loc2).length if h[0] else None
    rec = {'loc': [round(c, 2) for c in loc2], 'tgt': [round(c, 2) for c in tgt2],
           'lens': lens, 'gnd': gn, 'zg': round(zg, 2),
           'hit': hname, 'hit_pt': hpt, 'hit_dist': None if dist is None else round(dist, 2)}
    tried.append(rec)
    print('TRY', rec, flush=True)
    # accept if first hit is not immediately in front (<4 m) and not a building wall name
    bad = False
    if dist is not None and dist < 4.0:
        bad = True
    if hname and any(k in hname.lower() for k in ('wall', 'richardson', 'stone hall', 'reid', 'building')):
        if dist is not None and dist < 25:
            bad = True
    if not bad and picked is None:
        picked = rec

print('PICKED', picked, flush=True)
if picked:
    cam.location = Vector(picked['loc'])
    cam.rotation_euler = look_rot(picked['loc'], picked['tgt'])
    cam.data.lens = picked['lens']
    cam.data.clip_start = 0.2
    cam.data.clip_end = 30000
    bpy.ops.wm.save_mainfile()
    print('SAVED', flush=True)

json.dump({'old_around': around, 'tried': tried, 'picked': picked},
          open(f'{ROOT}/data/wq/cam4.json', 'w'), indent=1)
