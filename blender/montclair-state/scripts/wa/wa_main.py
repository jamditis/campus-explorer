# wa (Nov 7 2026, MAIN, day 11): Bohn south-wing W face (vw 'narrow' 2+2 + base 4) re-laid as ONE
# continuous 4-bay eggcrate grid with shared pier lines on base/L1/L2, starting at the TP_Bohn_shaft_0
# north side face (t=411.05) so no window cell is cut by the shaft (4a) and the doubled pier at the
# polygon split (t=416.92) is gone. Counts unchanged (2 per ~6.6 m half; slide 1519 narrow end faces
# read 2 cols). Same vw language/materials (proud eggcrate + opaque-reflective glass). ALL UNVERIFIED.
# REVERT=1 restores nothing exactly -> use scripts/wa/wa_revert_all.sh (REVERT_EXACT backup).
import bpy, bmesh, os, json, math
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
ROOT = '/workspace/nj-scenes/montclair-state'; OUT = ROOT + '/data/wa'
CN = 'WA_Bohn_south_wing_W_grid_UNVERIFIED'
NOTE = ('wa: Bohn south-wing W eggcrate re-laid as one continuous 4-bay grid from TP shaft_0 side face; '
        'pier lines shared base/L1/L2; counts/pier/window widths UNVERIFIED (slides 1251/1519); opaque-reflective glass')
PIER_W = 0.48; BAND_H = 0.42; DEPTH = 0.40; GLASS_T = 0.04; GLASS_OFF = 0.015
FLOOR = 2.75; MARGIN_Z = 0.12
T_SHAFT = None            # TP_Bohn_shaft_0 north side face, computed in-frame below
NBAYS = 4
log = {'session': 'wa'}

# ---- wing axis from the same face attributes vw used
targets = []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render: continue
    if not (o.name.startswith('TL_Bohn_Hall_') or o.name == 'TK_Bohn_Hall_232853538_base_UNVERIFIED'): continue
    if 'PH' in o.name: continue
    me = o.data; mw = o.matrix_world
    if 'ti_dir' not in me.attributes: continue
    for pi, p in enumerate(me.polygons):
        n = (mw.to_3x3() @ p.normal).normalized()
        if abs(n.z) > 0.5 or n.x > -0.70: continue
        verts = [mw @ me.vertices[i].co for i in p.vertices]
        zs = [v.z for v in verts]
        if max(zs) - min(zs) < 2.0: continue
        cx = sum(v.x for v in verts) / len(verts); cy = sum(v.y for v in verts) / len(verts)
        if not (221 < cx < 230 and 355 < cy < 369): continue
        N = Vector((n.x, n.y, 0)).normalized(); U = Vector((-N.y, N.x, 0)).normalized()
        if U.y < 0: U = -U
        if (max(v.x for v in verts) - min(v.x for v in verts)) ** 2 + (max(v.y for v in verts) - min(v.y for v in verts)) ** 2 < 5.5 ** 2: continue
        targets.append(dict(mesh=o.name, pi=pi, U=U, N=N, verts=[Vector((v.x, v.y, 0)) for v in verts],
                            z0=min(zs), z1=max(zs)))
U = targets[0]['U']; N = targets[0]['N']
O = sum((v for t in targets for v in t['verts']), Vector()) / sum(len(t['verts']) for t in targets)
for t in targets:
    ts = [(v - O).dot(U) for v in t['verts']]; ns = [(v - O).dot(N) for v in t['verts']]
    t['t0'], t['t1'] = min(ts), max(ts); t['nw'] = sum(ns) / len(ns)
    # plane line n(t) of this face in the local frame
    Nf = t['N']; c = sum(t['verts'], Vector()) / len(t['verts'])
    t['c'] = c; t['Nf'] = Nf
    del t['verts']
