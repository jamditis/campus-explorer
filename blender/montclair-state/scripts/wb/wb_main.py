# wb (Nov 7 2026, MAIN, day 11): Bohn NORTH-wing / mid-step W elevation eggcrate re-laid on ONE shared
# 8-bay pier grid (t-grid) for base (TK), L1 (2 faces), L2, L3 so pier lines run continuously from the roof
# down to grade (same method as wa on the south wing). Mid-step count stays 8 UNVERIFIED (wa: AMBIGUOUS).
# Grid span = common L2/L3 extent; base/L1 (which stop ~10 m short of the north end) get the same pier
# lines; their south pier is clipped to the face start; their north partial bay (~1.2-1.5 m) is a solid
# end panel framed by a corner pier (UNVERIFIED decision). L2 bays over TP_Bohn_shaft_9 start above its
# coping (clash clip, residual #2). Reuses vw materials (proud eggcrate + opaque-reflective glass).
# REVERT_EXACT: scripts/wb/wb_revert_all.sh.
import bpy, bmesh, os, json, math
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
ROOT = '/workspace/nj-scenes/montclair-state'; OUT = ROOT + '/data/wb'
CN = 'WB_Bohn_north_wing_W_grid_UNVERIFIED'
NOTE = ('wb: Bohn north-wing/mid-step W eggcrate re-laid on one shared 8-bay pier grid (base/L1/L2/L3); '
        'count 8 kept from vw (AMBIGUOUS vs slides 1251/1519); end panels/pier/window widths UNVERIFIED; opaque-reflective glass')
PIER_W = 0.48; BAND_H = 0.42; DEPTH = 0.40; GLASS_T = 0.04; GLASS_OFF = 0.015
FLOOR = 2.75; MARGIN_Z = 0.12; MARGIN_T = 0.10; NBAYS = 8
log = {'session': 'wb'}
assert not bpy.data.collections.get(CN), 'wb already applied'

targets = []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render: continue
    if not (o.name.startswith('TL_Bohn_Hall_') or o.name == 'TK_Bohn_Hall_232853538_base_UNVERIFIED'): continue
    if 'PH' in o.name: continue
    me = o.data; mw = o.matrix_world
    for pi, p in enumerate(me.polygons):
        n = (mw.to_3x3() @ p.normal).normalized()
        if abs(n.z) > 0.5 or n.x > -0.90: continue
        verts = [mw @ me.vertices[i].co for i in p.vertices]
        zs = [v.z for v in verts]
        if max(zs) - min(zs) < 2.0: continue
        cx = sum(v.x for v in verts) / len(verts); cy = sum(v.y for v in verts) / len(verts)
        if not (225.5 < cx < 236.5 and 383 < cy < 400): continue
        w = math.hypot(max(v.x for v in verts) - min(v.x for v in verts), max(v.y for v in verts) - min(v.y for v in verts))
        if w < 5.5: continue
        N = Vector((n.x, n.y, 0)).normalized(); U = Vector((-N.y, N.x, 0)).normalized()
        if U.y < 0: U = -U
        targets.append(dict(mesh=o.name, pi=pi, U=U, N=N, Nf=N.copy(), verts=[Vector((v.x, v.y, 0)) for v in verts],
                            z0=min(zs), z1=max(zs), w=w))
for t in targets: print('WB tgt', t['mesh'][:18], t['pi'], round(t['w'], 2), round(t['z0'], 1))
L2t = [t for t in targets if t['mesh'].startswith('TL_Bohn_Hall_L2')][0]
U = L2t['U']; N = L2t['N']
O = sum((v for t in targets for v in t['verts']), Vector()) / sum(len(t['verts']) for t in targets)
for t in targets:
    ts = [(v - O).dot(U) for v in t['verts']]
    t['t0'], t['t1'] = min(ts), max(ts); t['c'] = sum(t['verts'], Vector()) / len(t['verts']); del t['verts']
levels = {}
for t in targets:
    k = (t['mesh'], round(t['z0'], 1))
    L = levels.setdefault(k, dict(mesh=t['mesh'], z0=t['z0'], z1=t['z1'], t0=t['t0'], t1=t['t1'], faces=[]))
    L['t0'] = min(L['t0'], t['t0']); L['t1'] = max(L['t1'], t['t1']); L['faces'].append(t)
