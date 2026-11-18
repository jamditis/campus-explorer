"""un: apron/w399 forced xy-smooth + light boundary bevel (no length gate). Stair untouched."""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def soft(o, tag, box, rounds=8, lerp=0.52, bevel_off=0.032, z_band=0.40):
    if o is None: return {}
    # ensure true bak exists (already should)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top = {v for v in bm.verts if (mw @ v.co).z > zref - z_band}
    x0,x1,y0,y1 = box
    focus = {v for v in top if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top
    n_ops = 0
    for _ in range(rounds):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, lerp)
            coords[v] = Vector((nc.x, nc.y, v.co.z)); n_ops += 1
        for v,c in coords.items():
            v.co = c
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    bedges = [e for e,c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
    n_bev = 0
    if bedges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=bedges[:], offset=bevel_off, segments=1, affect='EDGES', profile=0.5)
            n_bev = len(bedges)
        except Exception as e:
            print('UN soft2 bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['UNVERIFIED_un_w'] = f'{tag} xy+boundary bevel UNVERIFIED (un); stair not erased'
    info = {'tag': tag, 'ops': n_ops, 'bev': n_bev, 'verts': len(o.data.vertices), 'focus': len(focus), 'bedges': len(bedges)}
    print('UN soft2', info)
    return info

log = {}
apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
w399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
log['apron'] = soft(apron, 'apron', (-110,-96,243,258), rounds=8, lerp=0.52, bevel_off=0.032)
log['w399'] = soft(w399, 'walk399', (-110,-96,243,258), rounds=5, lerp=0.38, bevel_off=0.018, z_band=0.25)
json.dump(log, open(D + 'data/un/un_apron_soft2.json', 'w'), indent=1)
print('UN soft2 LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
