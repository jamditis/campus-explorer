"""Session ck (Oct 19 ~9:30 PM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cj; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_lidar_massing_20261019cj.py with SAVE 0 first (-> ci2 -> ci -> ch -> cg -> cf), THEN builds the level-4
OPEN ARCADE gallery on Kasser's SOUTH facade (Joe's photo refs/joe/kasser_level4_arcade_joe_20261019.jpg, Oct 19 ~9:11 PM ET):
 - walls object: S-face band z > FLOOR (131.4) between s 1.80 and S_END is DELETED (bisect + delete; removes the generic shader windows there).
 - roof (LiDAR) object: the south_strip prism's S side face below the arcade top (ZT) in that s range is deleted.
 - all arcade geometry is APPENDED to the roof object's mesh (so north picks it up through the existing Kasser link; new material slots).
   Arcade skin u -0.30..+0.30 (piers, semicircular arch spandrels, curb), dado band on piers, maroon diagonal-bar railings, sconces,
   floor slab at 131.4 (= RHD L4, MEASURED) with saw-cut joints + one drain, white ceiling + transverse beam per pier, inner wall at u 2.45
   with tall maroon/dark-wood framed windows + sill band + skirting, west end wall with glass double door (no sign/lettering), east end wall.
 Heights: FLOOR 131.4 MEASURED (RHD L4 slab 131.0-131.5); shed above 135.61->136.29 MEASURED (cj fit). Bay 3.3 m, pier 0.70 m, opening 2.60 m,
 springing 133.50, apex 134.80, railing 1.05 m, curb 0.30 m, gallery length 6 bays: photo-scaled, UNVERIFIED.
Idempotent (each run starts from the cj chain). 4a BVH printed vs the cf RHD npz (trees excluded)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_lidar_massing_20261019cj.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
FLOOR = 131.4; ZT = float(os.environ.get('ZT', '135.40')); CEIL = ZT - 0.10
BAY = float(os.environ.get('BAY', '3.3')); P = float(os.environ.get('PIER', '0.70')); NB = int(os.environ.get('NBAY', '6'))
OPEN = BAY - P; R = OPEN / 2; APEX = float(os.environ.get('APEX', '134.80')); ZS = APEX - R
CURB = FLOOR + 0.30; RAIL = FLOOR + 1.05
U_OUT, U_IN, U_WALL = -0.30, 0.30, 2.45
S_W = 1.83; S0 = S_W + 0.12; S_END = S0 + NB * BAY + P
# cl (Oct 19 ~10:27 PM ET) params, defaults = ck behaviour: S_ENDX widens the last (corner) pier to that s; EAST_OPEN=1 drops the east end wall; ROOFU1 = u max of the roof S-face cut
if os.environ.get('S_ENDX'): S_END = float(os.environ['S_ENDX'])
EAST_OPEN = os.environ.get('EAST_OPEN', '0') == '1'; ROOFU1 = float(os.environ.get('ROOFU1', '0.25'))
print('ck arcade s', S0, round(S_END, 2), 'bay', BAY, 'pier', P, 'open', round(OPEN, 2), 'spring', round(ZS, 2), 'apex', APEX, 'top', ZT, flush=True)
# ---------- 1. walls: delete the S-face band above FLOOR in the arcade span
wo = bpy.data.objects['Alexander Kasser Theater walls']; wm = wo.matrix_world
bm = bmesh.new(); bm.from_mesh(wo.data); bm.transform(wm)
def bis(bm, co, no, geom=None):
    g = geom if geom is not None else bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=g, dist=1e-4, plane_co=Vector(co), plane_no=Vector(no))
def near_s(f, s0, s1, u0, u1):
    s, u = su(f.calc_center_median()); return s0 < s < s1 and u0 < u < u1 and abs(f.normal.z) < 0.2 and abs(Vector((*d, 0)).dot(f.normal)) > 0.9
cand = [f for f in bm.faces if near_s(f, 1.5, S_END + 2, -0.2, 0.5)]
g = list({e for f in cand for e in f.edges}) + cand + list({v for f in cand for v in f.verts})
bis(bm, (0, 0, FLOOR), (0, 0, 1), g)
cand = [f for f in bm.faces if near_s(f, 1.5, S_END + 2, -0.2, 0.5)]
g = list({e for f in cand for e in f.edges}) + cand + list({v for f in cand for v in f.verts})
co = xy(S_END, 0); bis(bm, (co[0], co[1], 0), (n[0], n[1], 0), g)
dele = [f for f in bm.faces if near_s(f, 1.80, S_END, -0.2, 0.5) and f.calc_center_median().z > FLOOR]
print('ck walls S-band faces deleted', len(dele), flush=True)
bmesh.ops.delete(bm, geom=dele, context='FACES')
bm.transform(wm.inverted()); bm.to_mesh(wo.data); bm.free(); wo.data.update()
# ---------- 2. roof: open the south_strip prism's S face below ZT
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; rm = ro.matrix_world
bm = bmesh.new(); bm.from_mesh(ro.data); bm.transform(rm)
def roofc(f): return near_s(f, 1.5, S_END + 2, -0.08, ROOFU1) and min(v.co.z for v in f.verts) > 133.9 and f.material_index not in (6, 7)
cand = [f for f in bm.faces if roofc(f)]
g = list({e for f in cand for e in f.edges}) + cand + list({v for f in cand for v in f.verts}); bis(bm, (0, 0, ZT), (0, 0, 1), g)
for sv in (S_W, S_END):
    cand = [f for f in bm.faces if roofc(f)]
    g = list({e for f in cand for e in f.edges}) + cand + list({v for f in cand for v in f.verts}); co = xy(sv, 0); bis(bm, (co[0], co[1], 0), (n[0], n[1], 0), g)
dele = [f for f in bm.faces if roofc(f) and S_W - 0.01 < su(f.calc_center_median())[0] < S_END and max(v.co.z for v in f.verts) < ZT + 0.005]
print('ck roof S-face faces deleted', len(dele), flush=True)
bmesh.ops.delete(bm, geom=dele, context='FACES')
# ---------- 3. materials (new slots on the roof mesh)
me = ro.data
def mk(name, col, rough, metal=0.0, bump=0.0, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    for nd in [x for x in nt.nodes if x.name.startswith('ck_')]: nt.nodes.remove(nd)
    if bump > 0:
        tx = nt.nodes.new('ShaderNodeTexNoise'); tx.name = 'ck_noise'; tx.inputs['Scale'].default_value = 60.0; tx.inputs['Detail'].default_value = 6
        bp = nt.nodes.new('ShaderNodeBump'); bp.name = 'ck_bump'; bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 0.005
        nt.links.new(tx.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    if emit > 0:
        b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = emit
    return m
MATS = {'stucco': mk('Arcade_stucco_white_ck', (0.80, 0.785, 0.75), 0.85, 0, 0.25), 'ceil': mk('Arcade_ceiling_white_ck', (0.82, 0.81, 0.78), 0.8),
        'floor': mk('Arcade_concrete_floor_ck', (0.34, 0.33, 0.31), 0.9, 0, 0.15), 'curb': mk('Arcade_concrete_curb_ck', (0.70, 0.69, 0.66), 0.85, 0, 0.2),
        'rail': mk('Arcade_rail_maroon_ck', (0.045, 0.009, 0.008), 0.5, 0.2), 'joint': mk('Arcade_joint_dark_ck', (0.10, 0.10, 0.10), 0.95),
        'sconce': mk('Arcade_sconce_bronze_ck', (0.035, 0.033, 0.03), 0.4, 0.6), 'doorframe': mk('Arcade_door_frame_white_ck', (0.75, 0.75, 0.74), 0.35, 0.6),
        'wood': mk('Arcade_window_frame_wood_ck', (0.06, 0.025, 0.014), 0.55)}
MI = {}
for k_, m in MATS.items():
    if m.name not in [x.name for x in me.materials if x]: me.materials.append(m)
    MI[k_] = [x.name if x else None for x in me.materials].index(m.name)
GLASS = [x.name if x else None for x in me.materials].index('Kasser_window_glass_cj')
# ---------- 4. geometry helpers (world coords, deck frame)
def P3(s, u, z): q = xy(s, u); return Vector((q[0], q[1], z))
def box(s0, s1, u0, u1, z0, z1, mat):
    c = [(s0, u0), (s1, u0), (s1, u1), (s0, u1)]
    lo = [bm.verts.new(P3(s, u, z0)) for s, u in c]; hi = [bm.verts.new(P3(s, u, z1)) for s, u in c]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi)] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i])) for i in range(4)]
    for f in fs: f.material_index = mat
    return fs
def prism_sz(poly, u0, u1, mat):  # polygon in (s, z), extruded u0..u1
    a = [bm.verts.new(P3(s, u0, z)) for s, z in poly]; b = [bm.verts.new(P3(s, u1, z)) for s, z in poly]; N = len(poly)
    fs = [bm.faces.new(a), bm.faces.new(b[::-1])] + [bm.faces.new((a[i], b[i], b[(i + 1) % N], a[(i + 1) % N])) for i in range(N)]
    for f in fs: f.material_index = mat
    return fs
def bar_sz(p0, p1, w, u0, u1, mat):  # straight bar between two (s, z) points, width w, depth u0..u1
    p0 = np.array(p0); p1 = np.array(p1); t = (p1 - p0) / np.linalg.norm(p1 - p0); q = np.array([-t[1], t[0]]) * w / 2
    return prism_sz([tuple(p0 - q), tuple(p1 - q), tuple(p1 + q), tuple(p0 + q)], u0, u1, mat)
def cyl(s, u, z0, z1, r, mat, seg=12):
    lo = [bm.verts.new(P3(s, u, z0) + Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), 0))) for i in range(seg)]
    hi = [bm.verts.new(v.co + Vector((0, 0, z1 - z0))) for v in lo]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi)] + [bm.faces.new((lo[i], lo[(i + 1) % seg], hi[(i + 1) % seg], hi[i])) for i in range(seg)]
    for f in fs: f.material_index = mat
new0 = len(bm.faces)
ST, CE, FL, CB, RL, JT, SC, DF, WD = (MI[k_] for k_ in ('stucco', 'ceil', 'floor', 'curb', 'rail', 'joint', 'sconce', 'doorframe', 'wood'))
SK0 = FLOOR - 0.40   # skin bottom (belt course line)
piers = [S0 + i * BAY for i in range(NB + 1)]
for ps in piers:
    PW = (S_END - ps) if (ps == piers[-1] and os.environ.get('S_ENDX')) else P   # cl: corner pier
    box(ps, ps + PW, U_OUT, U_IN, SK0, ZT, ST)
    box(ps - 0.03, ps + PW + 0.03, U_OUT - 0.03, U_IN + 0.03, FLOOR + 1.10, FLOOR + 1.20, ST)       # dado band (photo), UNVERIFIED height
    box(ps - 0.02, ps + PW + 0.02, U_OUT - 0.02, U_IN + 0.02, ZS - 0.12, ZS, ST)                    # impost band at springing
    if ps > S0 + 0.1:
        cyl(ps + P / 2, U_IN + 0.08, ZS - 0.48, ZS - 0.18, 0.065, SC)                              # sconce on gallery face, just under the impost (photo)
        box(ps + P / 2 - 0.04, ps + P / 2 + 0.04, U_IN, U_IN + 0.02, ZS - 0.42, ZS - 0.24, SC)    # backplate
    # (no outside sconces: not photo-backed, 2026-10-13 rule)
for i in range(NB):
    sL = S0 + i * BAY + P; sR = sL + OPEN; sc_ = (sL + sR) / 2
    arc = [(sc_ - R * math.cos(math.pi * k / 24), ZS + R * math.sin(math.pi * k / 24)) for k in range(25)]
    prism_sz([(sR, ZT), (sL, ZT)] + arc, U_OUT, U_IN, ST)       # spandrel: top edge + arch intrados
    box(sL, sR, U_OUT, U_IN, SK0, CURB, CB)                     # curb / ledge (photo ~0.3 m)
    # railing: posts at ends + middle, top + bottom rails, diagonal bars alternating per panel (photo)
    UR0, UR1 = -0.07, -0.02
    for sp in (sL + 0.05, sc_, sR - 0.05): box(sp - 0.025, sp + 0.025, UR0 - 0.005, UR1 + 0.005, CURB, RAIL, RL)
    box(sL, sR, UR0 - 0.01, UR1 + 0.01, RAIL - 0.05, RAIL, RL); box(sL, sR, UR0, UR1, CURB + 0.08, CURB + 0.12, RL)
    for pi_, (a0, a1) in enumerate(((sL + 0.075, sc_ - 0.025), (sc_ + 0.025, sR - 0.075))):
        z0, z1 = CURB + 0.12, RAIL - 0.05; H = z1 - z0; sgn = 1 if (i + pi_) % 2 == 0 else -1; sp = 0.20
        for t in np.arange(-H + sp / 2, a1 - a0, sp):   # lines s = a0 + t + sgn*(z - z0) style, clipped to the panel
            pts = []
            for zz in (z0, z1):
                ss = a0 + t + (zz - z0) if sgn > 0 else a1 - t - (zz - z0); pts.append((ss, zz))
            (s_a, z_a), (s_b, z_b) = pts
            def clip(sa, za, sb, zb):
                if sa < a0: za = za + (a0 - sa) * (zb - za) / (sb - sa); sa = a0
                if sa > a1: za = za + (a1 - sa) * (zb - za) / (sb - sa); sa = a1
                return sa, za
            s_a, z_a = clip(s_a, z_a, s_b, z_b); s_b, z_b = clip(s_b, z_b, s_a, z_a)
            if math.hypot(s_b - s_a, z_b - z_a) > 0.08: bar_sz((s_a, z_a), (s_b, z_b), 0.022, UR0 + 0.01, UR1 - 0.01, RL)
# floor slab + joints + drain
box(S_W, S_END, U_OUT + 0.02, U_WALL, FLOOR - 0.25, FLOOR, FL)
for js in np.arange(S0 + P + 1.65, S_END - 0.3, 1.65): box(js - 0.006, js + 0.006, U_IN, U_WALL, FLOOR, FLOOR + 0.002, JT)
box(S_W + 0.12, S_END, (U_IN + U_WALL) / 2 - 0.006, (U_IN + U_WALL) / 2 + 0.006, FLOOR, FLOOR + 0.002, JT)
dr = S0 + 4 * BAY + P + 0.5; box(dr, dr + 0.30, U_IN + 0.25, U_IN + 0.50, FLOOR, FLOOR + 0.003, JT)
# ceiling + transverse beams at each pier
box(S_W, S_END, U_IN - 0.02, U_WALL, CEIL, ZT, CE)
for ps in piers: box(ps + P / 2 - 0.13, ps + P / 2 + 0.13, U_IN, U_WALL, CEIL - 0.28, CEIL, CE)
# inner wall + skirting + sill band + windows
box(S_W, S_END, U_WALL, U_WALL + 0.04, FLOOR, CEIL, ST)
box(S_W + 0.12, S_END - 0.12, U_WALL - 0.02, U_WALL, FLOOR, FLOOR + 0.12, CB)
WB, WT, WW = FLOOR + 0.95, FLOOR + 3.15, 1.30
for i in range(NB):
    sc_ = S0 + i * BAY + P + OPEN / 2
    box(sc_ - WW / 2, sc_ + WW / 2, U_WALL - 0.07, U_WALL, WB, WT, WD)                         # dark wood/maroon frame
    box(sc_ - WW / 2 + 0.09, sc_ + WW / 2 - 0.09, U_WALL - 0.075, U_WALL - 0.06, WB + 0.09, WT - 0.09, GLASS)
    box(sc_ - 0.025, sc_ + 0.025, U_WALL - 0.085, U_WALL - 0.06, WB + 0.09, WT - 0.09, WD)     # mullion
    box(sc_ - WW / 2 - 0.08, sc_ + WW / 2 + 0.08, U_WALL - 0.11, U_WALL, WB - 0.06, WB, WD)     # sill
box(S_W + 0.12, S_END - 0.12, U_WALL - 0.03, U_WALL, FLOOR + 1.10, FLOOR + 1.18, WD)           # trim band (photo: dark wood horizontal)
# end walls; west one with a glass double door (photo); NO sign/lettering (2026-10-13 rule)
uc = (U_IN + U_WALL) / 2; DW, DH = 1.80, 2.30
box(S_W, S0, U_IN - 0.02, uc - DW / 2, FLOOR, CEIL, ST); box(S_W, S0, uc + DW / 2, U_WALL, FLOOR, CEIL, ST); box(S_W, S0, uc - DW / 2, uc + DW / 2, FLOOR + DH, CEIL, ST)
box(S_W + 0.02, S_W + 0.06, uc - DW / 2, uc + DW / 2, FLOOR, FLOOR + DH, GLASS)
for (a, b_) in ((uc - DW / 2, uc - DW / 2 + 0.07), (uc - 0.035, uc + 0.035), (uc + DW / 2 - 0.07, uc + DW / 2)): box(S0 - 0.06, S0 + 0.02, a, b_, FLOOR, FLOOR + DH, DF)
box(S0 - 0.06, S0 + 0.02, uc - DW / 2, uc + DW / 2, FLOOR + DH - 0.08, FLOOR + DH, DF); box(S0 - 0.06, S0 + 0.02, uc - DW / 2, uc + DW / 2, FLOOR + 0.95, FLOOR + 1.0, DF)
if not EAST_OPEN: box(S_END - 0.12, S_END, U_IN - 0.02, U_WALL, FLOOR, CEIL, ST)
print('ck arcade faces added', len(bm.faces) - new0, flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['ck_piers'] = str([round(x, 3) for x in piers]); ro['ck_arcade'] = 'level-4 S arcade (ck): s %.2f-%.2f, %d bays, floor %.2f, top %.2f' % (S0, S_END, NB, FLOOR, ZT)
# ---------- 5. 4a BVH vs RHD npz
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm_ = zz['names']; kp = np.array([not str(nm_[i]).startswith('NT_') for i in ob]); T = T[kp]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('ck 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b2).overlap(RB)), flush=True); b2.free()
print('ck roof+arcade faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('ck main: SAVED', flush=True)