assert len(levels) == 4, [(k, len(v['faces'])) for k, v in levels.items()]
def nw_at(L, tc):
    fs = sorted(L['faces'], key=lambda f: 0 if f['t0'] - 0.3 <= tc <= f['t1'] + 0.3 else min(abs(tc - f['t0']), abs(tc - f['t1'])))
    f = fs[0]; p = O + U * tc
    return (f['c'] - p).dot(f['Nf']) / N.dot(f['Nf'])
def tnz(p): q = Vector((p.x, p.y, 0)) - O; return (q.dot(U), q.dot(N), p.z)
for L in levels.values(): L['nw'] = nw_at(L, (L['t0'] + L['t1']) / 2)
log['origin'] = [round(O.x, 3), round(O.y, 3)]; log['U'] = [round(U.x, 4), round(U.y, 4)]
log['levels'] = [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in L.items() if k != 'faces'} | {'nfaces': len(L['faces'])} for L in levels.values()]
print('WB levels', log['levels'])
upper = [L for L in levels.values() if L['mesh'].startswith(('TL_Bohn_Hall_L2', 'TL_Bohn_Hall_L3'))]
c0 = max(L['t0'] for L in upper) + MARGIN_T + PIER_W / 2
cN = min(L['t1'] for L in upper) - MARGIN_T - PIER_W / 2
bay = (cN - c0) / NBAYS
piers = [c0 + i * bay for i in range(NBAYS + 1)]
log['pier_centres_t'] = [round(p, 3) for p in piers]; log['bay_m_UNVERIFIED'] = round(bay, 3)
# shaft_9 footprint in frame (clash clip)
sh = bpy.data.objects['TP_Bohn_shaft_9_L1_UNVERIFIED']
sv = [tnz(sh.matrix_world @ v.co) for v in sh.data.vertices]
S9 = dict(t0=min(a[0] for a in sv), t1=max(a[0] for a in sv), n0=min(a[1] for a in sv), n1=max(a[1] for a in sv), ztop=max(a[2] for a in sv))
cop = bpy.data.objects.get('TP_Bohn_shaft_9_L1_coping_UNVERIFIED')
if cop: S9['ztop'] = max(S9['ztop'], max((cop.matrix_world @ v.co).z for v in cop.data.vertices))
log['shaft9'] = {k: round(v, 3) for k, v in S9.items()}
print('WB piers', log['pier_centres_t'], 'bay', bay, 'shaft9', log['shaft9'])

# ---- strip vw boxes on these 4 levels
removed = {}
for vn in ('VW_Bohn_W_piers_bands_UNVERIFIED', 'VW_Bohn_W_reveals_UNVERIFIED', 'VW_Bohn_W_glass_UNVERIFIED'):
    o = bpy.data.objects[vn]; mw = o.matrix_world
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    seen = set(); kill = []
    for v in bm.verts:
        if v.index in seen: continue
        isl = []; st = [v]; seen.add(v.index)
        while st:
            a = st.pop(); isl.append(a)
            for e in a.link_edges:
                b = e.other_vert(a)
                if b.index not in seen: seen.add(b.index); st.append(b)
        c = sum((mw @ a.co for a in isl), Vector()) / len(isl)
        tt, nn, zz = tnz(c)
        for L in levels.values():
            if (L['z0'] - 0.05 < zz < L['z1'] + 0.05 and L['t0'] - 0.6 < tt < L['t1'] + 0.6
                    and -0.25 < nn - nw_at(L, tt) < 0.65):
                kill.extend(isl); break
    removed[vn] = len(set(kill)) // 8
    bmesh.ops.delete(bm, geom=list(set(kill)), context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
log['removed_vw_boxes'] = removed
print('WB removed', removed)

M_CONC = bpy.data.materials['VW_Bohn_W_concrete_UNVERIFIED']
M_GLASS = bpy.data.materials['VW_Bohn_W_glass_opaque_reflective_UNVERIFIED']
M_REVEAL = bpy.data.materials['VW_Bohn_W_reveal_UNVERIFIED']
col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col); col['wb_obj'] = 1
class MB:
    def __init__(s, name, mats): s.bm = bmesh.new(); s.name = name; s.mats = mats; s.n = 0
    def box(s, ta, tb, L, d0, d1, z0, z1):
        if tb - ta < 0.02 or z1 - z0 < 0.02: return
        nw = nw_at(L, (ta + tb) / 2); cs = []
        for z in (z0, z1):
            for tt, dd in ((ta, d0), (tb, d0), (tb, d1), (ta, d1)):
                p = O + U * tt + N * (nw + dd); cs.append(s.bm.verts.new((p.x, p.y, z)))
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            s.bm.faces.new([cs[i] for i in f])
        s.n += 1
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        for p in me.polygons: p.use_smooth = False
        o = bpy.data.objects.new(s.name, me); col.objects.link(o); o['wb_obj'] = 1; o['UNVERIFIED'] = NOTE
        return o
