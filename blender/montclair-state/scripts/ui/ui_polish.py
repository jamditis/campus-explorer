"""ui self-review polish: soften Footpaths S edge along Partridge E lawn strip + light QXP S boundary.
Assumes ui_main already applied (uses existing UI_bak_*). REVERT still via ui_main REVERT=1.
"""
import bpy, os
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def ensure_bak(o):
    if any(m.get('ui_bak_of') == o.name for m in bpy.data.meshes):
        return
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UI_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ui_bak_of'] = o.name; orig['ui_orig_name'] = nm
    cp.name = nm

# Footpaths along strip south edge (walk ↔ lawn)
fp = bpy.data.objects.get('Footpaths_OSM')
nfp = 0
if fp:
    ensure_bak(fp)
    me = fp.data; mw = fp.matrix_world; imw = mw.inverted()
    idxs = [v.index for v in me.vertices
            if -68 < (mw @ v.co).x < -35 and 245.0 < (mw @ v.co).y < 249.0]
    for _ in range(6):
        adj = {}
        for e in me.edges:
            a, b = e.vertices
            if a in idxs or b in idxs:
                adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
        newxy = {}
        for vi in idxs:
            nbr = adj.get(vi, [])
            if len(nbr) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbr) / len(nbr)
            ay = sum((mw @ me.vertices[j].co).y for j in nbr) / len(nbr)
            p = mw @ me.vertices[vi].co
            newxy[vi] = (0.5 * p.x + 0.5 * ax, 0.5 * p.y + 0.5 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nfp += 1
    me.update()
print('UI polish Footpaths strip-edge ops', nfp)

# QXP remaining S-boundary xy smooth a bit more
o = bpy.data.objects.get('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
nq = 0
if o:
    ensure_bak(o)
    me = o.data; mw = o.matrix_world; imw = mw.inverted()
    idxs = [v.index for v in me.vertices
            if -68 < (mw @ v.co).x < -30 and 249.5 < (mw @ v.co).y < 253.0]
    zs = [(mw @ me.vertices[i].co).z for i in idxs] or [0]
    zmax = max(zs)
    top = [i for i in idxs if (mw @ me.vertices[i].co).z > zmax - 0.12]
    for _ in range(5):
        adj = {}
        for e in me.edges:
            a, b = e.vertices
            if a in top or b in top:
                adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
        newxy = {}
        for vi in top:
            nbr = [j for j in adj.get(vi, []) if j in top]
            if len(nbr) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbr) / len(nbr)
            ay = sum((mw @ me.vertices[j].co).y for j in nbr) / len(nbr)
            p = mw @ me.vertices[vi].co
            newxy[vi] = (0.55 * p.x + 0.45 * ax, 0.55 * p.y + 0.45 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nq += 1
    me.update()
print('UI polish QXP S-edge ops', nq)

open(D + 'data/ui/ui_polish.json', 'w').write('{"fp":%d,"qxp":%d}\n' % (nfp, nq))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
