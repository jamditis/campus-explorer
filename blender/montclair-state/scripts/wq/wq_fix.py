"""wq: plant CHM local-max trees on already-modelled LiDAR ground
south of Stone Hall (y<215, OSM wood 315835594).
Seat by lowest point (bbox min) = ground - 0.25.
Also place two eye cams + one close-up with local BVH/bbox occlusion checks.
"""
import bpy, json, math, random, numpy as np
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree

ROOT = '/workspace/nj-scenes/montclair-state'
rep = {'added': [], 'skipped': [], 'cams': []}

probe = json.load(open(f'{ROOT}/data/wq/probe.json'))
sel = probe['priority_B']['sel']

g = np.load(f'{ROOT}/data/wo/chm_grid_sw_1m.npz')
DTM = g['USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz__dtm']
GX0, GY0 = 40.0, 140.0


def dtm(x, y):
    i = int(round(x - GX0))
    j = int(round(y - GY0))
    if 0 <= j < DTM.shape[0] and 0 <= i < DTM.shape[1] and np.isfinite(DTM[j, i]):
        return float(DTM[j, i])
    return None


dg = bpy.context.evaluated_depsgraph_get()

GROUND_NAMES = [
    'Terrain_LiDAR_DTM_1m',
    'QG_north_strip_LiDAR_terrain_patch',
    'QH_east_fan_LiDAR_terrain_patch',
    'QI_east_edge_LiDAR_terrain_patch',
]


def make_bvh(name):
    o = bpy.data.objects.get(name)
    if o is None:
        return None
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    vs = [o.matrix_world @ v.co for v in m.vertices]
    b = BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in m.polygons])
    e.to_mesh_clear()
    return b


print('BVH grounds...', flush=True)
gbvhs = []
for n in GROUND_NAMES:
    b = make_bvh(n)
    print('  ', n, 'ok' if b else 'MISSING', flush=True)
    if b:
        gbvhs.append((n, b))
rep['grounds'] = [n for n, _ in gbvhs]


def ground_hit(x, y):
    best = None
    best_n = None
    for n, b in gbvhs:
        h = b.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)))
        if h[0] is not None:
            if best is None or h[0].z > best:
                best = h[0].z
                best_n = n
    return best, best_n


src = [o for o in bpy.data.collections['Trees_assets_LiDAR'].all_objects if o.type == 'MESH']
meshes = {}
for o in src:
    meshes.setdefault(o.data.name, o)
info = [(n, min(v.co.z for v in o.data.vertices),
         max(v.co.z for v in o.data.vertices) - min(v.co.z for v in o.data.vertices))
        for n, o in meshes.items()]

ex = []
for o in bpy.data.objects:
    n = o.name
    if n.startswith(('TL_tree_', 'WJ_gully_tree_', 'WM_south_wood_tree_', 'WQ_south_wood_tree_')):
        t = o.matrix_world.translation
        ex.append(Vector((t.x, t.y, 0)))
    elif o in src:
        t = o.matrix_world.translation
        ex.append(Vector((t.x, t.y, 0)))

# any other tree-ish mesh already in the plant box
near_existing = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    if 'tree' not in o.name.lower():
        continue
    t = o.matrix_world.translation
    if 120 <= t.x <= 220 and 130 <= t.y <= 230:
        near_existing.append([o.name, round(t.x, 2), round(t.y, 2)])
        ex.append(Vector((t.x, t.y, 0)))
rep['existing_trees_in_wide_box'] = near_existing

parent = bpy.data.collections.get('TL_dorm_trees_LiDAR_UNVERIFIED')
col = bpy.data.collections.get('WQ_south_wood_trees_UNVERIFIED')
if col is None:
    col = bpy.data.collections.new('WQ_south_wood_trees_UNVERIFIED')
    linked = False
    if parent:
        for c in bpy.data.collections:
            if parent.name in c.children:
                c.children.link(col)
                linked = True
                break
    if not linked:
        bpy.context.scene.collection.children.link(col)
col['wq_col'] = 1
col['UNVERIFIED'] = 'wq: CHM trees south of Stone Hall on existing LiDAR (y<215, OSM wood 315835594)'

