"""Session ur (Nov 6 2026 ~2:27–~3:12 AM ET, MAIN, day-9 leftovers): Partridge polish after uq.
Densify exhausted (uo/uq declared). Material/shader/attribute polish + light local edge ONLY.
Joe lawn strip (ui) stays — do not reverse.
A) Probe UG↔SA; strengthen join soft mats + light z re-feather (no boundary push unless gap_xy > ~0.08).
B) S-edge: attribute edge soft + material dirt/desat + xy-smooth + tiny bevel only (sub=0) — NO densify balloon.
C) W apron / 404 / 399: material dirt/edge soften + mild silhouette bevel; NO apron densify (keep ~4929); stair untouched.
D) Additive grass UR_* (~400 pts) on bald strip patches.
Cams: UR_CAM_*.
REVERT=1 restores UR_bak_* meshes and deletes ur_obj objects / ur_mat materials.
"""
import bpy, bmesh, os, json, math, random
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'; SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UR_Partridge_leftover_polish_UNVERIFIED'
XA, XB = -67.5, -35.5
Y_WALK, Y_PLAZA = 247.0, 251.2

def revert():
    for me in [m for m in bpy.data.meshes if m.get('ur_bak_of')]:
        on = me['ur_bak_of']; o = bpy.data.objects.get(on)
        if o:
            mod = o.data; o.data = me
            if mod.users == 0: bpy.data.meshes.remove(mod)
        nm = me['ur_orig_name']; del me['ur_bak_of']; del me['ur_orig_name']
        me.use_fake_user = False; me.name = nm
    for o in [o for o in list(bpy.data.objects) if o.get('ur_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            (bpy.data.meshes if t == 'MESH' else bpy.data.cameras).remove(me)
    for m in [m for m in list(bpy.data.materials) if m.get('ur_mat')]:
        on = m.get('ur_of'); orig_n = m.get('ur_orig_mat')
        o = bpy.data.objects.get(on) if on else None
        orig = bpy.data.materials.get(orig_n) if orig_n else None
        if o and orig:
            for slot in o.material_slots:
                if slot.material == m:
                    slot.material = orig
        bpy.data.materials.remove(m)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    print('UR REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def backup(o):
    if any(m.get('ur_bak_of') == o.name for m in bpy.data.meshes):
        return o.data
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UR_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ur_bak_of'] = o.name; orig['ur_orig_name'] = nm
    cp.name = nm
    return cp

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
UG = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA = caster('SA_ground_lower_patch_UNVERIFIED')

log = {'session': 'ur', 'joe_lawn_strip': 'kept (do not reverse)', 'approach': 'material/shader + tiny bevel only (densify exhausted; no balloon)'}

# ---------- A) PROBE UG↔SA join first ----------
probe = {'both': 0, 'ug_only': 0, 'sa_only': 0, 'gap_xy': 0, 'dz_samples': [], 'ug_ymax': None, 'sa_ymin': None}
xs = [XA + i * (XB - XA) / 24.0 for i in range(25)]
ys = [249.4 + i * 0.08 for i in range(40)]
ug_ys = []; sa_ys = []
for x in xs:
    for y in ys:
        ugz, _ = UG(x, y); saz, _ = SA(x, y)
        if ugz is not None and saz is not None:
            probe['both'] += 1
            probe['dz_samples'].append(abs(ugz - saz))
        elif ugz is not None:
            probe['ug_only'] += 1; ug_ys.append(y)
        elif saz is not None:
            probe['sa_only'] += 1; sa_ys.append(y)
for x in xs:
    for y in [252.5 - i * 0.05 for i in range(60)]:
        ugz, _ = UG(x, y)
        if ugz is not None:
            ug_ys.append(y); break
    for y in [249.0 + i * 0.05 for i in range(60)]:
        saz, _ = SA(x, y)
        if saz is not None:
            sa_ys.append(y); break
if ug_ys: probe['ug_ymax'] = max(ug_ys)
if sa_ys: probe['sa_ymin'] = min(sa_ys)
if probe['ug_ymax'] is not None and probe['sa_ymin'] is not None:
    probe['gap_xy'] = probe['sa_ymin'] - probe['ug_ymax']
probe['dz_p95'] = sorted(probe['dz_samples'])[int(0.95 * (len(probe['dz_samples']) - 1))] if probe['dz_samples'] else None
probe['dz_max'] = max(probe['dz_samples']) if probe['dz_samples'] else None
probe['dz_mean'] = (sum(probe['dz_samples']) / len(probe['dz_samples'])) if probe['dz_samples'] else None
probe_slim = {k: v for k, v in probe.items() if k != 'dz_samples'}
probe_slim['n_dz'] = len(probe['dz_samples'])
log['probe'] = probe_slim
json.dump(probe_slim, open(D + 'data/ur/crease_probe.json', 'w'), indent=1)
print('UR A probe', probe_slim)

do_boundary_push = (probe.get('gap_xy') or 0) > 0.08
log['boundary_push'] = bool(do_boundary_push)

ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
ume = backup(ugo); umw = ugo.matrix_world; uimw = umw.inverted()
sme = backup(sao); smw = sao.matrix_world; simw = smw.inverted()

if do_boundary_push:
    eu = {}
    for p in ume.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = {vi for ek, c in eu.items() if c == 1 for vi in ek}
    n_push = 0
    for vi in bvi:
        v = ume.vertices[vi]; p = umw @ v.co
        if not (XA - 1.0 < p.x < XB + 1.0): continue
        if p.y < 249.8: continue
        p.y += 0.30; v.co = uimw @ p; n_push += 1
    ume.update(); log['ug_n_push'] = n_push
    eu2 = {}
    for p in sme.polygons:
        for ek in p.edge_keys:
            eu2[ek] = eu2.get(ek, 0) + 1
    bvi2 = {vi for ek, c in eu2.items() if c == 1 for vi in ek}
    n_spush = 0
    for vi in bvi2:
        v = sme.vertices[vi]; p = smw @ v.co
        if not (XA - 1.0 < p.x < XB + 1.0): continue
        if not (250.2 < p.y < 252.5): continue
        p.y -= 0.30; v.co = simw @ p; n_spush += 1
    sme.update(); log['sa_s_push'] = n_spush
    print('UR A boundary push UG', n_push, 'SA', n_spush)
else:
    log['ug_n_push'] = 0; log['sa_s_push'] = 0
    print('UR A no boundary push (gap ok)')

# very light z re-feather on overlap band
dg = bpy.context.evaluated_depsgraph_get()
UG2 = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA2 = caster('SA_ground_lower_patch_UNVERIFIED')
n_ug = 0
for v in ume.vertices:
    p = umw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if p.y < 249.6: continue
    saz = None
    for dy in (0.0, 0.25, 0.5, 0.9, 1.4):
        saz, _ = SA2(p.x, p.y + dy)
        if saz is not None: break
    if saz is None: continue
    t = min(1.0, max(0.0, (p.y - 249.6) / 2.6))
    target = p.z * (1 - 0.35 * t) + (saz + 0.0015) * (0.35 * t)
    if abs(target - p.z) > 0.0008:
        p.z = target; v.co = uimw @ p; n_ug += 1
ume.update(); log['ug_refeather'] = n_ug
print('UR A ug refeather', n_ug)

dg = bpy.context.evaluated_depsgraph_get(); UG3 = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
n_sa = 0
for v in sme.vertices:
    p = smw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if not (249.7 < p.y < 253.2): continue
    ugz, _ = UG3(p.x, min(p.y, 250.9))
    if ugz is None:
        ugz, _ = UG3(p.x, 250.5)
    if ugz is None: continue
    t = min(1.0, max(0.0, (252.6 - p.y) / 2.8))
    target = p.z * (1 - 0.32 * t) + (ugz - 0.002) * (0.32 * t)
    if abs(target - p.z) > 0.0008:
        p.z = target; v.co = simw @ p; n_sa += 1
sme.update(); log['sa_refeather'] = n_sa
print('UR A sa refeather', n_sa)

# longer fade attr + stronger soft material
def ensure_join_attr(o, me, mw, y_lo, y_hi, x0, x1, attr_name='ur_join_soft'):
    if attr_name not in me.attributes:
        me.attributes.new(attr_name, 'FLOAT', 'POINT')
    attr = me.attributes[attr_name]
    n = 0
    mid = 0.5 * (y_lo + y_hi)
    half = max(0.22, 0.62 * (y_hi - y_lo))  # longer fade than uq
    for i, v in enumerate(me.vertices):
        p = mw @ v.co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            w = 1.0 - abs(p.y - mid) / half
            w = max(0.0, min(1.0, w))
            attr.data[i].value = w; n += 1
        else:
            attr.data[i].value = 0.0
    return n

n_ug_attr = ensure_join_attr(ugo, ume, umw, 249.6, 251.8, XA - 1.0, XB + 1.0)
n_sa_attr = ensure_join_attr(sao, sme, smw, 249.6, 252.0, XA - 1.0, XB + 1.0)
log['ug_join_attr'] = n_ug_attr; log['sa_join_attr'] = n_sa_attr
print('UR A join attr UG', n_ug_attr, 'SA', n_sa_attr)

def soften_lawn_mat(o, tag, fac_target=0.22):
    """Duplicate first material; bump Mix Fac on prior soft or insert UP soft multiply."""
    if not o.material_slots:
        return None
    slot = o.material_slots[0]
    if slot.material is None:
        return None
    src = slot.material
    if src.get('ur_mat') and src.get('ur_of') == o.name:
        mat = src
    else:
        mat = src.copy()
        mat.name = ('UR_' + src.name)[:60]
        mat['ur_mat'] = 1
        mat['ur_of'] = o.name
        mat['ur_orig_mat'] = src.name
        for _k in ('uq_mat','uq_of','uq_orig_mat','up_mat','uo_mat','un_mat'):
            if _k in mat: del mat[_k]  # del_inherited
        mat['UNVERIFIED'] = f'{tag} join soft material UNVERIFIED (ur)'
        src.use_fake_user = True
        slot.material = mat
    nt = mat.node_tree
    if nt is None:
        return mat.name
    prin = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if prin is None:
        return mat.name
    # bump Fac on any prior join soft mix (UN/UM/UL/UK/UP)
    bumped = False
    for n in nt.nodes:
        if (n.name.startswith(('UR_join_soft', 'UQ_join_soft', 'UP_join_soft', 'UO_join_soft', 'UN_join_soft', 'UM_join_soft', 'UL_join_soft', 'UK_join_soft'))
                and hasattr(n, 'inputs') and 'Fac' in n.inputs):
            n.inputs['Fac'].default_value = min(0.42, max(n.inputs['Fac'].default_value, fac_target))
            bumped = True
    if bumped:
        rough = prin.inputs.get('Roughness')
        if rough and not rough.is_linked:
            rough.default_value = min(1.0, max(rough.default_value, 0.74) + 0.04)
        return mat.name
    mix = nt.nodes.new('ShaderNodeMixRGB')
    mix.name = 'UR_join_soft_mix'
    mix.blend_type = 'MIX'
    mix.inputs['Fac'].default_value = fac_target
    mix.inputs['Color2'].default_value = (0.20, 0.27, 0.15, 1.0)
    base_in = prin.inputs.get('Base Color')
    if base_in and base_in.links:
        link = base_in.links[0]
        from_s = link.from_socket
        nt.links.remove(link)
        nt.links.new(from_s, mix.inputs['Color1'])
    else:
        mix.inputs['Color1'].default_value = (0.28, 0.36, 0.17, 1.0)
    nt.links.new(mix.outputs['Color'], prin.inputs['Base Color'])
    rough = prin.inputs.get('Roughness')
    if rough and not rough.is_linked:
        rough.default_value = min(1.0, max(rough.default_value, 0.74) + 0.05)
    return mat.name

log['ug_mat'] = soften_lawn_mat(ugo, 'UG', fac_target=0.38)
log['sa_mat'] = soften_lawn_mat(sao, 'SA', fac_target=0.36)
print('UR A mats', log['ug_mat'], log['sa_mat'])

# ---------- B) S-edge: attr + material soft; light densify ONLY if sparse long edges ----------
def ensure_edge_attr(o, me, mw, y_lo, y_hi, x0, x1, attr_name='ur_edge_soft'):
    if attr_name not in me.attributes:
        me.attributes.new(attr_name, 'FLOAT', 'POINT')
    attr = me.attributes[attr_name]
    # boundary verts in band get high weight
    eu = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = {vi for ek, c in eu.items() if c == 1 for vi in ek}
    n = 0
    for i, v in enumerate(me.vertices):
        p = mw @ v.co
        if x0 < p.x < x1 and y_lo < p.y < y_hi and i in bvi:
            attr.data[i].value = 1.0; n += 1
        elif x0 < p.x < x1 and y_lo < p.y < y_hi:
            # near-boundary soft falloff
            dmin = 999.0
            for j in bvi:
                q = mw @ me.vertices[j].co
                d = math.hypot(p.x - q.x, p.y - q.y)
                if d < dmin: dmin = d
                if dmin < 0.15: break
            w = max(0.0, 1.0 - dmin / 0.85)
            attr.data[i].value = w
            if w > 0.05: n += 1
        else:
            attr.data[i].value = 0.0
    return n

def soften_paving_mat(o, tag, fac=0.18):
    """Mild darken/desat on Base Color near edge (visual soft)."""
    if not o.material_slots or o.material_slots[0].material is None:
        return None
    slot = o.material_slots[0]
    src = slot.material
    if src.get('ur_mat') and src.get('ur_of') == o.name:
        mat = src
    else:
        mat = src.copy()
        mat.name = ('UR_' + src.name)[:60]
        mat['ur_mat'] = 1
        mat['ur_of'] = o.name
        mat['ur_orig_mat'] = src.name
        for _k in ('uq_mat','uq_of','uq_orig_mat','up_mat','uo_mat','un_mat'):
            if _k in mat: del mat[_k]  # del_inherited
        mat['UNVERIFIED'] = f'{tag} S-edge soft material UNVERIFIED (ur)'
        src.use_fake_user = True
        slot.material = mat
    nt = mat.node_tree
    if nt is None:
        return mat.name
    if any(n.name.startswith('UR_edge_soft') for n in nt.nodes):
        for n in nt.nodes:
            if n.name.startswith('UR_edge_soft') and 'Fac' in n.inputs:
                n.inputs['Fac'].default_value = min(0.36, max(n.inputs['Fac'].default_value, fac))
        return mat.name
    prin = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if prin is None:
        return mat.name
    mix = nt.nodes.new('ShaderNodeMixRGB')
    mix.name = 'UR_edge_soft_mix'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = fac
    mix.inputs['Color2'].default_value = (0.82, 0.80, 0.76, 1.0)  # mild dirt/warm desat
    base_in = prin.inputs.get('Base Color')
    if base_in and base_in.links:
        link = base_in.links[0]
        from_s = link.from_socket
        nt.links.remove(link)
        nt.links.new(from_s, mix.inputs['Color1'])
    else:
        c = base_in.default_value[:] if base_in else (0.55, 0.55, 0.52, 1.0)
        mix.inputs['Color1'].default_value = c
    nt.links.new(mix.outputs['Color'], prin.inputs['Base Color'])
    rough = prin.inputs.get('Roughness')
    if rough and not rough.is_linked:
        rough.default_value = min(1.0, max(rough.default_value, 0.68) + 0.05)
    return mat.name

def light_s_edge(name, y_lo, y_hi, x0, x1, rounds=6, lerp=0.48,
                 subdivide_len=0.55, bevel_off=0.018, near_r=0.60, max_sub=40):
    """Prefer xy-smooth + tiny bevel; densify only long sparse edges (capped)."""
    o = bpy.data.objects.get(name)
    if not o: return {'ops': 0}
    me = backup(o)
    n_attr = ensure_edge_attr(o, me, o.matrix_world, y_lo, y_hi, x0, x1)
    mat_n = soften_paving_mat(o, name.split('_')[0], fac=0.28)
    bm = bmesh.new(); bm.from_mesh(me)
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
    long = [e for e in focus_edges if e.is_valid and e.calc_length() > subdivide_len]
    n_sub = 0
    if long and len(long) <= max_sub:
        bmesh.ops.subdivide_edges(bm, edges=long[:max_sub], cuts=1)
        n_sub = min(len(long), max_sub)
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
    elif long:
        print('UR B skip densify', name, 'long', len(long), '> max_sub', max_sub)
    bvi = set()
    for e in focus_edges:
        bvi.update(e.verts)
    idxs = [v for v in bvi if x0 < (mw @ v.co).x < x1 and y_lo < (mw @ v.co).y < y_hi]
    near = set(idxs)
    for v in bm.verts:
        p = mw @ v.co
        if not (x0 < p.x < x1 and y_lo < p.y < y_hi): continue
        for u in idxs:
            q = mw @ u.co
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < near_r ** 2:
                near.add(v); break
    if near:
        zs = [(mw @ v.co).z for v in near]
        zmax = max(zs)
        near = {v for v in near if (mw @ v.co).z > zmax - 0.20}
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
            w = lerp if v in idxs else lerp * 0.50
            newxy[v] = (p.x * (1 - w) + ax * w, p.y * (1 - w) + ay * w, p.z)
        for v, (x, y, z) in newxy.items():
            v.co = imw @ Vector((x, y, z)); n_ops += 1
    n_bev = 0
    if focus_edges and bevel_off > 0:
        top_edges = [e for e in focus_edges if e.is_valid and all(v in near for v in e.verts)]
        if top_edges and len(top_edges) < 200:
            try:
                bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                                affect='EDGES', profile=0.5)
                n_bev = len(top_edges)
            except Exception as e:
                print('UR B bevel fail', name, e)
    bm.to_mesh(me); bm.free(); me.update()
    o['ur_touched'] = 1
    o['UNVERIFIED_ur'] = f'{name} S-edge attr+mat soft + light xy/bevel UNVERIFIED (ur); Joe lawn kept'
    print('UP B', name, 'sub', n_sub, 'ops', n_ops, 'bev', n_bev, 'attr', n_attr, 'mat', mat_n, 'verts', len(me.vertices))
    return {'sub': n_sub, 'ops': n_ops, 'bev': n_bev, 'attr': n_attr, 'mat': mat_n, 'verts': len(me.vertices)}

log['qxp_s'] = light_s_edge(
    'QXP_pedestrian_area_313024781_paving_UNVERIFIED',
    y_lo=249.0, y_hi=253.2, x0=-69.0, x1=-30.0, rounds=8, lerp=0.52,
    subdivide_len=9.0, bevel_off=0.018, max_sub=0)
log['qy_s'] = light_s_edge(
    'QY_plaza_rim_band_313024781_UNVERIFIED',
    y_lo=249.0, y_hi=253.2, x0=-69.0, x1=-30.0, rounds=6, lerp=0.48,
    subdivide_len=9.0, bevel_off=0.016, max_sub=0)
log['fp_s'] = light_s_edge(
    'Footpaths_OSM',
    y_lo=245.5, y_hi=250.8, x0=-69.0, x1=-34.0, rounds=7, lerp=0.50,
    subdivide_len=9.0, bevel_off=0.016, near_r=0.70, max_sub=0)

# ---------- C) W apron / 404 / 399 — NO densify on apron; material + mild bevel ----------
def apron_mat_soften(o):
    if o is None or not o.material_slots or o.material_slots[0].material is None:
        return None
    slot = o.material_slots[0]
    src = slot.material
    if src.get('ur_mat') and src.get('ur_of') == o.name:
        mat = src
    else:
        mat = src.copy()
        mat.name = ('UR_' + src.name)[:60]
        mat['ur_mat'] = 1
        mat['ur_of'] = o.name
        mat['ur_orig_mat'] = src.name
        for _k in ('uq_mat','uq_of','uq_orig_mat','up_mat','uo_mat','un_mat'):
            if _k in mat: del mat[_k]  # del_inherited
        mat['UNVERIFIED'] = 'apron lip dirt/edge soft UNVERIFIED (ur)'
        src.use_fake_user = True
        slot.material = mat
    nt = mat.node_tree
    if nt is None:
        return mat.name
    if any(n.name.startswith('UR_apron_dirt') for n in nt.nodes):
        return mat.name
    prin = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if prin is None:
        return mat.name
    mix = nt.nodes.new('ShaderNodeMixRGB')
    mix.name = 'UR_apron_dirt_mix'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Fac'].default_value = 0.16
    mix.inputs['Color2'].default_value = (0.78, 0.74, 0.68, 1.0)
    base_in = prin.inputs.get('Base Color')
    if base_in and base_in.links:
        link = base_in.links[0]
        from_s = link.from_socket
        nt.links.remove(link)
        nt.links.new(from_s, mix.inputs['Color1'])
    else:
        mix.inputs['Color1'].default_value = (0.55, 0.52, 0.48, 1.0)
    nt.links.new(mix.outputs['Color'], prin.inputs['Base Color'])
    rough = prin.inputs.get('Roughness')
    if rough and not rough.is_linked:
        rough.default_value = min(1.0, max(rough.default_value, 0.70) + 0.06)
    return mat.name

def soft_outline_no_densify(o, tag, rounds=5, lerp=0.38, bevel_off=0.030,
                            focus_box=(-110, -96, 243, 258), allow_sub=False, sub_len=0.50, max_sub=12):
    """xy-smooth + mild bevel; densify OFF by default (apron stay ~4929)."""
    if o is None: return {'verts': 0}
    backup(o)
    v0 = len(o.data.vertices)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    mw = o.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top_set = {v for v in bm.verts if (mw @ v.co).z > zref - 0.40}
    x0, x1, y0, y1 = focus_box
    focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
    # prefer boundary edges for bevel
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    bedges = [e for e, c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
    top_edges = bedges if bedges else [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    n_sub = 0
    if allow_sub:
        long = [e for e in top_edges if e.calc_length() > sub_len][:max_sub]
        if long:
            bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
            n_sub = len(long)
            bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
            zs = sorted((mw @ v.co).z for v in bm.verts)
            zref = zs[int(0.90 * (len(zs) - 1))]
            top_set = {v for v in bm.verts if (mw @ v.co).z > zref - 0.40}
            focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
            eu = {}
            for f in bm.faces:
                for e in f.edges:
                    eu[e] = eu.get(e, 0) + 1
            bedges = [e for e, c in eu.items() if c == 1 and e.verts[0] in focus and e.verts[1] in focus]
            top_edges = bedges if bedges else [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(rounds):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top_set]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, lerp)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    n_bev = 0
    if top_edges and bevel_off > 0 and len(top_edges) < 180:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                            affect='EDGES', profile=0.5)
            n_bev = len(top_edges)
        except Exception as e:
            print('UR bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['ur_touched'] = 1
    o['UNVERIFIED_ur_w'] = f'{tag} xy-smooth+mild bevel (no densify balloon) UNVERIFIED (ur); stair not erased'
    info = {'verts': len(o.data.vertices), 'v0': v0, 'sub': n_sub, 'bev': n_bev}
    print('UP C', tag, info)
    return info

apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
walk404 = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
walk399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
# DO NOT touch stair
log['apron_mat'] = apron_mat_soften(apron)
log['apron'] = soft_outline_no_densify(apron, 'apron', rounds=5, lerp=0.36, bevel_off=0.028,
                                       allow_sub=False)
log['w404'] = soft_outline_no_densify(walk404, 'walk404', rounds=4, lerp=0.34, bevel_off=0.022,
                                      focus_box=(-108, -97, 245, 255), allow_sub=False)
if walk399:
    log['w399'] = soft_outline_no_densify(walk399, 'walk399', rounds=3, lerp=0.32, bevel_off=0.018,
                                          focus_box=(-108, -96, 244, 256), allow_sub=False)

# Footpaths near W apron — xy only
fp = bpy.data.objects.get('Footpaths_OSM')
if fp:
    me = backup(fp); mw = fp.matrix_world; imw = mw.inverted()
    idxs = [v.index for v in me.vertices
            if -108 < (mw @ v.co).x < -96.0 and 244.5 < (mw @ v.co).y < 252.5]
    nfp = 0
    for _ in range(4):
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
            newxy[vi] = (0.62 * p.x + 0.38 * ax, 0.62 * p.y + 0.38 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nfp += 1
    me.update(); log['fp_w'] = nfp
    print('UR C Footpaths W', nfp)

# ---------- D) grass ----------
rnd = random.Random(20261106 + 7)
src = (bpy.data.objects.get('UQ_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UP_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UO_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UN_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UM_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UL_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UK_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UJ_Partridge_E_strip_grass_fill_UNVERIFIED') or
       bpy.data.objects.get('UI_Partridge_E_strip_grass_points_UNVERIFIED') or
       bpy.data.objects.get('UH_Partridge_E_seam_grass_points_UNVERIFIED'))
added = 0
if src:
    existing = []
    for gn in ('UH_Partridge_E_seam_grass_points_UNVERIFIED',
               'UI_Partridge_E_strip_grass_points_UNVERIFIED',
               'UJ_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UK_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UL_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UM_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UN_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UO_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UP_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UQ_Partridge_E_strip_grass_fill_UNVERIFIED'):
        go = bpy.data.objects.get(gn)
        if go:
            existing.extend(tuple(v.co) for v in go.data.vertices)
    ugo2 = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
    umw2 = ugo2.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    uge = ugo2.evaluated_get(dg)
    FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
    def inside(x, y):
        c = False; n = len(FP)
        for i in range(n):
            x1, y1 = FP[i]; x2, y2 = FP[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
        return c
    blk_names = [
        'QXP_pedestrian_area_313024781_paving_UNVERIFIED',
        'QY_plaza_rim_band_313024781_UNVERIFIED',
        'Footpaths_OSM',
        'TY_footway_313026406_to_Partridge_UNVERIFIED',
        'TY_footway_313026407_to_Partridge_UNVERIFIED',
        'TY_footway_313026405_to_Partridge_UNVERIFIED',
        'TY Partridge entrance steps+landings (UNVERIFIED)',
    ]
    blk = []
    for n in blk_names:
        o = bpy.data.objects.get(n)
        if o: blk.append((o.evaluated_get(dg), o.matrix_world))
    def hit_blk(x, y, z):
        for e, mw in blk:
            iw = mw.inverted()
            o0 = iw @ Vector((x, y, z + 40)); o1 = iw @ Vector((x, y, z - 0.05)); d = o1 - o0
            if d.length < 1e-6: continue
            if e.ray_cast(o0, d.normalized(), distance=d.length)[0]:
                return True
        return False
    pts = list(existing)
    new_pts = []
    for _ in range(2000):
        if rnd.random() < 0.58:
            x = -62.0 + rnd.random() * 18.0
            y = 247.6 + rnd.random() * 3.0
        else:
            x = XA + rnd.random() * (XB - XA)
            y = Y_WALK + 0.25 + rnd.random() * (Y_PLAZA - Y_WALK - 0.4)
        if inside(x, y): continue
        if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < 0.28 ** 2 for p in pts[::max(1, len(pts)//90)] + pts[-160:]):
            continue
        r = uge.ray_cast(ugo2.matrix_world.inverted() @ Vector((x, y, 400)),
                         (ugo2.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
        if not r[0]: continue
        z = (umw2 @ r[1]).z
        if hit_blk(x, y, z): continue
        new_pts.append((x, y, z - 0.004)); pts.append(new_pts[-1]); added += 1
        if added >= 400: break
    if added:
        col = bpy.data.collections.get(COLN) or bpy.data.collections.new(COLN)
        if COLN not in [c.name for c in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(col)
        me_g = bpy.data.meshes.new('UR_Partridge_E_strip_grass_fill_UNVERIFIED')
        me_g.from_pydata(new_pts, [], [])
        ob_g = src.copy(); ob_g.data = me_g
        ob_g.name = 'UR_Partridge_E_strip_grass_fill_UNVERIFIED'
        ob_g.matrix_world = Matrix.Identity(4)
        for c in list(ob_g.users_collection): c.objects.unlink(ob_g)
        col.objects.link(ob_g)
        ob_g['ur_obj'] = 1
        ob_g['UNVERIFIED'] = 'cx_grass fill on bald Partridge E strip patches; density UNVERIFIED (ur)'
        if 'cx_grass' not in ob_g.modifiers:
            m = ob_g.modifiers.new('cx_grass', 'NODES')
            m.node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
        else:
            ob_g.modifiers['cx_grass'].node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
log['grass_added'] = added
print('UR D grass added', added)

# ---------- E) optional Normal Ave soft-end material polish (material only) ----------
def bump_uf_softfade():
    mat = bpy.data.materials.get('UF_asphalt_softfade_UNVERIFIED')
    if mat is None or mat.node_tree is None:
        return 'miss'
    nt = mat.node_tree
    # bump any Mix / Math Fac that looks like a softfade gate
    n_bumped = 0
    for n in nt.nodes:
        if n.type == 'MATH' and n.operation == 'MULTIPLY':
            for inp in n.inputs:
                if not inp.is_linked and hasattr(inp, 'default_value') and 0.05 < inp.default_value < 0.95:
                    inp.default_value = min(0.95, inp.default_value + 0.04)
                    n_bumped += 1
        if n.type == 'MIX_RGB' or n.type == 'MIX':
            if 'Fac' in n.inputs and not n.inputs['Fac'].is_linked:
                fv = n.inputs['Fac'].default_value
                if 0.05 < fv < 0.9:
                    n.inputs['Fac'].default_value = min(0.85, fv + 0.03)
                    n_bumped += 1
    # mark as touched via a custom prop on material (no ur_mat — don't delete on revert)
    mat['ur_softfade_bump'] = 1
    mat['UNVERIFIED_ur'] = 'UF softfade Fac mild bump UNVERIFIED (ur); material only'
    return f'bumped_{n_bumped}'
log['uf_softfade'] = bump_uf_softfade()
print('UR E uf_softfade', log['uf_softfade'])

# ---------- cams ----------
col = bpy.data.collections.get(COLN)
if col is None:
    col = bpy.data.collections.new(COLN)
    bpy.context.scene.collection.children.link(col)

def cam(name, loc, tgt, lens):
    if name in bpy.data.objects:
        o = bpy.data.objects[name]
        o.location = loc
        o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        o['ur_obj'] = 1
        return
    # try copy transforms from UN_CAM equivalent
    un_name = name.replace('UR_CAM_', 'UQ_CAM_')
    un = bpy.data.objects.get(un_name)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['ur_obj'] = 1
    if un:
        o.location = un.location.copy()
        o.rotation_euler = un.rotation_euler.copy()
        if un.data:
            cd.lens = un.data.lens
    else:
        o.location = loc
        o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

cam('UR_CAM_oblique_Partridge_E_lawn_from_SE', (-16, 196, 177), (-55, 250, 140), 35)
cam('UR_CAM_eye_Partridge_E_face_from_E', (-45, 251.8, 141.6), (-68, 253.0, 141.0), 28)
cam('UR_CAM_eye_Partridge_W_steps_from_W', (-117, 246.2, 141.1), (-99, 250.5, 139.6), 30)
cam('UR_CAM_closeup_Partridge_E_S_edge', (-48, 245.2, 141.5), (-54, 249.8, 139.85), 32)

json.dump(log, open(D + 'data/ur/ur_main.json', 'w'), indent=1)
print('UR LOG', log)
print('UR objects', len(bpy.data.objects))
if apron:
    print('UR apron verts final', len(apron.data.vertices))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
