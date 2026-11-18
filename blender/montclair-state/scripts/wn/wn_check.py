"""wn verify: tree seating, y=292 WJ/WN join (sample inside each mesh). Read-only."""
import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = '/workspace/nj-scenes/montclair-state'
dg = bpy.context.evaluated_depsgraph_get()

def bvh(n):
    o = bpy.data.objects[n]
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    vs = [o.matrix_world @ v.co for v in m.vertices]
    b = BVHTree.FromPolygons(vs, [tuple(p.vertices) for p in m.polygons])
    e.to_mesh_clear()
    return b

bn = bvh('WN_south_wood_LiDAR_patch_ext_UNVERIFIED')
be = bvh('WJ_south_gully_LiDAR_patch_ext_UNVERIFIED')
sk = bvh('Context_skirt_3DEP_ortho_4km')

def hz(b, x, y):
    h = b.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)))
    return h[0].z if h[0] is not None else None

rep = {'join': [], 'trees_bad': []}
for x in range(182, 246, 4):
    zn = hz(bn, x, 291.5)   # inside WN
    zj = hz(be, x, 292.5)   # inside WJ
    zne = hz(bn, x, 291.99)
    zje = hz(be, x, 292.01)
    d = None if (zn is None or zj is None) else round(zn - zj, 3)
    de = None if (zne is None or zje is None) else round(zne - zje, 3)
    rep['join'].append({
        'x': x,
        'wn_291.5': None if zn is None else round(zn, 2),
        'wj_292.5': None if zj is None else round(zj, 2),
        'd_0.5in': d,
        'wn_291.99': None if zne is None else round(zne, 2),
        'wj_292.01': None if zje is None else round(zje, 2),
        'd_edge': de,
    })

offs = []
for o in bpy.data.objects:
    if not o.name.startswith('WM_south_wood_tree_'):
        continue
    t = o.matrix_world.translation
    bb = min((o.matrix_world @ Vector(c)).z for c in o.bound_box)
    g = hz(bn, t.x, t.y) or hz(sk, t.x, t.y)
    off = None if g is None else round(bb - (g - 0.25), 3)
    offs.append(off)
    if off is None or abs(off) > 0.2:
        rep['trees_bad'].append([o.name, round(t.x, 1), round(t.y, 1),
                                 None if g is None else round(g, 2), round(bb, 2), off])
rep['n_wm'] = len(offs)
rep['tree_off_max'] = None if not offs else max(abs(o) for o in offs if o is not None)
ds = [r['d_edge'] for r in rep['join'] if r['d_edge'] is not None]
d2 = [r['d_0.5in'] for r in rep['join'] if r['d_0.5in'] is not None]
rep['join_edge_max'] = None if not ds else max(abs(v) for v in ds)
rep['join_in_max'] = None if not d2 else max(abs(v) for v in d2)
rep['cam'] = [round(c, 2) for c in bpy.data.objects['WN_CAM_closeup_south_wood_ground'].location]
print('SUMMARY', json.dumps({k: rep[k] for k in (
    'n_wm', 'tree_off_max', 'trees_bad', 'join_edge_max', 'join_in_max', 'cam')}, indent=1))
print('JOIN', json.dumps(rep['join']))
json.dump(rep, open(f'{ROOT}/data/wn/check.json', 'w'), indent=1)