log['origin'] = [round(O.x, 3), round(O.y, 3)]
for t in targets: print('WA tgt', t['mesh'][:16], t['pi'], round(t['t0'],2), round(t['t1'],2), round(t['nw'],3), round(t['z0'],1))
levels = {}
for t in targets:
    k = (t['mesh'], round(t['z0'], 1))
    L = levels.setdefault(k, dict(mesh=t['mesh'], z0=t['z0'], z1=t['z1'], t0=t['t0'], t1=t['t1'], nw=[], faces=[]))
    L['t0'] = min(L['t0'], t['t0']); L['t1'] = max(L['t1'], t['t1']); L['nw'].append(t['nw']); L['faces'].append(t)
for L in levels.values(): L['nw'] = sum(L['nw']) / len(L['nw'])
def nw_at(L, tc):
    fs = sorted(L['faces'], key=lambda f: 0 if f['t0'] - 0.3 <= tc <= f['t1'] + 0.3 else min(abs(tc - f['t0']), abs(tc - f['t1'])))
    f = fs[0]; p = O + U * tc
    # point on face plane along N from p: plane through f['c'] with normal f['Nf']
    den = N.dot(f['Nf']); s_ = (f['c'] - p).dot(f['Nf']) / den
    return s_
log['U'] = [round(U.x, 4), round(U.y, 4)]; log['N'] = [round(N.x, 4), round(N.y, 4)]
log['levels'] = [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in L.items() if k != 'faces'} for L in levels.values()]
print('WA levels', log['levels'])
assert len(levels) == 3, levels

def tnz(p): q = Vector((p.x, p.y, 0)) - O; return (q.dot(U), q.dot(N), p.z)
sh = bpy.data.objects['TP_Bohn_shaft_0_L2_UNVERIFIED']
sv = [tnz(sh.matrix_world @ v.co) for v in sh.data.vertices]
T_SHAFT = max(a[0] for a in sv)
log['shaft0_t_range'] = [round(min(a[0] for a in sv), 3), round(T_SHAFT, 3)]
log['shaft0_n_range'] = [round(min(a[1] for a in sv), 3), round(max(a[1] for a in sv), 3)]
T_END_C = min(L['t1'] for L in levels.values()) - 0.10 - PIER_W / 2
T_SHAFT = max(T_SHAFT, max(L['t0'] for L in levels.values()) - 0.10)
log['T_SHAFT_used'] = round(T_SHAFT, 3); log['T_END_C'] = round(T_END_C, 3)
print('WA shaft', log['shaft0_t_range'], log['shaft0_n_range'], 'T_SHAFT', T_SHAFT, 'T_END_C', T_END_C)

# ---- strip the vw boxes on this wing face (islands by centre in t/n/z)
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
    removed[vn] = len(kill) // 8
    bmesh.ops.delete(bm, geom=list(set(kill)), context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
log['removed_vw_boxes'] = removed
print('WA removed', removed)

# ---- rebuild with shared pier lines
M_CONC = bpy.data.materials['VW_Bohn_W_concrete_UNVERIFIED']
M_GLASS = bpy.data.materials['VW_Bohn_W_glass_opaque_reflective_UNVERIFIED']
M_REVEAL = bpy.data.materials['VW_Bohn_W_reveal_UNVERIFIED']
col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col); col['wa_obj'] = 1

class MB:
    def __init__(s, name, mats): s.bm = bmesh.new(); s.name = name; s.mats = mats
    def box(s, tc, w, L, d0, d1, z0, z1):
        nw = nw_at(L, tc)
        cs = []
        for z in (z0, z1):
            for a, dd in ((-1, d0), (1, d0), (1, d1), (-1, d1)):
                tt = tc + a * w / 2; nn = nw + dd
                p = O + U * tt + N * nn
                cs.append(s.bm.verts.new((p.x, p.y, z)))
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            s.bm.faces.new([cs[i] for i in f])
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o = bpy.data.objects.new(s.name, me); col.objects.link(o)
        o['wa_obj'] = 1; o['UNVERIFIED'] = NOTE
        return o

