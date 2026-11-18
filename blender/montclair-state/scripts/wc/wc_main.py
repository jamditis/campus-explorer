# wc (Nov 7 2026, MAIN, day 11): Bohn NW lower-block W face (~218,409) eggcrate re-laid on ONE
# shared 4-bay pier grid for base (TK pi29) + L1 (TL pi67). vw had base bay 3.02 / 4 cols vs
# L1 bay 2.77 / 5 cols (confirmed mismatch, data/wc/probe.json). Span = common overlap of the two
# faces; L1's ~1.9 m south overhang = solid end panel + ONE corner pier (UNVERIFIED decision).
# Count 4 kept from the taller base (matches west-tower language). Reuses vw materials (proud
# eggcrate + opaque-reflective glass). ALL UNVERIFIED.
# REVERT_EXACT: scripts/wc/wc_revert_all.sh
import bpy, bmesh, os, json, math
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
ROOT = '/workspace/nj-scenes/montclair-state'; OUT = ROOT + '/data/wc'
CN = 'WC_Bohn_NW_lower_W_grid_UNVERIFIED'
NOTE = ('wc: Bohn NW lower-block W eggcrate re-laid on one shared 4-bay pier grid (base+L1); '
        'count 4 from taller base; L1 south end panel UNVERIFIED; opaque-reflective glass')
PIER_W = 0.48; BAND_H = 0.42; DEPTH = 0.40; GLASS_T = 0.04; GLASS_OFF = 0.015
FLOOR = 2.75; MARGIN_Z = 0.12; MARGIN_T = 0.10; NBAYS = 4
log = {'session': 'wc'}
assert not bpy.data.collections.get(CN), 'wc already applied'

# ---- NW lower-block W faces (region from probe)
targets = []
for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render: continue
    if not (o.name.startswith('TL_Bohn_Hall_') or o.name == 'TK_Bohn_Hall_232853538_base_UNVERIFIED'): continue
    if 'PH' in o.name: continue
    me = o.data; mw = o.matrix_world
    for pi, p in enumerate(me.polygons):
        n = (mw.to_3x3() @ p.normal).normalized()
        if abs(n.z) > 0.5 or n.x > -0.70: continue
        verts = [mw @ me.vertices[i].co for i in p.vertices]
        zs = [v.z for v in verts]
        if max(zs) - min(zs) < 2.0: continue
        cx = sum(v.x for v in verts) / len(verts); cy = sum(v.y for v in verts) / len(verts)
        if not (214 < cx < 222 and 404 < cy < 414): continue
        w = math.hypot(max(v.x for v in verts) - min(v.x for v in verts),
                       max(v.y for v in verts) - min(v.y for v in verts))
        if w < 8.0: continue
        N = Vector((n.x, n.y, 0)).normalized(); U = Vector((-N.y, N.x, 0)).normalized()
        if U.y < 0: U = -U
        targets.append(dict(mesh=o.name, pi=pi, U=U, N=N, Nf=N.copy(),
                            verts=[Vector((v.x, v.y, 0)) for v in verts],
                            z0=min(zs), z1=max(zs), w=w,
                            cx=cx, cy=cy))
for t in targets:
    print('WC tgt', t['mesh'][:28], 'pi', t['pi'], 'w', round(t['w'], 2),
          'z', round(t['z0'], 1), round(t['z1'], 1), 'xy', round(t['cx'], 1), round(t['cy'], 1))
assert len(targets) == 2, [(t['mesh'], t['pi'], t['w']) for t in targets]

# Prefer L1's U/N if present (same orientation expected); use mean origin
U = targets[0]['U']; N = targets[0]['N']
# re-orient all to shared U (flip if anti-parallel)
for t in targets:
    if t['U'].dot(U) < 0: t['U'] = -t['U']; t['N'] = -t['N']; t['Nf'] = -t['Nf']
U = sum((t['U'] for t in targets), Vector()).normalized()
N = sum((t['N'] for t in targets), Vector()).normalized()
O = sum((v for t in targets for v in t['verts']), Vector()) / sum(len(t['verts']) for t in targets)
for t in targets:
    ts = [(v - O).dot(U) for v in t['verts']]
    t['t0'], t['t1'] = min(ts), max(ts)
    t['c'] = sum(t['verts'], Vector()) / len(t['verts'])
    del t['verts']

levels = {}
for t in targets:
    k = (t['mesh'], round(t['z0'], 1))
    L = levels.setdefault(k, dict(mesh=t['mesh'], pi=t['pi'], z0=t['z0'], z1=t['z1'],
                                  t0=t['t0'], t1=t['t1'], faces=[]))
    L['t0'] = min(L['t0'], t['t0']); L['t1'] = max(L['t1'], t['t1']); L['faces'].append(t)