mp = MB('WB_Bohn_N_wing_W_piers_bands_UNVERIFIED', [M_CONC])
mr = MB('WB_Bohn_N_wing_W_reveals_UNVERIFIED', [M_REVEAL])
mg = MB('WB_Bohn_N_wing_W_glass_UNVERIFIED', [M_GLASS])
lower = [L for L in levels.values() if L not in upper]
T_CORNER = min(L['t1'] for L in lower) - MARGIN_T - PIER_W / 2
log['T_CORNER_UNVERIFIED'] = round(T_CORNER, 3)
cells = 0; per_level = {}; end_panels = []; clipped = 0
def over_s9(ta, tb, L):
    return ta < S9['t1'] and tb > S9['t0'] and S9['n0'] - 0.5 < nw_at(L, (ta + tb) / 2) < S9['n1'] + 0.5
for L in sorted(levels.values(), key=lambda L: L['z0']):
    lo = L['t0'] + 0.0; hi = L['t1'] - 0.0
    z_lo = L['z0'] + MARGIN_Z; z_hi = L['z1'] - MARGIN_Z
    ns = max(1, int(round((z_hi - z_lo) / FLOOR))); shh = (z_hi - z_lo) / ns
    lc = 0
    # piers on the shared grid, clipped to this face's extent
    used = []
    for pc in piers:
        a, b = max(pc - PIER_W / 2, lo), min(pc + PIER_W / 2, hi)
        if b - a < 0.10: continue
        zl = z_lo
        if over_s9(a, b, L) and zl < S9['ztop']: zl = S9['ztop'] + 0.01; clipped += 1
        mp.box(a, b, L, -0.03, DEPTH, zl, z_hi); used.append(pc)
    # north partial bay on the short lower faces (base/L1) -> solid end panel framed by ONE corner pier
    # line shared by base and L1 (at the shorter L1 end), UNVERIFIED decision
    last = used[-1]
    if hi - (last + PIER_W / 2) > 0.9:
        cp = T_CORNER
        mp.box(cp - PIER_W / 2, cp + PIER_W / 2, L, -0.03, DEPTH, z_lo, z_hi)
        end_panels.append(dict(level=L['mesh'][:16], t_from=round(last + PIER_W / 2, 2), t_to=round(cp - PIER_W / 2, 2)))
    for i in range(NBAYS):
        pa, pb = piers[i], piers[i + 1]
        if pa not in used or pb not in used: continue
        ta, tb = pa + PIER_W / 2, pb - PIER_W / 2
        clip = over_s9(ta, tb, L)
        for s_i in range(ns + 1):
            if s_i == 0: z0b, z1b = z_lo, z_lo + BAND_H
            elif s_i == ns: z0b, z1b = z_hi - BAND_H, z_hi
            else: zc = z_lo + s_i * shh; z0b, z1b = zc - BAND_H / 2, zc + BAND_H / 2
            if clip and z1b < S9['ztop'] + 0.05: clipped += 1; continue
            mp.box(ta - 0.02, tb + 0.02, L, -0.03, DEPTH, max(z0b, S9['ztop'] + 0.01) if clip else z0b, z1b)
        for s_i in range(ns):
            z0w = z_lo + s_i * shh + BAND_H + 0.03; z1w = z_lo + (s_i + 1) * shh - BAND_H - 0.03
            if z1w - z0w < 0.75: continue
            if clip and z0w < S9['ztop'] + 0.2: clipped += 1; continue
            mr.box(ta + 0.005, tb - 0.005, L, GLASS_OFF, DEPTH - 0.01, z0w - 0.02, z1w + 0.02)
            mg.box(ta + 0.03, tb - 0.03, L, GLASS_OFF, GLASS_OFF + GLASS_T, z0w, z1w)
            cells += 1; lc += 1
    # bands across the end panel (solid wall panel reads as continuous floor bands)
    if end_panels and end_panels[-1]['level'] == L['mesh'][:16] and len(end_panels) and end_panels[-1].get('z') is None:
        ep = end_panels[-1]; ep['z'] = [round(L['z0'], 2), round(L['z1'], 2)]
        for s_i in range(ns + 1):
            if s_i == 0: z0b, z1b = z_lo, z_lo + BAND_H
            elif s_i == ns: z0b, z1b = z_hi - BAND_H, z_hi
            else: zc = z_lo + s_i * shh; z0b, z1b = zc - BAND_H / 2, zc + BAND_H / 2
            mp.box(last + PIER_W / 2 - 0.02, cp - PIER_W / 2 + 0.02, L, -0.03, DEPTH, z0b, z1b)
    per_level[L['mesh'][:18] + '@' + str(round(L['z0'], 1))] = dict(cells=lc, storeys=ns, piers=len(used), t=[round(lo, 2), round(hi, 2)])