c0 = T_SHAFT + PIER_W / 2
bay = (T_END_C - c0) / NBAYS
piers = [c0 + i * bay for i in range(NBAYS + 1)]
log['pier_centres_t'] = [round(p, 3) for p in piers]; log['bay_m_UNVERIFIED'] = round(bay, 3)
mp = MB('WA_Bohn_S_wing_W_piers_bands_UNVERIFIED', [M_CONC])
mr = MB('WA_Bohn_S_wing_W_reveals_UNVERIFIED', [M_REVEAL])
mg = MB('WA_Bohn_S_wing_W_glass_UNVERIFIED', [M_GLASS])
cells = 0
for L in sorted(levels.values(), key=lambda L: L['z0']):
    z_lo = L['z0'] + MARGIN_Z; z_hi = L['z1'] - MARGIN_Z
    ns = max(1, int(round((z_hi - z_lo) / FLOOR))); sh = (z_hi - z_lo) / ns
    for pc in piers: mp.box(pc, PIER_W, L, -0.03, DEPTH, z_lo, z_hi)
    for i in range(NBAYS):
        tc = piers[i] + bay / 2; bw = bay - PIER_W - 0.04
        for s_i in range(ns + 1):
            if s_i == 0: z0b, z1b = z_lo, z_lo + BAND_H
            elif s_i == ns: z0b, z1b = z_hi - BAND_H, z_hi
            else: zc = z_lo + s_i * sh; z0b, z1b = zc - BAND_H / 2, zc + BAND_H / 2
            mp.box(tc, bw, L, -0.03, DEPTH, z0b, z1b)
        ww = bay - PIER_W - 0.06
        for s_i in range(ns):
            z0w = z_lo + s_i * sh + BAND_H + 0.03; z1w = z_lo + (s_i + 1) * sh - BAND_H - 0.03
            if z1w - z0w < 0.75: continue
            mr.box(tc, ww + 0.05, L, GLASS_OFF, DEPTH - 0.01, z0w - 0.02, z1w + 0.02)
            mg.box(tc, ww, L, GLASS_OFF, GLASS_OFF + GLASS_T, z0w, z1w)
            cells += 1
    # solid strip between the face end and the first pier is plain wall (no overlay) — shaft corner
o1 = mp.done(); o2 = mr.done(); o3 = mg.done()
log['cells'] = cells

def cam(name, t, n, z, tt, tn, tz, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 30000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['wa_obj'] = 1
    p = O + U * t + N * n; q = O + U * tt + N * tn
    o.location = (p.x, p.y, z); d = Vector((q.x - p.x, q.y - p.y, tz - z))
    o.rotation_euler = (math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0, math.atan2(d.y, d.x) - math.pi / 2)
    return o
NL2 = nw_at([L for L in levels.values() if L['mesh'].startswith('TL_Bohn_Hall_L2')][0], T_SHAFT + 2.0)
cam('WA_CAM_closeup_Bohn_S_wing_W_grid', T_SHAFT + 10.0, NL2 + 16.0, 147.0, T_SHAFT + 2.0, NL2, 141.5, 30)
def gz(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    for gn in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
        go = bpy.data.objects.get(gn)
        if not go: continue
        e = go.evaluated_get(dg); iw = go.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]: return (go.matrix_world @ r[1]).z
    return 130.0
pe = O + U * (-24.0) + N * 34.0
ge = gz(pe.x, pe.y); log['eye_ground_z'] = round(ge, 2)
cam('WA_CAM_eye_Bohn_S_wing_from_SW', -24.0, 34.0, ge + 1.7, 0.0, 0.0, ge + 16.0, 24)
log['n_objs_after'] = len(bpy.data.objects)
json.dump(log, open(OUT + '/apply.json', 'w'), indent=2)
print('WA cells', cells, 'objs', log['n_objs_after'], 'piers', log['pier_centres_t'])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
