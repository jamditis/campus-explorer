"""uk self-review polish: stronger W apron outline soft (stair untouched).
Assumes uk_main already applied (uses existing UK_bak_*). REVERT still via uk_main REVERT=1.
"""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def ensure_bak(o):
    if any(m.get('uk_bak_of') == o.name for m in bpy.data.meshes):
        return
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UK_bak_' + nm[:50]; orig.use_fake_user = True
    orig['uk_bak_of'] = o.name; orig['uk_orig_name'] = nm
    cp.name = nm

log = {}

# Extra apron outline soft — force densify even on medium edges
apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
if apron:
    ensure_bak(apron)
    bm = bmesh.new(); bm.from_mesh(apron.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = apron.matrix_world
    wz = [(v, (mw @ v.co).z) for v in bm.verts]
    zmax = max(z for _, z in wz)
    top = {v for v, z in wz if z > zmax - 0.14}
    focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
    top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    long = [e for e in top_edges if e.calc_length() > 0.28]
    n_sub = 0
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        n_sub = len(long)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        wz = [(v, (mw @ v.co).z) for v in bm.verts]
        zmax = max(z for _, z in wz)
        top = {v for v, z in wz if z > zmax - 0.14}
        focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(4):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, 0.40)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    if top_edges:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=0.04, segments=1, affect='EDGES', profile=0.5)
        except Exception as e:
            print('UK polish bevel fail', e)
    bm.to_mesh(apron.data); bm.free(); apron.data.update()
    log['apron_sub'] = n_sub
    log['apron_v'] = len(apron.data.vertices)
    print('UK polish apron sub', n_sub, 'verts', log['apron_v'])

# light extra QXP S-edge xy (already UK_bak)
def xy_smooth(name, y_lo, y_hi, x0, x1, rounds=6, lerp=0.55):
    o = bpy.data.objects.get(name)
    if not o: return 0
    ensure_bak(o)
    me = o.data; mw = o.matrix_world; imw = mw.inverted()
    eu = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = set()
    for ek, c in eu.items():
        if c == 1: bvi.update(ek)
    idxs = [vi for vi in bvi if x0 < (mw @ me.vertices[vi].co).x < x1
            and y_lo < (mw @ me.vertices[vi].co).y < y_hi]
    near = set(idxs)
    for v in me.vertices:
        p = mw @ v.co
        if not (x0 < p.x < x1 and y_lo < p.y < y_hi): continue
        for vi in idxs:
            q = mw @ me.vertices[vi].co
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < 0.70 ** 2:
                near.add(v.index); break
    if near:
        zs = [(mw @ me.vertices[i].co).z for i in near]
        zmax = max(zs)
        near = {i for i in near if (mw @ me.vertices[i].co).z > zmax - 0.20}
    adj = {}
    for e in me.edges:
        a, b = e.vertices
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    n = 0
    for _ in range(rounds):
        newxy = {}
        for vi in near:
            nbrs = [j for j in adj.get(vi, []) if j in near]
            if len(nbrs) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbrs) / len(nbrs)
            ay = sum((mw @ me.vertices[j].co).y for j in nbrs) / len(nbrs)
            p = mw @ me.vertices[vi].co
            w = lerp if vi in idxs else lerp * 0.55
            newxy[vi] = (p.x * (1 - w) + ax * w, p.y * (1 - w) + ay * w, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); n += 1
    me.update(); print('UK polish', name, 'ops', n); return n

log['qxp'] = xy_smooth('QXP_pedestrian_area_313024781_paving_UNVERIFIED', 249.0, 253.5, -69, -30)
log['fp'] = xy_smooth('Footpaths_OSM', 245.0, 251.0, -69, -34, rounds=5, lerp=0.50)

json.dump(log, open(D + 'data/uk/uk_polish.json', 'w'), indent=1)
print('UK polish LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
