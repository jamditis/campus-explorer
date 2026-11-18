"""un: apron/w399 restore from true UN_bak_* + boundary xy + mild bevel."""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def find_true_bak(name):
    cands = [m for m in bpy.data.meshes if m.get('un_bak_of') == name]
    # prefer name starting UN_bak_ and fake_user
    pref = [m for m in cands if m.name.startswith('UN_bak_') and m.use_fake_user]
    if pref:
        return min(pref, key=lambda m: len(m.vertices))  # original pre-un is smallest
    pref = [m for m in cands if m.name.startswith('UN_bak_')]
    if pref:
        return min(pref, key=lambda m: len(m.vertices))
    return min(cands, key=lambda m: len(m.vertices)) if cands else None

def restore(name):
    o = bpy.data.objects.get(name)
    bak = find_true_bak(name)
    if not o or not bak:
        return None, None, f'miss o={bool(o)} bak={bool(bak)}'
    # scrub inherited un_bak_of from any non-bak meshes pointing here
    for m in list(bpy.data.meshes):
        if m.get('un_bak_of') == name and m is not bak and not m.name.startswith('UN_bak_'):
            if 'un_bak_of' in m: del m['un_bak_of']
            if 'un_orig_name' in m: del m['un_orig_name']
    bak_verts = len(bak.vertices)
    mod = o.data
    mod_name = mod.name
    cp = bak.copy()
    # ensure copy does NOT look like a bak
    if 'un_bak_of' in cp: del cp['un_bak_of']
    if 'un_orig_name' in cp: del cp['un_orig_name']
    cp.use_fake_user = False
    o.data = cp
    cp.name = mod_name
    if mod.users == 0 and mod is not bak:
        bpy.data.meshes.remove(mod)
    print('UN restore', name, 'from', bak.name, 'verts', bak_verts, 'now', len(o.data.vertices))
    return o, bak_verts, 'ok'

def soft_boundary(o, tag, box, rounds=6, lerp=0.48, sub_len=0.35, bevel_off=0.028, z_band=0.35):
    if o is None: return {}
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top = {v for v in bm.verts if (mw @ v.co).z > zref - z_band}
    x0,x1,y0,y1 = box
    focus = {v for v in top if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    bedges = [e for e,c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
    n_sub = 0
    long = [e for e in bedges if e.calc_length() > sub_len]
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1); n_sub = len(long)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        zs = sorted((mw @ v.co).z for v in bm.verts)
        zref = zs[int(0.90 * (len(zs) - 1))]
        top = {v for v in bm.verts if (mw @ v.co).z > zref - z_band}
        focus = {v for v in top if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top
        eu = {}
        for f in bm.faces:
            for e in f.edges:
                eu[e] = eu.get(e, 0) + 1
        bedges = [e for e,c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(rounds):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, lerp)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v,c in coords.items():
            v.co = c
    n_bev = 0
    if bedges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=bedges[:], offset=bevel_off, segments=1, affect='EDGES', profile=0.5)
            n_bev = len(bedges)
        except Exception as e:
            print('UN mild bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['UNVERIFIED_un_w'] = f'{tag} boundary densify+xy+mild bevel UNVERIFIED (un); stair not erased'
    info = {'tag': tag, 'sub': n_sub, 'bev': n_bev, 'verts': len(o.data.vertices), 'focus': len(focus)}
    print('UN apron_mild', info)
    return info

log = {}
apron, av, st = restore('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
log['apron_status'] = st; log['apron_bak'] = av
log['apron'] = soft_boundary(apron, 'apron', (-110,-96,243,258), rounds=7, lerp=0.50, sub_len=0.32, bevel_off=0.030) if st=='ok' else {}
w399, wv, st2 = restore('TY_footway_313026399_to_Partridge_UNVERIFIED')
log['w399_status'] = st2; log['w399_bak'] = wv
log['w399'] = soft_boundary(w399, 'walk399', (-110,-96,243,258), rounds=4, lerp=0.36, sub_len=0.34, bevel_off=0.018, z_band=0.25) if st2=='ok' else {}
json.dump(log, open(D + 'data/un/un_apron_mild.json', 'w'), indent=1)
print('UN apron_mild LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
