"""wn: find a closeup cam that sees the new LiDAR woodland floor + a raised tree base."""
import bpy, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = '/workspace/nj-scenes/montclair-state'
dg = bpy.context.evaluated_depsgraph_get()

def bvh_obj(o):
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    vs = [o.matrix_world @ v.co for v in m.vertices]
    faces = [tuple(p.vertices) for p in m.polygons]
    b = BVHTree.FromPolygons(vs, faces) if faces else None
    e.to_mesh_clear()
    return b

WN = bpy.data.objects['WN_south_wood_LiDAR_patch_ext_UNVERIFIED']
bn = bvh_obj(WN)

def gz(x, y):
    h = bn.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)))
    return h[0].z if h[0] is not None else None

# what did the old cam hit?
old = Vector((160.0, 248.0, 137.6))
tgt0 = Vector((176.0, 258.0, 134.5))
d0 = (tgt0 - old)
# scene ray
hit = bpy.context.scene.ray_cast(dg, old, d0.normalized(), distance=d0.length + 5)
rep = {'old_hit': None}
if hit[0]:
    rep['old_hit'] = [hit[4].name if hit[4] else '?', [round(c, 2) for c in hit[1]]]

# local occlusion BVH: nearby meshes
vs_all, fs_all, names = [], [], []
base = 0
near = []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.name == WN.name:
        continue
    t = o.matrix_world.translation
    if not (145 <= t.x <= 210 and 230 <= t.y <= 280):
        # also include large objects by bbox
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        cx = sum(p.x for p in bb) / 8
        cy = sum(p.y for p in bb) / 8
        if not (145 <= cx <= 210 and 230 <= cy <= 280):
            continue
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    if len(m.vertices) > 200000:
        e.to_mesh_clear()
        continue
    vs = [o.matrix_world @ v.co for v in m.vertices]
    vs_all.extend(vs)
    fs_all.extend([tuple(p.vertices[i] + base for i in range(len(p.vertices))) for p in m.polygons])
    names.append(o.name)
    base += len(vs)
    e.to_mesh_clear()
    near.append(o.name)
tb = BVHTree.FromPolygons(vs_all, fs_all) if fs_all else None
rep['near_n'] = len(near)
rep['near'] = near[:30]

# candidates: stand on the new patch, look at tree_00 / hillside
# tree_00 169.5, 256.5, g~136
g00 = gz(169.5, 256.5)
g_t = gz(176.0, 258.0)
rep['g00'] = None if g00 is None else round(g00, 2)
candidates = [
    (178.0, 250.0, 1.7, 169.5, 256.5, 0.4),
    (184.0, 255.0, 1.65, 170.0, 258.0, 0.3),
    (174.0, 246.0, 1.8, 170.0, 258.0, 0.4),
    (188.0, 248.0, 2.2, 172.0, 257.0, 0.3),
    (182.0, 262.0, 1.7, 170.0, 257.0, 0.3),
    (190.0, 252.0, 3.0, 172.0, 258.0, 0.2),
    (172.0, 244.0, 2.0, 170.0, 258.0, 0.5),
    (186.5, 249.5, 1.8, 175.5, 257.5, 0.3),
    (165.0, 245.0, 1.8, 170.0, 258.0, 0.4),
    (195.0, 255.0, 2.5, 176.0, 258.0, 0.2),
]
tried = []
picked = None
for x, y, eh, tx, ty, th in candidates:
    g = gz(x, y)
    gt = gz(tx, ty)
    if g is None or gt is None:
        tried.append([x, y, 'no_ground'])
        continue
    loc = Vector((x, y, g + eh))
    tgt = Vector((tx, ty, gt + th))
    direc = tgt - loc
    ln = direc.length
    # inside something? small sphere
    inside = tb.ray_cast(loc, Vector((0, 0, 1)), 0.3)[0] is not None if tb else False
    hitp = tb.ray_cast(loc, direc.normalized(), ln - 0.4) if tb else (None,)
    blocked = hitp[0] is not None
    # also scene ray for buildings
    sh = bpy.context.scene.ray_cast(dg, loc, direc.normalized(), distance=ln - 0.3)
    scene_block = sh[0] and sh[4] and not sh[4].name.startswith(('WN_south', 'WM_south', 'WJ_gully', 'TL_tree', 'WF_east', 'Context_skirt'))
    rec = {
        'loc': [round(x, 1), round(y, 1), round(g + eh, 2)],
        'tgt': [round(tx, 1), round(ty, 1), round(gt + th, 2)],
        'inside': inside, 'bvh_blocked': blocked,
        'scene_hit': sh[4].name if sh[0] and sh[4] else None,
        'ok': (not inside) and (not blocked) and (not scene_block),
    }
    tried.append(rec)
    if rec['ok'] and picked is None:
        picked = rec

rep['tried'] = tried
rep['picked'] = picked
cam = bpy.data.objects['WN_CAM_closeup_south_wood_ground']
if picked:
    loc = Vector(picked['loc'])
    tgt = Vector(picked['tgt'])
    d = tgt - loc
    cam.location = loc
    cam.rotation_euler = (
        math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)),
        0,
        math.atan2(d.y, d.x) - math.pi / 2,
    )
    cam.data.lens = 32
    bpy.ops.wm.save_mainfile()
    rep['saved'] = True
print('CAM', json.dumps({k: rep[k] for k in ('old_hit', 'g00', 'picked', 'saved') if k in rep}, indent=1))
print('TRIED', json.dumps(tried, indent=1))
json.dump(rep, open(f'{ROOT}/data/wn/cam.json', 'w'), indent=1)