rng = random.Random(202611081)
k = 0
for rec in sorted(sel, key=lambda r: (r['y'], r['x'])):
    x, y, h = rec['x'], rec['y'], rec['h']
    if any(math.hypot(e.x - x, e.y - y) < 4.5 for e in ex):
        rep['skipped'].append(['near_existing', round(x, 2), round(y, 2)])
        continue
    zg, gn = ground_hit(x, y)
    if zg is None:
        rep['skipped'].append(['no_ground', round(x, 2), round(y, 2)])
        continue
    hh = min(26.0, float(h))
    n, zmin, mh = info[rng.randrange(len(info))]
    s = max(0.45, min(2.2, hh / mh))
    name = 'WQ_south_wood_tree_%02d_UNVERIFIED' % k
    # replace if re-run
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    ob = bpy.data.objects.new(name, meshes[n].data)
    col.objects.link(ob)
    ob['wq_obj'] = 1
    ob['UNVERIFIED'] = (
        'wq: 2017 LiDAR CHM local max south of Stone Hall / south of the litter-mask box '
        '(h=%.1f m, capped 26), seated on existing LiDAR %s by lowest point = ground-0.25; '
        'species/model approximated; OSM natural=wood 315835594' % (hh, gn)
    )
    yaw = rng.uniform(0, 2 * math.pi)
    zsc = s * rng.uniform(0.95, 1.05)
    # origin placed so bbox min z = ground - 0.25
    ob.matrix_world = (
        Matrix.Translation((x, y, zg - 0.25 - zmin * zsc))
        @ Matrix.Rotation(yaw, 4, 'Z')
        @ Matrix.Diagonal((s, s, zsc, 1))
    )
    bb = min((ob.matrix_world @ Vector(c)).z for c in ob.bound_box)
    ex.append(Vector((x, y, 0)))
    rec_out = {
        'n': name, 'x': round(x, 2), 'y': round(y, 2),
        'h': round(hh, 2), 'raw_h': rec.get('raw_chm'),
        'ground': gn, 'zg': round(zg, 2),
        'bbox_min': round(bb, 2), 'bbox_minus_g': round(bb - zg, 3),
        'asset': n, 'scale': round(s, 3),
    }
    rep['added'].append(rec_out)
    k += 1

print('PLANTED', k, 'skipped', len(rep['skipped']), flush=True)


# ---------- cameras ----------
def look_rot(loc, tgt):
    d = Vector(tgt) - Vector(loc)
    return Euler((math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                  math.atan2(d.y, d.x) - math.pi / 2))


# local tree occupancy: origin + rough crown radius from scale
crowns = []
for rec_out in rep['added']:
    o = bpy.data.objects[rec_out['n']]
    t = o.matrix_world.translation
    zs = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    xs_ = [(o.matrix_world @ Vector(c)).x for c in o.bound_box]
    ys_ = [(o.matrix_world @ Vector(c)).y for c in o.bound_box]
    r = max(max(xs_) - min(xs_), max(ys_) - min(ys_)) / 2
    crowns.append((t.x, t.y, min(zs), max(zs), max(r, 3.0), rec_out['n']))


def inside_crown(x, y, z, margin=1.5):
    hits = []
    for cx, cy, z0, z1, r, n in crowns:
        if (x - cx) ** 2 + (y - cy) ** 2 <= (r + margin) ** 2 and (z0 - 1) <= z <= (z1 + 1):
            hits.append(n)
    return hits


def near_plane_blocked(loc, tgt, near=6.0):
    """True if a crown intersects the first `near` metres of the look ray."""
    locV, tgtV = Vector(loc), Vector(tgt)
    d = tgtV - locV
    L = d.length
    if L < 1e-6:
        return True, ['zero_dir']
    dn = d.normalized()
    blocked = []
    for s in np.linspace(0.3, near, 12):
        p = locV + dn * s
        hs = inside_crown(p.x, p.y, p.z, margin=0.8)
        if hs:
            blocked.extend(hs)
    return (len(blocked) > 0), list(dict.fromkeys(blocked))


def ensure_cam(name, loc, tgt, lens):
    cam = bpy.data.objects.get(name)
    if cam is None:
        cd = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cd)
        bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector(loc)
    cam.rotation_euler = look_rot(loc, tgt)
    cam.data.lens = lens
    cam.data.clip_end = 30000
    cam['wq_obj'] = 1
    cam['UNVERIFIED'] = 'wq review camera'
    return cam


