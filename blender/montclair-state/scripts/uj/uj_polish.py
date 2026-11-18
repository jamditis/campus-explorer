"""uj self-review polish: close UG↔SA ~15 cm coverage gap + stronger S-edge/apron soft.
Assumes uj_main already applied (uses existing UJ_bak_*). REVERT still via uj_main REVERT=1.
"""
import bpy, bmesh, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
XA, XB = -67.5, -35.5

def ensure_bak(o):
    if any(m.get('uj_bak_of') == o.name for m in bpy.data.meshes):
        return
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UJ_bak_' + nm[:50]; orig.use_fake_user = True
    orig['uj_bak_of'] = o.name; orig['uj_orig_name'] = nm
    cp.name = nm

dg = bpy.context.evaluated_depsgraph_get()
def caster(n):
    o = bpy.data.objects.get(n)
    if not o: return lambda x, y: (None, None)
    e = o.evaluated_get(dg); mw = o.matrix_world; iw = mw.inverted()
    d = (iw.to_3x3() @ Vector((0, 0, -1))).normalized()
    def f(x, y):
        r = e.ray_cast(iw @ Vector((x, y, 400)), d)
        return ((mw @ r[1]).z, r[3]) if r[0] else (None, None)
    return f

log = {}

# ---- 1) Extend UG N boundary north ~0.40 m; SA S boundary south ~0.40 m ----
ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
ensure_bak(ugo)
ume = ugo.data; umw = ugo.matrix_world; uimw = umw.inverted()
# N-boundary verts of UG in strip: high y, few faces north
eu = {}
for p in ume.polygons:
    for ek in p.edge_keys:
        eu[ek] = eu.get(ek, 0) + 1
bvi = set()
for ek, c in eu.items():
    if c == 1: bvi.update(ek)
n_push = 0
for vi in bvi:
    v = ume.vertices[vi]; p = umw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if p.y < 249.8: continue
    # push north
    p.y += 0.42; v.co = uimw @ p; n_push += 1
ume.update(); log['ug_n_push'] = n_push
print('UJ polish UG N push', n_push)

sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
ensure_bak(sao)
sme = sao.data; smw = sao.matrix_world; simw = smw.inverted()
eu2 = {}
for p in sme.polygons:
    for ek in p.edge_keys:
        eu2[ek] = eu2.get(ek, 0) + 1
bvi2 = set()
for ek, c in eu2.items():
    if c == 1: bvi2.update(ek)
n_spush = 0
for vi in bvi2:
    v = sme.vertices[vi]; p = smw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if not (250.2 < p.y < 252.5): continue
    p.y -= 0.42; v.co = simw @ p; n_spush += 1
sme.update(); log['sa_s_push'] = n_spush
print('UJ polish SA S push', n_spush)

# ---- 2) Re-feather z across the new overlap ----
dg = bpy.context.evaluated_depsgraph_get()
UG = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA = caster('SA_ground_lower_patch_UNVERIFIED')

n_ug = 0
for v in ume.vertices:
    p = umw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if p.y < 249.5: continue
    saz = None
    for dy in (0.0, 0.3, 0.6, 1.0, 1.5):
        saz, _ = SA(p.x, p.y + dy)
        if saz is not None: break
    if saz is None: continue
    t = min(1.0, max(0.0, (p.y - 249.5) / 2.8))
    target = p.z * (1 - t) + (saz + 0.002) * t
    if abs(target - p.z) > 0.001:
        p.z = target; v.co = uimw @ p; n_ug += 1
ume.update(); log['ug_refeather'] = n_ug
print('UJ polish UG refeather', n_ug)

dg = bpy.context.evaluated_depsgraph_get(); UG2 = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
n_sa = 0
for v in sme.vertices:
    p = smw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if not (249.6 < p.y < 253.5): continue
    ugz, _ = UG2(p.x, min(p.y, 250.8))
    if ugz is None:
        ugz, _ = UG2(p.x, 250.4)
    if ugz is None: continue
    # blend SA toward UG in overlap
    t = min(1.0, max(0.0, (252.8 - p.y) / 3.0))
    target = p.z * (1 - 0.65 * t) + (ugz - 0.003) * (0.65 * t)
    if abs(target - p.z) > 0.0012:
        p.z = target; v.co = simw @ p; n_sa += 1
sme.update(); log['sa_refeather'] = n_sa
print('UJ polish SA refeather', n_sa)

# ---- 3) Stronger QXP / Footpaths S-edge xy smooth (top near-boundary) ----
def xy_smooth(name, y_lo, y_hi, x0, x1, rounds=8, lerp=0.62):
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
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < 0.65 ** 2:
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
    me.update(); print('UJ polish', name, 'ops', n, 'near', len(near)); return n

log['qxp'] = xy_smooth('QXP_pedestrian_area_313024781_paving_UNVERIFIED', 249.0, 253.5, -69, -30)
log['qy'] = xy_smooth('QY_plaza_rim_band_313024781_UNVERIFIED', 249.0, 253.5, -69, -30, rounds=6, lerp=0.55)
log['fp'] = xy_smooth('Footpaths_OSM', 245.0, 251.0, -69, -34, rounds=7, lerp=0.55)

# ---- 4) Extra apron outline soft (gentle; stair untouched) ----
apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
if apron:
    ensure_bak(apron)
    bm = bmesh.new(); bm.from_mesh(apron.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    mw = apron.matrix_world
    wz = [(v, (mw @ v.co).z) for v in bm.verts]
    zmax = max(z for _, z in wz)
    top = {v for v, z in wz if z > zmax - 0.12}
    focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
    for _ in range(3):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, 0.35)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    bm.to_mesh(apron.data); bm.free(); apron.data.update()
    log['apron'] = len(apron.data.vertices)
    print('UJ polish apron verts', log['apron'])

json.dump(log, open(D + 'data/uj/uj_polish.json', 'w'), indent=1)
print('UJ polish LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
