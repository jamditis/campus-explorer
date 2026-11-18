"""um self-review: tone down over-aggressive walk404 bevel from apron_fix; keep apron.
Restores walk404 from UM_bak_* then applies milder soften. Stair untouched.
"""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

# restore walk404 only from its UM bak
name = 'TY_footway_313026404_to_Partridge_UNVERIFIED'
o = bpy.data.objects.get(name)
bak = next((m for m in bpy.data.meshes if m.get('um_bak_of') == name), None)
if o and bak:
    mod = o.data; o.data = bak.copy(); o.data.name = mod.name
    if mod.users == 0: bpy.data.meshes.remove(mod)
    # keep bak as the pre-um original still
    print('UM w404 restored from bak verts', len(o.data.vertices))
else:
    print('UM w404 bak miss', bool(o), bool(bak))
    if o and not bak:
        orig = o.data; nm = orig.name
        cp = orig.copy(); o.data = cp
        orig.name = 'UM_bak_' + nm[:50]; orig.use_fake_user = True
        orig['um_bak_of'] = name; orig['um_orig_name'] = nm
        cp.name = nm
        print('UM w404 bak created from current verts', len(orig.vertices))

def soften_mild(o):
    if o is None: return {}
    # bak already exists
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.20}
    focus = {v for v in top if -108 < (mw @ v.co).x < -97 and 245 < (mw @ v.co).y < 255} or top
    # only boundary edges of focus
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    bedges = [e for e, c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
    long = [e for e in bedges if e.calc_length() > 0.32]
    n_sub = 0
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        n_sub = len(long)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        zs = sorted((mw @ v.co).z for v in bm.verts)
        zref = zs[int(0.90 * (len(zs) - 1))]
        top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.20}
        focus = {v for v in top if -108 < (mw @ v.co).x < -97 and 245 < (mw @ v.co).y < 255} or top
        eu = {}
        for f in bm.faces:
            for e in f.edges:
                eu[e] = eu.get(e, 0) + 1
        bedges = [e for e, c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(5):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, 0.40)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    n_bev = 0
    if bedges:
        try:
            bmesh.ops.bevel(bm, geom=bedges[:], offset=0.028, segments=1, affect='EDGES', profile=0.5)
            n_bev = len(bedges)
        except Exception as e:
            print('UM w404 bevel fail', e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['UNVERIFIED_um_w'] = 'walk404 mild boundary densify+xy-smooth+bevel UNVERIFIED (um); stair not erased'
    info = {'sub': n_sub, 'bev': n_bev, 'verts': len(o.data.vertices), 'focus': len(focus)}
    print('UM w404_tone', info)
    return info

log = {'w404': soften_mild(o)}
# confirm apron still densified
apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
log['apron_verts'] = len(apron.data.vertices) if apron else None
json.dump(log, open(D + 'data/um/um_w404_tone.json', 'w'), indent=1)
print('UM w404_tone LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