# candidate lists: (loc, tgt, lens, kind)
# ground-relative heights from DTM + offset
def cand(xy, zoff, txy, tzoff, lens, kind):
    z = dtm(*xy)
    tz = dtm(*txy)
    if z is None:
        z = 120.0
    if tz is None:
        tz = z
    return ((xy[0], xy[1], z + zoff), (txy[0], txy[1], tz + tzoff), lens, kind)


candidates = [
    # close-up: pulled-back low obliques toward the dense y180-200 / x160-180 cluster
    cand((198, 158), 14, (170, 188), 8, 35, 'close'),
    cand((200, 170), 12, (172, 190), 7, 32, 'close'),
    cand((145, 165), 16, (170, 188), 8, 35, 'close'),
    cand((168, 145), 16, (170, 188), 8, 38, 'close'),
    cand((205, 195), 12, (175, 188), 7, 32, 'close'),
    cand((155, 205), 8, (172, 180), 6, 35, 'close'),
    cand((210, 160), 16, (175, 185), 8, 34, 'close'),
    cand((140, 190), 14, (172, 188), 7, 32, 'close'),
    # eye SE (downslope, looking NW up into the wood)
    cand((200, 160), 1.7, (168, 190), 6, 32, 'eye_se'),
    cand((205, 170), 1.8, (170, 188), 5, 30, 'eye_se'),
    cand((195, 150), 2.0, (168, 185), 6, 32, 'eye_se'),
    cand((210, 185), 1.8, (175, 188), 5, 28, 'eye_se'),
    # eye NW (just south of Stone, looking SE/S into the wood)
    cand((150, 208), 1.7, (175, 175), 5, 32, 'eye_nw'),
    cand((145, 200), 1.8, (175, 180), 6, 30, 'eye_nw'),
    cand((155, 210), 1.7, (178, 180), 5, 35, 'eye_nw'),
    cand((140, 190), 1.8, (172, 180), 5, 30, 'eye_nw'),
]

picked = {'close': None, 'eye_se': None, 'eye_nw': None}
tried = []
for loc, tgt, lens, kind in candidates:
    inn = inside_crown(*loc, margin=2.0)
    blk, who = near_plane_blocked(loc, tgt, near=7.0)
    rec = {
        'kind': kind, 'loc': [round(c, 2) for c in loc], 'tgt': [round(c, 2) for c in tgt],
        'lens': lens, 'inside': inn, 'near_blocked': blk, 'blocked_by': who,
    }
    tried.append(rec)
    print('TRY', kind, rec['loc'], 'inside', inn, 'blocked', who, flush=True)
    if inn or blk:
        continue
    if picked[kind] is None:
        picked[kind] = rec

# fallbacks: take the candidate farthest from any crown even if near-blocked
for kind in picked:
    if picked[kind] is None:
        opts = [t for t in tried if t['kind'] == kind and not t['inside']]
        if not opts:
            opts = [t for t in tried if t['kind'] == kind]
        if opts:
            picked[kind] = min(opts, key=lambda t: (t['near_blocked'], len(t['blocked_by'])))

cam_names = {
    'close': 'WQ_CAM_closeup_south_wood_trees',
    'eye_se': 'WQ_CAM_eye_south_wood_from_SE',
    'eye_nw': 'WQ_CAM_eye_south_wood_from_NW',
}
for kind, rec in picked.items():
    if rec is None:
        print('NO CAM', kind, flush=True)
        continue
    ensure_cam(cam_names[kind], rec['loc'], rec['tgt'], rec['lens'])
    rec['name'] = cam_names[kind]
    print('PICKED', kind, rec, flush=True)

rep['cams'] = picked
rep['cam_tried'] = tried
rep['n_added'] = len(rep['added'])
rep['n_skipped'] = len(rep['skipped'])
rep['objs'] = len(bpy.data.objects)

bpy.ops.wm.save_mainfile()
print('SAVED objs', rep['objs'], 'trees', rep['n_added'], flush=True)
json.dump(rep, open(f'{ROOT}/data/wq/fix_report.json', 'w'), indent=1)
