"""um self-review: extra QXP/Footpaths/QY S-edge densify+xy after WIP closeup still shows sawtooth."""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def ensure_bak(o):
    if any(m.get('um_bak_of') == o.name for m in bpy.data.meshes):
        return
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UM_bak_' + nm[:50]; orig.use_fake_user = True
    orig['um_bak_of'] = o.name; orig['um_orig_name'] = nm
    cp.name = nm

def densify(name, y_lo, y_hi, x0, x1, rounds=8, lerp=0.60, sub_len=0.28, bevel_off=0.022):
    o = bpy.data.objects.get(name)
    if not o: return {}
    ensure_bak(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    mw = o.matrix_world; imw = mw.inverted()
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    bedges = [e for e, c in eu.items() if c == 1]
    focus_edges = []
    for e in bedges:
        for v in e.verts:
            p = mw @ v.co
            if x0 < p.x < x1 and y_lo < p.y < y_hi:
                focus_edges.append(e); break
    long = [e for e in focus_edges if e.is_valid and e.calc_length() > sub_len]
    n_sub = 0
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        n_sub = len(long)
        bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        eu = {}
        for f in bm.faces:
            for e in f.edges:
                eu[e] = eu.get(e, 0) + 1
        bedges = [e for e, c in eu.items() if c == 1]
        focus_edges = []
        for e in bedges:
            for v in e.verts:
                p = mw @ v.co
                if x0 < p.x < x1 and y_lo < p.y < y_hi:
                    focus_edges.append(e); break
    bvi = set()
    for e in focus_edges:
        bvi.update(e.verts)
    idxs = []
    for v in bvi:
        p = mw @ v.co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            idxs.append(v)
    near = set(idxs)
    for v in bm.verts:
        p = mw @ v.co
        if not (x0 < p.x < x1 and y_lo < p.y < y_hi): continue
        for u in idxs:
            q = mw @ u.co
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < 0.70 ** 2:
                near.add(v); break
    if near:
        zs = [(mw @ v.co).z for v in near]
        zmax = max(zs)
        near = {v for v in near if (mw @ v.co).z > zmax - 0.22}
        idxs = [v for v in idxs if v in near]
    n_ops = 0
    for _ in range(rounds):
        newxy = {}
        for v in near:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in near]
            if len(nbrs) < 2: continue
            ax = sum((mw @ n.co).x for n in nbrs) / len(nbrs)
            ay = sum((mw @ n.co).y for n in nbrs) / len(nbrs)
            p = mw @ v.co
            w = lerp if v in idxs else lerp * 0.55
            newxy[v] = (p.x * (1 - w) + ax * w, p.y * (1 - w) + ay * w, p.z)
        for v, (x, y, z) in newxy.items():
            v.co = imw @ Vector((x, y, z)); n_ops += 1
    n_bev = 0
    top_edges = [e for e in focus_edges if e.is_valid and all(v in near for v in e.verts)]
    if top_edges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1, affect='EDGES', profile=0.5)
            n_bev = len(top_edges)
        except Exception as e:
            print('UM sedge bevel fail', name, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    info = {'sub': n_sub, 'ops': n_ops, 'bev': n_bev, 'near': len(near)}
    print('UM sedge_extra', name, info)
    return info

log = {}
log['qxp'] = densify('QXP_pedestrian_area_313024781_paving_UNVERIFIED', 249.0, 253.5, -69, -30, rounds=12, lerp=0.66, sub_len=0.22, bevel_off=0.020)
log['qy'] = densify('QY_plaza_rim_band_313024781_UNVERIFIED', 249.0, 253.5, -69, -30, rounds=10, lerp=0.60, sub_len=0.26, bevel_off=0.018)
log['fp'] = densify('Footpaths_OSM', 245.5, 251.0, -69, -34, rounds=10, lerp=0.60, sub_len=0.26, bevel_off=0.018)
json.dump(log, open(D + 'data/um/um_sedge_extra.json', 'w'), indent=1)
print('UM sedge_extra LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
