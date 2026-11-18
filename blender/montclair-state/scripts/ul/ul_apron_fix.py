"""ul self-review: fix W apron outline soft — prior zmax-0.12 only caught a 1-vert outlier.
Use zp90 band. Stair mesh untouched. Uses existing UL_bak_* if present.
"""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def ensure_bak(o):
    if any(m.get('ul_bak_of') == o.name for m in bpy.data.meshes):
        return
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UL_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ul_bak_of'] = o.name; orig['ul_orig_name'] = nm
    cp.name = nm

def soften(o, tag, focus_box, sub_len=0.28, rounds=6, lerp=0.45, bevel_off=0.05, z_band=0.35):
    if o is None: return {}
    ensure_bak(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]  # zp90, ignore outlier spike
    top = {v for v in bm.verts if (mw @ v.co).z > zref - z_band}
    x0, x1, y0, y1 = focus_box
    focus = {v for v in top if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top
    top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    n_sub = 0
    for thresh in (sub_len, sub_len * 0.75, sub_len * 0.55):
        long = [e for e in top_edges if e.is_valid and e.calc_length() > thresh]
        if not long:
            continue
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        n_sub += len(long)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        zs = sorted((mw @ v.co).z for v in bm.verts)
        zref = zs[int(0.90 * (len(zs) - 1))]
        top = {v for v in bm.verts if (mw @ v.co).z > zref - z_band}
        focus = {v for v in top if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(rounds):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, lerp)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    n_bev = 0
    if top_edges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                            affect='EDGES', profile=0.5)
            n_bev = len(top_edges)
        except Exception as e:
            print('UL apron_fix bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['ul_touched'] = 1
    o['UNVERIFIED_ul_w'] = f'{tag} zp90 densify+xy-smooth+bevel UNVERIFIED (ul); stair not erased'
    info = {'tag': tag, 'sub': n_sub, 'bev': n_bev, 'verts': len(o.data.vertices),
            'focus': len(focus), 'top': len(top), 'zref': zref}
    print('UL apron_fix', info)
    return info

log = {}
apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
walk404 = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
# DO NOT touch stair
log['apron'] = soften(apron, 'apron', (-110, -96, 243, 258),
                      sub_len=0.30, rounds=7, lerp=0.48, bevel_off=0.055, z_band=0.40)
log['w404'] = soften(walk404, 'walk404', (-110, -96, 243, 258),
                     sub_len=0.28, rounds=6, lerp=0.42, bevel_off=0.040, z_band=0.25)
json.dump(log, open(D + 'data/ul/ul_apron_fix.json', 'w'), indent=1)
print('UL apron_fix LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