assert len(levels) == 2, list(levels.keys())

def nw_at(L, tc):
    fs = sorted(L['faces'], key=lambda f: 0 if f['t0'] - 0.3 <= tc <= f['t1'] + 0.3
                else min(abs(tc - f['t0']), abs(tc - f['t1'])))
    f = fs[0]; p = O + U * tc
    return (f['c'] - p).dot(f['Nf']) / N.dot(f['Nf'])

def tnz(p):
    q = Vector((p.x, p.y, 0)) - O
    return (q.dot(U), q.dot(N), p.z)

for L in levels.values():
    L['nw'] = nw_at(L, (L['t0'] + L['t1']) / 2)
log['origin'] = [round(O.x, 3), round(O.y, 3)]
log['U'] = [round(U.x, 4), round(U.y, 4)]
log['N'] = [round(N.x, 4), round(N.y, 4)]
log['levels'] = [{k: (round(v, 3) if isinstance(v, float) else v)
                  for k, v in L.items() if k != 'faces'} | {'nfaces': len(L['faces'])}
                 for L in levels.values()]
print('WC levels', log['levels'])

# Shared grid on COMMON overlap (taller base count = 4)
c0 = max(L['t0'] for L in levels.values()) + MARGIN_T + PIER_W / 2
cN = min(L['t1'] for L in levels.values()) - MARGIN_T - PIER_W / 2
bay = (cN - c0) / NBAYS
piers = [c0 + i * bay for i in range(NBAYS + 1)]
log['pier_centres_t'] = [round(p, 3) for p in piers]
log['bay_m_UNVERIFIED'] = round(bay, 3)
log['NBAYS_UNVERIFIED'] = NBAYS
print('WC piers', log['pier_centres_t'], 'bay', bay)

# ---- strip vw boxes on these 2 levels
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
print('WC removed', removed)

M_CONC = bpy.data.materials['VW_Bohn_W_concrete_UNVERIFIED']
M_GLASS = bpy.data.materials['VW_Bohn_W_glass_opaque_reflective_UNVERIFIED']
M_REVEAL = bpy.data.materials['VW_Bohn_W_reveal_UNVERIFIED']
col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
col['wc_obj'] = 1

class MB:
    def __init__(s, name, mats):
        s.bm = bmesh.new(); s.name = name; s.mats = mats; s.n = 0
    def box(s, ta, tb, L, d0, d1, z0, z1):
        if tb - ta < 0.02 or z1 - z0 < 0.02: return
        nw = nw_at(L, (ta + tb) / 2); cs = []
        for z in (z0, z1):
            for tt, dd in ((ta, d0), (tb, d0), (tb, d1), (ta, d1)):
                p = O + U * tt + N * (nw + dd)
                cs.append(s.bm.verts.new((p.x, p.y, z)))
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            s.bm.faces.new([cs[i] for i in f])
        s.n += 1
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        for p in me.polygons: p.use_smooth = False
        o = bpy.data.objects.new(s.name, me); col.objects.link(o)
        o['wc_obj'] = 1; o['UNVERIFIED'] = NOTE
        return o

mp = MB('WC_Bohn_NW_lower_W_piers_bands_UNVERIFIED', [M_CONC])
mr = MB('WC_Bohn_NW_lower_W_reveals_UNVERIFIED', [M_REVEAL])
mg = MB('WC_Bohn_NW_lower_W_glass_UNVERIFIED', [M_GLASS])

# L1 is the longer face (south overhang) — corner pier for end panel
L_long = max(levels.values(), key=lambda L: L['t1'] - L['t0'])
L_short = min(levels.values(), key=lambda L: L['t1'] - L['t0'])
# south overhang on L1 (more negative t)
T_CORNER = L_long['t0'] + MARGIN_T + PIER_W / 2   # pier at south end of L1
# but only if L_long extends south of the shared grid
log['T_CORNER_UNVERIFIED'] = round(T_CORNER, 3)
log['long_mesh'] = L_long['mesh'][:40]
log['short_mesh'] = L_short['mesh'][:40]