o1 = mp.done(); o2 = mr.done(); o3 = mg.done()
log['cells'] = cells; log['per_level'] = per_level; log['end_panels_UNVERIFIED'] = end_panels; log['shaft9_clip_skips'] = clipped

def cam(name, t, n, z, tt, tn, tz, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 30000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['wb_obj'] = 1
    p = O + U * t + N * n; q = O + U * tt + N * tn
    o.location = (p.x, p.y, z); d = Vector((q.x - p.x, q.y - p.y, tz - z))
    o.rotation_euler = (math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0, math.atan2(d.y, d.x) - math.pi / 2)
    return o
def gz(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    for gn in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
        go = bpy.data.objects.get(gn)
        if not go: continue
        e = go.evaluated_get(dg); iw = go.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]: return (go.matrix_world @ r[1]).z
    return 130.0
tm = (piers[0] + piers[-1]) / 2
CC = os.environ.get('CLOSE', '12,15,140,0,0,138')
v = [float(a) for a in CC.split(',')]
cam('WB_CAM_closeup_Bohn_N_wing_W_piers', tm + v[0], v[1], v[2], tm + v[3], v[4], v[5], 28)
EC = os.environ.get('EYE', '20,32,6,0,14')  # dt, n, tt, tn, tz-above-ground
e = [float(a) for a in EC.split(',')]
pe = O + U * (tm + e[0]) + N * e[1]; ge = gz(pe.x, pe.y); log['eye_ground_z'] = round(ge, 2)
cam('WB_CAM_eye_Bohn_N_wing_from_NW', tm + e[0], e[1], ge + 1.7, tm + e[2], e[3], ge + e[4], 24)
old = bpy.data.objects.get('VW_CAM_eye_Bohn_from_SW')
if old and os.environ.get('RETIRE', '1') == '1':
    cd = old.data; bpy.data.objects.remove(old, do_unlink=True)
    if cd.users == 0: bpy.data.cameras.remove(cd)
    log['retired'] = 'VW_CAM_eye_Bohn_from_SW (inside tree canopy)'
log['n_objs_after'] = len(bpy.data.objects); log['frame_tm'] = round(tm, 3)
json.dump(log, open(OUT + '/apply.json', 'w'), indent=2)
print('WB cells', cells, 'objs', log['n_objs_after'], json.dumps(per_level), end_panels, 'clip', clipped)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('TESTSAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['TESTSAVE'], copy=True); print('TESTSAVED')
