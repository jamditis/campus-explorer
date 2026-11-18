"""un: tone apron densify if un_main over-subdivided; restore from UN_bak then mild zp90 soft. Stair untouched."""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
name = 'TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)'
o = bpy.data.objects.get(name)
bak = next((m for m in bpy.data.meshes if m.get('un_bak_of') == name), None)
log = {'pre_verts': len(o.data.vertices) if o else None}
if o and bak:
    mod = o.data
    o.data = bak.copy()
    o.data.name = mod.name
    if mod.users == 0:
        bpy.data.meshes.remove(mod)
    log['restored_from_bak_verts'] = len(bak.vertices)
    print('UN apron restored from bak verts', len(o.data.vertices))
else:
    print('UN apron bak miss', bool(o), bool(bak))

def soften_mild(o):
    if o is None:
        return {}
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.40}
    focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
    top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    n_sub = 0
    for thresh in (0.30, 0.22):
        long = [e for e in top_edges if e.is_valid and e.calc_length() > thresh]
        if not long:
            continue
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        n_sub += len(long)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        zs = sorted((mw @ v.co).z for v in bm.verts)
        zref = zs[int(0.90 * (len(zs) - 1))]
        top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.40}
        focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(6):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2:
                continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, 0.46)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    n_bev = 0
    if top_edges:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=0.034, segments=1, affect='EDGES', profile=0.5)
            n_bev = len(top_edges)
        except Exception as e:
            print('UN apron_tone bevel fail', e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['UNVERIFIED_un_w'] = 'apron mild zp90 densify+xy+bevel UNVERIFIED (un); stair not erased'
    return {'sub': n_sub, 'bev': n_bev, 'verts': len(o.data.vertices), 'focus': len(focus)}

log['apron'] = soften_mild(o)
# also tone walk399 if exploded
w399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
bak399 = next((m for m in bpy.data.meshes if m.get('un_bak_of') == 'TY_footway_313026399_to_Partridge_UNVERIFIED'), None)
log['w399_pre'] = len(w399.data.vertices) if w399 else None
if w399 and bak399 and len(w399.data.vertices) > 12000:
    mod = w399.data
    w399.data = bak399.copy()
    w399.data.name = mod.name
    if mod.users == 0:
        bpy.data.meshes.remove(mod)
    bm = bmesh.new(); bm.from_mesh(w399.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = w399.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.30}
    focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
    top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    long = [e for e in top_edges if e.calc_length() > 0.30]
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        zs = sorted((mw @ v.co).z for v in bm.verts)
        zref = zs[int(0.90 * (len(zs) - 1))]
        top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.30}
        focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(4):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2:
                continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, 0.36)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    if top_edges:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=0.020, segments=1, affect='EDGES', profile=0.5)
        except Exception as e:
            print('UN w399 tone bevel fail', e)
    bm.to_mesh(w399.data); bm.free(); w399.data.update()
    log['w399_toned'] = len(w399.data.vertices)
    print('UN w399 toned verts', log['w399_toned'])
else:
    log['w399_toned'] = 'skipped'
json.dump(log, open(D + 'data/un/un_apron_tone.json', 'w'), indent=1)
print('UN apron_tone LOG', log)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
