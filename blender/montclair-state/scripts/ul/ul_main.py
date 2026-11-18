"""Session ul (Nov 5 2026 ~9:20–~10:12 PM ET, MAIN, day-9 leftovers): Partridge polish after uk.
Joe lawn strip (ui) stays — do not reverse.
A) Probe UG↔SA join; material/shader soften + very light z re-feather (no large boundary push unless gap).
B) Densify + stronger QXP / Footpaths_OSM / QY S-edge xy-smooth / light bevel (south only; plaza N kept).
C) Densify + xy-smooth + light bevel on W apron / 404 / 399 (DO NOT touch stair mesh).
D) Optional modest grass on bald strip patches (UL_* additive).
Cams: UL_CAM_*.
REVERT=1 restores UL_bak_* meshes and deletes ul_obj objects.
"""
import bpy, bmesh, os, json, math, random
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'; SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UL_Partridge_leftover_polish_UNVERIFIED'
XA, XB = -67.5, -35.5
Y_WALK, Y_PLAZA = 247.0, 251.2

def revert():
    for me in [m for m in bpy.data.meshes if m.get('ul_bak_of')]:
        on = me['ul_bak_of']; o = bpy.data.objects.get(on)
        if o:
            mod = o.data; o.data = me
            if mod.users == 0: bpy.data.meshes.remove(mod)
        nm = me['ul_orig_name']; del me['ul_bak_of']; del me['ul_orig_name']
        me.use_fake_user = False; me.name = nm
    for o in [o for o in list(bpy.data.objects) if o.get('ul_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            (bpy.data.meshes if t == 'MESH' else bpy.data.cameras).remove(me)
    # restore original materials on objects that got UL copies, then remove UL mats
    for m in [m for m in list(bpy.data.materials) if m.get('ul_mat')]:
        on = m.get('ul_of'); orig_n = m.get('ul_orig_mat')
        o = bpy.data.objects.get(on) if on else None
        orig = bpy.data.materials.get(orig_n) if orig_n else None
        if o and orig:
            for slot in o.material_slots:
                if slot.material == m:
                    slot.material = orig
        bpy.data.materials.remove(m)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    print('UL REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def backup(o):
    if any(m.get('ul_bak_of') == o.name for m in bpy.data.meshes):
        return o.data
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UL_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ul_bak_of'] = o.name; orig['ul_orig_name'] = nm
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

log = {'session': 'ul', 'joe_lawn_strip': 'kept (do not reverse)'}

# ---------- A) PROBE UG↔SA join first ----------
probe = {'both': 0, 'ug_only': 0, 'sa_only': 0, 'gap_xy': 0, 'dz_samples': [], 'ug_ymax': None, 'sa_ymin': None}
xs = [XA + i * (XB - XA) / 24.0 for i in range(25)]
ys = [249.4 + i * 0.08 for i in range(40)]  # 249.4 → 252.52
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
# sample max UG y / min SA y along strip midlines
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
    gap = probe['sa_ymin'] - probe['ug_ymax']
    probe['gap_xy'] = gap
probe['dz_p95'] = sorted(probe['dz_samples'])[int(0.95 * (len(probe['dz_samples']) - 1))] if probe['dz_samples'] else None
probe['dz_max'] = max(probe['dz_samples']) if probe['dz_samples'] else None
probe['dz_mean'] = (sum(probe['dz_samples']) / len(probe['dz_samples'])) if probe['dz_samples'] else None
# drop huge sample list from log
probe_slim = {k: v for k, v in probe.items() if k != 'dz_samples'}
probe_slim['n_dz'] = len(probe['dz_samples'])
log['probe'] = probe_slim
json.dump(probe_slim, open(D + 'data/ul/crease_probe.json', 'w'), indent=1)
print('UL A probe', probe_slim)

# Prefer material/shader soften; only light z re-feather (no large boundary push unless gap > 0.08 m)
do_boundary_push = (probe.get('gap_xy') or 0) > 0.08
log['boundary_push'] = bool(do_boundary_push)

ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
ume = backup(ugo); umw = ugo.matrix_world; uimw = umw.inverted()
sme = backup(sao); smw = sao.matrix_world; simw = smw.inverted()

if do_boundary_push:
    # rare path — only if probe shows a real gap again
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
    print('UL A boundary push UG', n_push, 'SA', n_spush)
else:
    log['ug_n_push'] = 0; log['sa_s_push'] = 0
    print('UL A no boundary push (gap ok)')

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
    # gentler than uj polish — half strength
    target = p.z * (1 - 0.55 * t) + (saz + 0.0015) * (0.55 * t)
    if abs(target - p.z) > 0.0008:
        p.z = target; v.co = uimw @ p; n_ug += 1
ume.update(); log['ug_refeather'] = n_ug
print('UL A ug refeather', n_ug)

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
    target = p.z * (1 - 0.50 * t) + (ugz - 0.002) * (0.50 * t)
    if abs(target - p.z) > 0.0008:
        p.z = target; v.co = simw @ p; n_sa += 1
sme.update(); log['sa_refeather'] = n_sa
print('UL A sa refeather', n_sa)

# material/shader soften on overlap: write ul_join_soft vertex color / attribute + mild Principled mix
def ensure_join_attr(o, me, mw, y_lo, y_hi, x0, x1, attr_name='ul_join_soft'):
    # attribute 0..1 peaking at mid of band
    if attr_name not in me.attributes:
        me.attributes.new(attr_name, 'FLOAT', 'POINT')
    attr = me.attributes[attr_name]
    n = 0
    mid = 0.5 * (y_lo + y_hi)
    half = max(0.15, 0.5 * (y_hi - y_lo))
    for i, v in enumerate(me.vertices):
        p = mw @ v.co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            w = 1.0 - abs(p.y - mid) / half
            w = max(0.0, min(1.0, w))
            attr.data[i].value = w; n += 1
        else:
            attr.data[i].value = 0.0
    return n

n_ug_attr = ensure_join_attr(ugo, ume, umw, 249.8, 251.4, XA - 1.0, XB + 1.0)
n_sa_attr = ensure_join_attr(sao, sme, smw, 249.8, 251.6, XA - 1.0, XB + 1.0)
log['ug_join_attr'] = n_ug_attr; log['sa_join_attr'] = n_sa_attr
print('UL A join attr UG', n_ug_attr, 'SA', n_sa_attr)

def soften_lawn_mat(o, tag):
    """Duplicate first material slot; darken albedo slightly via multiply so join reads softer (UNVERIFIED)."""
    if not o.material_slots:
        return None
    slot = o.material_slots[0]
    if slot.material is None:
        return None
    src = slot.material
    # already ul copy?
    if src.get('ul_mat') and src.get('ul_of') == o.name:
        mat = src
    else:
        mat = src.copy()
        mat.name = ('UL_' + src.name)[:60]
        mat['ul_mat'] = 1
        mat['ul_of'] = o.name
        mat['ul_orig_mat'] = src.name
        mat['UNVERIFIED'] = f'{tag} join soft material UNVERIFIED (ul)'
        slot.material = mat
    nt = mat.node_tree
    if nt is None:
        return mat.name
    # find Principled BSDF
    prin = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if prin is None:
        return mat.name
    # if we already added a UL soft multiply, skip
    if any(n.name.startswith('UL_join_soft') for n in nt.nodes):
        return mat.name
    # Insert a mild darken/desat on Base Color via MixRGB
    mix = nt.nodes.new('ShaderNodeMixRGB')
    mix.name = 'UL_join_soft_mix'
    mix.blend_type = 'MIX'
    mix.inputs['Fac'].default_value = 0.22  # subtle residual join soft
    mix.inputs['Color2'].default_value = (0.22, 0.28, 0.16, 1.0)  # soft mid grass
    # reconnect whatever fed Base Color
    base_in = prin.inputs.get('Base Color')
    if base_in and base_in.links:
        link = base_in.links[0]
        from_s = link.from_socket
        nt.links.remove(link)
        nt.links.new(from_s, mix.inputs['Color1'])
    else:
        # use default greenish
        mix.inputs['Color1'].default_value = (0.30, 0.38, 0.18, 1.0)
    nt.links.new(mix.outputs['Color'], prin.inputs['Base Color'])
    # slightly raise roughness to kill hard shadow edge
    rough = prin.inputs.get('Roughness')
    if rough and not rough.is_linked:
        rough.default_value = min(1.0, max(rough.default_value, 0.72) + 0.06)
    return mat.name

log['ug_mat'] = soften_lawn_mat(ugo, 'UG')
log['sa_mat'] = soften_lawn_mat(sao, 'SA')
print('UL A mats', log['ug_mat'], log['sa_mat'])

# ---------- B) QXP / QY / Footpaths S-edge: densify + stronger xy-smooth + light bevel ----------
def densify_and_smooth_s_edge(name, y_lo, y_hi, x0, x1, rounds=10, lerp=0.62,
                               subdivide_len=0.38, bevel_off=0.028, near_r=0.70):
    o = bpy.data.objects.get(name)
    if not o: return {'ops': 0}
    me = backup(o)
    bm = bmesh.new(); bm.from_mesh(me)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    mw = o.matrix_world; imw = mw.inverted()
    # boundary edges
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    bedges = [e for e, c in eu.items() if c == 1]
    # south-band boundary edges (prefer lower-y / strip-facing)
    focus_edges = []
    for e in bedges:
        for v in e.verts:
            p = mw @ v.co
            if x0 < p.x < x1 and y_lo < p.y < y_hi:
                focus_edges.append(e); break
    # densify long focus edges
    long = [e for e in focus_edges if e.is_valid and e.calc_length() > subdivide_len]
    n_sub = 0
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        n_sub = len(long)
        bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        # rebuild focus after subdivide
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
    # collect top-band verts near S boundary
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
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < near_r ** 2:
                near.add(v); break
    if near:
        zs = [(mw @ v.co).z for v in near]
        zmax = max(zs)
        near = {v for v in near if (mw @ v.co).z > zmax - 0.20}
        idxs = [v for v in idxs if v in near]
    # xy laplace
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
    # light bevel on focus top edges only (south)
    n_bev = 0
    if focus_edges and bevel_off > 0:
        # refresh focus edges validity
        top_edges = [e for e in focus_edges if e.is_valid and all(v in near for v in e.verts)]
        if top_edges:
            try:
                bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                                affect='EDGES', profile=0.5)
                n_bev = len(top_edges)
            except Exception as e:
                print('UL B bevel fail', name, e)
    bm.to_mesh(me); bm.free(); me.update()
    o['ul_touched'] = 1
    o['UNVERIFIED_ul'] = f'{name} S-edge densify+xy-smooth+bevel UNVERIFIED (ul); Joe lawn strip kept'
    print('UL B', name, 'sub', n_sub, 'ops', n_ops, 'bev', n_bev, 'near', len(near))
    return {'sub': n_sub, 'ops': n_ops, 'bev': n_bev, 'near': len(near)}

log['qxp_s'] = densify_and_smooth_s_edge(
    'QXP_pedestrian_area_313024781_paving_UNVERIFIED',
    y_lo=249.0, y_hi=253.2, x0=-69.0, x1=-30.0, rounds=12, lerp=0.66,
    subdivide_len=0.32, bevel_off=0.032)
log['qy_s'] = densify_and_smooth_s_edge(
    'QY_plaza_rim_band_313024781_UNVERIFIED',
    y_lo=249.0, y_hi=253.2, x0=-69.0, x1=-30.0, rounds=10, lerp=0.60,
    subdivide_len=0.36, bevel_off=0.028)
log['fp_s'] = densify_and_smooth_s_edge(
    'Footpaths_OSM',
    y_lo=245.5, y_hi=250.8, x0=-69.0, x1=-34.0, rounds=10, lerp=0.60,
    subdivide_len=0.38, bevel_off=0.024, near_r=0.78)

# ---------- C) W apron / 404 / 399 densify + xy-smooth + light bevel; stair untouched ----------
def soften_outline(o, tag, rounds=5, lerp=0.42, bevel_off=0.055, subdivide_len=0.42,
                   focus_box=(-110, -96, 243, 258)):
    if o is None: return 0
    backup(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    mw = o.matrix_world
    wz = [(v, (mw @ v.co).z) for v in bm.verts]
    zmax = max(z for _, z in wz)
    top_set = {v for v, z in wz if z > zmax - 0.12}
    x0, x1, y0, y1 = focus_box
    focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
    top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    long = [e for e in top_edges if e.calc_length() > subdivide_len]
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        wz = [(v, (mw @ v.co).z) for v in bm.verts]
        zmax = max(z for _, z in wz)
        top_set = {v for v, z in wz if z > zmax - 0.12}
        focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    # second densify pass for still-long edges
    long2 = [e for e in top_edges if e.calc_length() > subdivide_len * 0.85]
    if long2:
        bmesh.ops.subdivide_edges(bm, edges=long2, cuts=1)
        bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        wz = [(v, (mw @ v.co).z) for v in bm.verts]
        zmax = max(z for _, z in wz)
        top_set = {v for v, z in wz if z > zmax - 0.12}
        focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
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
    if top_edges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                            affect='EDGES', profile=0.5)
        except Exception as e:
            print('UL bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['ul_touched'] = 1
    o['UNVERIFIED_ul_w'] = f'{tag} densify+xy-smooth+bevel UNVERIFIED (ul); stair not erased'
    print('UL C', tag, 'verts', len(o.data.vertices))
    return len(o.data.vertices)

apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
walk404 = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
walk399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
# DO NOT touch 'TY Partridge entrance steps+landings (UNVERIFIED)'
log['apron_v'] = soften_outline(apron, 'apron', rounds=7, lerp=0.48, bevel_off=0.065, subdivide_len=0.22)
log['w404_v'] = soften_outline(walk404, 'walk404', rounds=6, lerp=0.42, bevel_off=0.044, subdivide_len=0.32)
if walk399:
    log['w399_v'] = soften_outline(walk399, 'walk399', rounds=5, lerp=0.38, bevel_off=0.034, subdivide_len=0.36)

# Footpaths near W apron / stair foot
fp = bpy.data.objects.get('Footpaths_OSM')
if fp:
    me = backup(fp); mw = fp.matrix_world; imw = mw.inverted()
    idxs = [v.index for v in me.vertices
            if -108 < (mw @ v.co).x < -96.0 and 244.5 < (mw @ v.co).y < 252.5]
    nfp = 0
    for _ in range(5):
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
            newxy[vi] = (0.58 * p.x + 0.42 * ax, 0.58 * p.y + 0.42 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nfp += 1
    me.update(); log['fp_w'] = nfp
    print('UL C Footpaths W', nfp)

# ---------- D) optional modest grass densify ----------
rnd = random.Random(20261105 + 21)
src = bpy.data.objects.get('UK_Partridge_E_strip_grass_fill_UNVERIFIED') or \
      bpy.data.objects.get('UJ_Partridge_E_strip_grass_fill_UNVERIFIED') or \
      bpy.data.objects.get('UI_Partridge_E_strip_grass_points_UNVERIFIED') or \
      bpy.data.objects.get('UH_Partridge_E_seam_grass_points_UNVERIFIED')
added = 0
if src:
    # gather existing points from all strip grass objs
    existing = []
    for gn in ('UH_Partridge_E_seam_grass_points_UNVERIFIED',
               'UI_Partridge_E_strip_grass_points_UNVERIFIED',
               'UJ_Partridge_E_strip_grass_fill_UNVERIFIED',
               'UK_Partridge_E_strip_grass_fill_UNVERIFIED'):
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
    for _ in range(1600):
        if rnd.random() < 0.60:
            x = -62.0 + rnd.random() * 18.0
            y = 247.6 + rnd.random() * 3.0
        else:
            x = XA + rnd.random() * (XB - XA)
            y = Y_WALK + 0.25 + rnd.random() * (Y_PLAZA - Y_WALK - 0.4)
        if inside(x, y): continue
        if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < 0.30 ** 2 for p in pts[::max(1, len(pts)//90)] + pts[-140:]):
            continue
        r = uge.ray_cast(ugo2.matrix_world.inverted() @ Vector((x, y, 400)),
                         (ugo2.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
        if not r[0]: continue
        z = (umw2 @ r[1]).z
        if hit_blk(x, y, z): continue
        new_pts.append((x, y, z - 0.004)); pts.append(new_pts[-1]); added += 1
        if added >= 240: break
    if added:
        col = bpy.data.collections.get(COLN) or bpy.data.collections.new(COLN)
        if COLN not in [c.name for c in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(col)
        me_g = bpy.data.meshes.new('UL_Partridge_E_strip_grass_fill_UNVERIFIED')
        me_g.from_pydata(new_pts, [], [])
        ob_g = src.copy(); ob_g.data = me_g
        ob_g.name = 'UL_Partridge_E_strip_grass_fill_UNVERIFIED'
        ob_g.matrix_world = Matrix.Identity(4)
        for c in list(ob_g.users_collection): c.objects.unlink(ob_g)
        col.objects.link(ob_g)
        ob_g['ul_obj'] = 1
        ob_g['UNVERIFIED'] = 'cx_grass fill on bald Partridge E strip patches; density UNVERIFIED (ul)'
        if 'cx_grass' not in ob_g.modifiers:
            m = ob_g.modifiers.new('cx_grass', 'NODES')
            m.node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
        else:
            ob_g.modifiers['cx_grass'].node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
log['grass_added'] = added
print('UL D grass added', added)

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
        o['ul_obj'] = 1
        return
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['ul_obj'] = 1
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

cam('UL_CAM_oblique_Partridge_E_lawn_from_SE', (-16, 196, 177), (-55, 250, 140), 35)
cam('UL_CAM_eye_Partridge_E_face_from_E', (-45, 251.8, 141.6), (-68, 253.0, 141.0), 28)
cam('UL_CAM_eye_Partridge_W_steps_from_W', (-117, 246.2, 141.1), (-99, 250.5, 139.6), 30)
# close-up of worst leftover: S-edge of plaza/lawn join
cam('UL_CAM_closeup_Partridge_E_S_edge', (-48, 245.2, 141.5), (-54, 249.8, 139.85), 32)

json.dump(log, open(D + 'data/ul/ul_main.json', 'w'), indent=1)
print('UL LOG', log)
print('UL objects', len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