cells = 0; per_level = {}; end_panels = []
for L in sorted(levels.values(), key=lambda L: L['z0']):
    lo = L['t0']; hi = L['t1']
    z_lo = L['z0'] + MARGIN_Z; z_hi = L['z1'] - MARGIN_Z
    ns = max(1, int(round((z_hi - z_lo) / FLOOR))); shh = (z_hi - z_lo) / ns
    lc = 0; used = []
    for pc in piers:
        a, b = max(pc - PIER_W / 2, lo), min(pc + PIER_W / 2, hi)
        if b - a < 0.10: continue
        mp.box(a, b, L, -0.03, DEPTH, z_lo, z_hi); used.append(pc)
    # south partial bay on the longer face → solid end panel + corner pier
    first = used[0] if used else None
    did_end = False
    if first is not None and (first - PIER_W / 2) - lo > 0.9:
        cp = T_CORNER
        # keep corner pier inside this face
        cp = max(cp, lo + PIER_W / 2 + 0.02)
        cp = min(cp, first - PIER_W - 0.05)
        mp.box(cp - PIER_W / 2, cp + PIER_W / 2, L, -0.03, DEPTH, z_lo, z_hi)
        end_panels.append(dict(level=L['mesh'][:20], side='south',
                               t_from=round(cp + PIER_W / 2, 2),
                               t_to=round(first - PIER_W / 2, 2),
                               z=[round(L['z0'], 2), round(L['z1'], 2)]))
        did_end = True
        # bands across the end panel
        for s_i in range(ns + 1):
            if s_i == 0: z0b, z1b = z_lo, z_lo + BAND_H
            elif s_i == ns: z0b, z1b = z_hi - BAND_H, z_hi
            else: zc = z_lo + s_i * shh; z0b, z1b = zc - BAND_H / 2, zc + BAND_H / 2
            mp.box(cp + PIER_W / 2 - 0.02, first - PIER_W / 2 + 0.02, L, -0.03, DEPTH, z0b, z1b)
    for i in range(NBAYS):
        pa, pb = piers[i], piers[i + 1]
        if pa not in used or pb not in used: continue
        ta, tb = pa + PIER_W / 2, pb - PIER_W / 2
        for s_i in range(ns + 1):
            if s_i == 0: z0b, z1b = z_lo, z_lo + BAND_H
            elif s_i == ns: z0b, z1b = z_hi - BAND_H, z_hi
            else: zc = z_lo + s_i * shh; z0b, z1b = zc - BAND_H / 2, zc + BAND_H / 2
            mp.box(ta - 0.02, tb + 0.02, L, -0.03, DEPTH, z0b, z1b)
        for s_i in range(ns):
            z0w = z_lo + s_i * shh + BAND_H + 0.03
            z1w = z_lo + (s_i + 1) * shh - BAND_H - 0.03
            if z1w - z0w < 0.75: continue
            mr.box(ta + 0.005, tb - 0.005, L, GLASS_OFF, DEPTH - 0.01, z0w - 0.02, z1w + 0.02)
            mg.box(ta + 0.03, tb - 0.03, L, GLASS_OFF, GLASS_OFF + GLASS_T, z0w, z1w)
            cells += 1; lc += 1
    per_level[L['mesh'][:18] + '@' + str(round(L['z0'], 1))] = dict(
        cells=lc, storeys=ns, piers=len(used), t=[round(lo, 2), round(hi, 2)], end_panel=did_end)
o1 = mp.done(); o2 = mr.done(); o3 = mg.done()
log['cells'] = cells; log['per_level'] = per_level
log['end_panels_UNVERIFIED'] = end_panels
log['boxes'] = dict(piers_bands=mp.n if False else o1.name,  # placeholder
                    n_pier_band_boxes='see mesh', n_reveal=o2.name, n_glass=o3.name)

def cam(name, t, n, z, tt, tn, tz, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 30000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['wc_obj'] = 1
    p = O + U * t + N * n; q = O + U * tt + N * tn
    o.location = (p.x, p.y, z)
    d = Vector((q.x - p.x, q.y - p.y, tz - z))
    o.rotation_euler = (math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0,
                        math.atan2(d.y, d.x) - math.pi / 2)
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
# closeup: stand out from the face looking at mid-grid
CC = os.environ.get('CLOSE', '0,14,138,0,0,130')
v = [float(a) for a in CC.split(',')]
cam('WC_CAM_closeup_Bohn_NW_lower_W_piers', tm + v[0], v[1], v[2], tm + v[3], v[4], v[5], 28)
# eye from NW courtyard
EC = os.environ.get('EYE', '-6,28,0,8,12')  # dt, n, tt, tn, tz-above-ground
e = [float(a) for a in EC.split(',')]
pe = O + U * (tm + e[0]) + N * e[1]
ge = gz(pe.x, pe.y); log['eye_ground_z'] = round(ge, 2)
cam('WC_CAM_eye_Bohn_NW_lower_from_NW', tm + e[0], e[1], ge + 1.7, tm + e[2], e[3], ge + e[4], 24)
log['n_objs_after'] = len(bpy.data.objects); log['frame_tm'] = round(tm, 3)
json.dump(log, open(OUT + '/apply.json', 'w'), indent=2)
print('WC cells', cells, 'objs', log['n_objs_after'], json.dumps(per_level), end_panels)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('TESTSAVE'):
    bpy.ops.wm.save_as_mainfile(filepath=os.environ['TESTSAVE'], copy=True); print('TESTSAVED')
