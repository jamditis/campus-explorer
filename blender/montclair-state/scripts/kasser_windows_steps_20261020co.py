"""Session co (Oct 20 ~1:30 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cn; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_east_loggia_20261020cn.py with SAVE 0 (-> cm -> cl -> ck -> cj -> ci2 -> ci -> ch -> cg -> cf), then:
 1. CURVED EAST WALL WINDOWS (PD Commons east photo; PARALLEL_20261020_cn.md sec 2): cj's 7 windows (frame/glass slots, s 54.7-55.3, z > 136)
    are deleted and replaced by the photo's 1 + 2 + 2 + 2 + 1 = 8: pairs centred over cn loggia arches 2-4 (face D arch centres projected
    onto the curved wall face s 55.0 = same u), leaf 1.30 m, 0.30 m stucco mullion pier; singles 1.10 m, 0.50 m off the outer pairs.
    Sill/head = cj's (shed + 0.45, 3.9 m tall). All widths/gaps photo-scaled = UNVERIFIED; the arch layout they key to is cn (UNVERIFIED);
    the wall face s 55.0 is MEASURED (cj LiDAR).
 3. Loggia ceiling downlights (one per bay, 5) + barrel-tile edge course on the cn east eave (sizes UNVERIFIED). No gutter (not in the photo).
 2. ONE STEP RUN ACROSS THE EAST FRONT: cm flight B (u 6-14.5) and cn's two diagonal runs are deleted and rebuilt as ONE mitred run on one
    riser grid (R 0.164 / T 0.345, 10 risers 131.80 -> 130.16) along the plaza-edge polyline P0 (SB, 6.0) -> P1 (SB, 14.5) -> E1 -> E2
    (cn E1/E2: plateau edge 1.9 m off face D's N end, 1.0 m off face N's end, MEASURED 1 m bins). SB = 73.62 = cm's fitted top riser
    (max(LiDAR, rendered terrain), so the 1 m terrain stays under the treads until the north clamp is done; ~0.4 m E of the LiDAR edge
    73.20 = approximation). Treads are mitred bands (no seam / overlap at either turn); each tread runs from the S cheek to where the
    MEASURED lower grade (LiDAR median 2.5-4.5 m out) rises above it, so the run tapers out to the north like cn. Plaza fill 131.80 over
    s 73.22-73.62 (cm's old top tread) and the thin wedge between cn's E0 line and the new P1 line. Cheek (u 5.6-6.0) and the two maroon
    rails (u 8.5 / 12.0, Commons photo in kind, positions UNVERIFIED) rebuilt on the new grid.
All new geometry goes into the roof object's mesh (north picks it up through the Kasser link). 4a BVH printed vs the cf RHD npz."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_east_loggia_20261020cn.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
def P3(s, u, z): q = xy(s, u); return Vector((q[0], q[1], z))
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']
names = [x.name if x else None for x in me.materials]; mi = names.index
GL, FR, STEP, NOSE, RLM, ST = mi('Kasser_window_glass_cj'), mi('Kasser_window_frame_maroon_cj'), mi('Kasser_step_concrete_cm'), mi('Kasser_step_nosing_cm'), mi('Arcade_rail_maroon_ck'), mi('Arcade_stucco_white_ck')
JT = mi('Arcade_joint_dark_ck')
FLOOR = 131.80; RS, TS, NR = 0.164, 0.345, 10
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
def fsu(f): return [su(v.co) for v in f.verts]
# ---------- 1a. delete cj curved-wall windows
win = [f for f in bm.faces if f.material_index in (GL, FR) and all(54.7 < s < 55.35 and 17.3 < u < 52 for s, u in fsu(f)) and 136.0 < min(v.co.z for v in f.verts) and max(v.co.z for v in f.verts) < 142.5]   # z/u limits keep the cn tower N-face bracket (s 55.0-55.2, z 148+)
zs = [v.co.z for f in win for v in f.verts]; us_ = sorted({round(u, 2) for f in win for s, u in fsu(f)})
ZB, ZT = (min(zs), max(zs)) if zs else (136.9, 140.8)
print('co cj windows deleted faces', len(win), 'z %.2f..%.2f' % (ZB, ZT), 'u range %.2f..%.2f' % (min(us_), max(us_)), flush=True)
bmesh.ops.delete(bm, geom=win, context='FACES')
def boxsu(s0, s1, u0, u1, z0, z1, mat):
    c = [(s0, u0), (s1, u0), (s1, u1), (s0, u1)]
    lo = [bm.verts.new(P3(s, u, z0)) for s, u in c]; hi = [bm.verts.new(P3(s, u, z1)) for s, u in c]
    fs = [bm.faces.new(lo), bm.faces.new(hi)] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i])) for i in range(4)]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
# ---------- 1b. new windows keyed to cn arches 2-4
frD = G['fr']['D']; OPEN, P = G['OPEN'], G['P']; ac = [4.63 + P + OPEN / 2 + i * (OPEN + P) for i in range(4)]
uarch = [float(frD.SU(a, 0.0)[1]) for a in ac]
print('co arch centre u', [round(u, 2) for u in uarch], flush=True)
# curved wall top (arc) at u from the roof mesh (max z of verts on the wall strip)
cw = np.array([(su(v.co)[1], v.co.z) for v in bm.verts if 53.4 < su(v.co)[0] < 55.1 and v.co.z > 141.0])
def arctop(u): k = np.abs(cw[:, 0] - u) < 0.6; return float(cw[k, 1].max()) if k.any() else 0.0
LEAF, MUL, SGL, GAP, WALL = 1.30, 0.30, 1.10, 0.50, 55.0
W = []
for uc in uarch[1:4]: W += [(uc - MUL / 2 - LEAF, uc - MUL / 2), (uc + MUL / 2, uc + MUL / 2 + LEAF)]
ul = uarch[1] - MUL / 2 - LEAF - GAP; ur = uarch[3] + MUL / 2 + LEAF + GAP
W = [(ul - SGL, ul)] + W + [(ur, ur + SGL)]
F_ = 0.12
for u0, u1 in sorted(W):
    top = min(arctop(u0), arctop(u1))
    print('co window u %.2f..%.2f arc top %.2f (head %.2f)' % (u0, u1, top, ZT), flush=True)
    boxsu(WALL - 0.10, WALL + 0.05, u0, u1, ZB, ZT, FR)
    boxsu(WALL - 0.10, WALL + 0.07, u0 + F_, u1 - F_, ZB + F_, ZT - F_, GL)
# ci head copings were keyed to cj's 7 windows (light ledges across the new gaps in the first co close-up) -> delete, one head cap per new window
CP = mi('Kasser_coping_precast_ci')
cop = [f for f in bm.faces if f.material_index == CP and all(54.3 < s < 55.7 and 17.3 < u < 45 for s, u in fsu(f)) and all(140.85 < v.co.z < 141.25 for v in f.verts)]
cz = [v.co.z for f in cop for v in f.verts]; csu = [su(v.co) for f in cop for v in f.verts]
print('co ci copings deleted', len(cop), 'z %.2f..%.2f s %.2f..%.2f' % (min(cz), max(cz), min(a for a, b in csu), max(a for a, b in csu)) if cop else '', flush=True)
cs0, cs1 = (min(a for a, b in csu), max(a for a, b in csu)) if cop else (WALL - 0.10, WALL + 0.15)
bmesh.ops.delete(bm, geom=cop, context='FACES')
for u0, u1 in W: boxsu(cs0, cs1, u0 - 0.06, u1 + 0.06, ZT - 0.005, ZT + 0.10, CP)   # head cap per window (UNVERIFIED, ci kind)
print('co curved-wall windows', len(W), flush=True)
# ---------- 2a. delete cm flight B (+ rails, cheek, its top tread) and cn's diagonal treads
E0, E1, E2 = np.array(G['E0']), np.array(G['E1']), np.array(G['E2'])
def in_B(f): return all((72.70 if f.material_index == ST else 73.15) < s < 77.4 and 5.5 < u < 14.56 for s, u in fsu(f)) and max(v.co.z for v in f.verts) < 133.0   # ST: cm cheek starts at xtB - 0.80
SEGS0 = [(E0, E1), (E1, E2)]
def outward_of_edge(s, u):
    best = -1e9   # MAX over the runs (co bug fix: cn's runs overlap 0.9 m past E1, and those vertices lie inside the OTHER run's line)
    for p0, p1 in SEGS0:
        t = (p1 - p0) / np.linalg.norm(p1 - p0); nn = np.array([t[1], -t[0]]); nn = nn if nn[0] > 0 else -nn
        q = np.array([s, u]) - p0; a = q @ t
        if -1.2 < a < np.linalg.norm(p1 - p0) + 1.2: best = max(best, q @ nn)
    return best
def in_diag(f):
    if f.material_index not in (STEP, NOSE) or max(v.co.z for v in f.verts) > 131.70: return False
    return all(u > 14.0 and s > 58.0 and outward_of_edge(s, u) > -0.1 for s, u in fsu(f))
dB = [f for f in bm.faces if f.material_index in (STEP, NOSE, RLM, ST) and in_B(f)]
dD = [f for f in bm.faces if f not in set(dB) and in_diag(f)]
print('co deleted flight B faces', len(dB), 'cn diagonal tread faces', len(dD), flush=True)
bmesh.ops.delete(bm, geom=dB + dD, context='FACES')
# ---------- 2b. one mitred run
SB = float(os.environ.get('SB', '73.62'))
Q = [np.array([SB, 6.0]), np.array([SB, 14.5]), E1, E2]
segL = [float(np.linalg.norm(Q[i + 1] - Q[i])) for i in range(3)]; cum = np.concatenate([[0], np.cumsum(segL)])
def seg_t(i): return (Q[i + 1] - Q[i]) / segL[i]
def seg_n(i): t = seg_t(i); nn = np.array([t[1], -t[0]]); return nn if nn[0] > 0 else -nn
print('co run polyline', [tuple(np.round(q, 2)) for q in Q], 'L', [round(x, 2) for x in segL], 'turns deg', [round(math.degrees(math.acos(float(seg_t(i) @ seg_t(i + 1)))), 1) for i in range(2)], flush=True)
def at(a):
    i = min(int(np.searchsorted(cum, a, side='right')) - 1, 2); i = max(i, 0)
    return Q[i] + seg_t(i) * (a - cum[i]), i
zpt = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); gk = (zpt['c'] == 1) | (zpt['c'] == 2)
GSn = (zpt['x'][gk] - A[0]) * n[0] + (zpt['y'][gk] - A[1]) * n[1]; GUn = (zpt['x'][gk] - A[0]) * d[0] + (zpt['y'][gk] - A[1]) * d[1]; GZn = zpt['z'][gk]
sk = (GSn > 55) & (GSn < 85) & (GUn > 0) & (GUn < 50); GSn, GUn, GZn = GSn[sk], GUn[sk], GZn[sk]
al = np.arange(0, cum[-1] + 1e-6, 0.5); zl = []
for a in al:
    p, i = at(a); q = np.stack([GSn, GUn], 1) - p; aa = q @ seg_t(i); ww = q @ seg_n(i)
    kk = (np.abs(aa) < 1.0) & (ww > 2.5) & (ww < 4.5); zl.append(float(np.median(GZn[kk])) if kk.sum() > 3 else 131.8)
zl = np.array(zl)
def offset_line(aend, w):
    """mitred offset of the polyline from arc 0 to aend at distance w (perpendicular end cuts)"""
    pts = [Q[0] + seg_n(0) * w]
    for j in (1, 2):
        if cum[j] < aend - 1e-6:
            n1, n2 = seg_n(j - 1), seg_n(j); m = (n1 + n2) / (1 + float(n1 @ n2)); pts.append(Q[j] + m * w)
    p, i = at(aend); pts.append(p + seg_n(i) * w)
    return pts
def band(aend, w0, w1, z0, z1, mat):
    inn = offset_line(aend, w0); out = offset_line(aend, w1)
    lo_i = [bm.verts.new(P3(*p, z0)) for p in inn]; hi_i = [bm.verts.new(P3(*p, z1)) for p in inn]
    lo_o = [bm.verts.new(P3(*p, z0)) for p in out]; hi_o = [bm.verts.new(P3(*p, z1)) for p in out]
    fs = []; m_ = len(inn)
    for j in range(m_ - 1):
        fs.append(bm.faces.new((hi_i[j], hi_i[j + 1], hi_o[j + 1], hi_o[j]))); fs.append(bm.faces.new((lo_i[j], lo_o[j], lo_o[j + 1], lo_i[j + 1])))
        fs.append(bm.faces.new((lo_i[j], lo_i[j + 1], hi_i[j + 1], hi_i[j]))); fs.append(bm.faces.new((lo_o[j], hi_o[j], hi_o[j + 1], lo_o[j + 1])))
    fs.append(bm.faces.new((lo_i[0], hi_i[0], hi_o[0], lo_o[0]))); fs.append(bm.faces.new((lo_i[-1], lo_o[-1], hi_o[-1], hi_i[-1])))
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
TZ = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cm/terrain_steps_cm.npz')['su_z']
ends = []
for k in range(NR):
    ztp = FLOOR - (k + 1) * RS; ok = zl < ztp + RS * 0.5
    if not ok[0]: break
    aend = float(al[np.argmin(ok)]) if not ok.all() else float(cum[-1])
    for j in (1, 2):   # keep the outer mitre from folding when a tread ends just past a turn
        if cum[j] < aend < cum[j] + 0.6: aend = float(cum[j] + 0.6)
    if aend < 0.6: break
    band(aend, k * TS - 0.025, (k + 1) * TS, 129.6, ztp, STEP)
    band(aend, k * TS - 0.025, k * TS + 0.03, ztp - 0.003, ztp + 0.0005, NOSE)
    # terrain clearance on the south segment (cm probe, rendered terrain)
    kk = (TZ[:, 1] > 6.1) & (TZ[:, 1] < 14.4) & (TZ[:, 0] > SB + k * TS + 0.05) & (TZ[:, 0] < SB + (k + 1) * TS - 0.05)
    ends.append((k, round(ztp, 3), round(aend, 2), round(float(TZ[kk, 2].max()) - ztp, 3) if kk.any() else None))
print('co treads (k, top, run end arc, S-seg terrain above top)', ends, 'total arc %.2f' % cum[-1], flush=True)
# ---------- 2c. plaza fill: cm's old top tread strip + wedge between cn E0 line and the new P1 line (MEASURED level 131.80)
boxsu(73.22, SB, 6.0, 14.5, 131.45, FLOOR, STEP)
tri = [E0, Q[1], E1]
top = [bm.verts.new(P3(*p, FLOOR)) for p in tri]; bot = [bm.verts.new(P3(*p, 131.45)) for p in tri]
fs = [bm.faces.new(top), bm.faces.new(bot[::-1])] + [bm.faces.new((bot[i], bot[(i + 1) % 3], top[(i + 1) % 3], top[i])) for i in range(3)]
bmesh.ops.recalc_face_normals(bm, faces=fs)
for f in fs: f.material_index = STEP
# ---------- 2d. cheek (u 5.6-6.0) + rails on the south segment
x0 = SB + (NR - 1) * TS; xt = SB
poly = [(x0 + 0.30, 129.80), (xt - 0.80, 129.80), (xt - 0.80, FLOOR + 0.30), (xt + 0.10, FLOOR + 0.30), (x0 + 0.05, 130.16 + 0.30 + RS), (x0 + 0.30, 130.16 + 0.30 + RS)]
a_ = [bm.verts.new(P3(s, 5.6, z)) for s, z in poly]; b_ = [bm.verts.new(P3(s, 6.0, z)) for s, z in poly]
fs = [bm.faces.new(a_), bm.faces.new(b_[::-1])] + [bm.faces.new((a_[(i + 1) % len(a_)], a_[i], b_[i], b_[(i + 1) % len(a_)])) for i in range(len(a_))]
for f in fs: f.material_index = ST
bmesh.ops.recalc_face_normals(bm, faces=fs)
def pipe(p0, p1, r, mat, seg=10):
    p0, p1 = Vector(p0), Vector(p1); ax = (p1 - p0).normalized(); t = ax.orthogonal().normalized(); b2 = ax.cross(t)
    lo = [bm.verts.new(p0 + r * (math.cos(2 * math.pi * i / seg) * t + math.sin(2 * math.pi * i / seg) * b2)) for i in range(seg)]
    hi_ = [bm.verts.new(v.co + (p1 - p0)) for v in lo]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi_)] + [bm.faces.new((lo[i], lo[(i + 1) % seg], hi_[(i + 1) % seg], hi_[i])) for i in range(seg)]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
zb_ = 130.16
for ur in (8.5, 12.0):
    p0 = P3(x0 + 0.30, ur, zb_ + 0.90); p1 = P3(x0, ur, zb_ + RS + 0.90); p2 = P3(xt, ur, FLOOR + 0.90); p3 = P3(xt - 0.35, ur, FLOOR + 0.90)
    pipe(p0, p1, 0.022, RLM); pipe(p1, p2, 0.022, RLM); pipe(p2, p3, 0.022, RLM)
    for tq in (0.0, 0.5, 1.0):
        sp = x0 + tq * (xt - x0); zt_ = zb_ + RS * (1 + tq * (NR - 1)); pipe(P3(sp, ur, zt_ - 0.05), P3(sp, ur, zt_ + 0.90), 0.02, RLM)
# ---------- 3. east loggia details: one ceiling downlight per bay (like the cl south arcade; Joe's level-4 photo shows lights in kind, east
# positions UNVERIFIED) + a barrel-tile edge course along the cn east eave (Commons photo: red barrel tile; tile pitch 0.26 m / radius 0.075 UNVERIFIED).
SCM, LENS = mi('Arcade_sconce_bronze_ck'), mi('Arcade_downlight_lens_cl')
# the roof tile material (slot 0) is driven by the 'roofc' attribute + normal z, so steep half-round sides render as stucco: own terracotta material
tm_ = bpy.data.materials.get('Kasser_tile_edge_terracotta_co') or bpy.data.materials.new('Kasser_tile_edge_terracotta_co'); tm_.use_nodes = True
pb_ = tm_.node_tree.nodes['Principled BSDF']; pb_.inputs['Base Color'].default_value = (0.38, 0.085, 0.05, 1); pb_.inputs['Roughness'].default_value = 0.72
if tm_.name not in [x.name if x else None for x in me.materials]: me.materials.append(tm_)
TILE = [x.name if x else None for x in me.materials].index(tm_.name)
frs, layout, DEPTH, WI, CEIL, zt = G['fr'], G['layout'], G['DEPTH'], G['WI'], G['CEIL'], G['zt']
def cylf(f_, a, w, z0, z1, r, mat, seg=16):
    c0 = [bm.verts.new(f_.V(a + r * math.cos(2 * math.pi * i / seg), w + r * math.sin(2 * math.pi * i / seg), z0)) for i in range(seg)]
    c1 = [bm.verts.new(f_.V(a + r * math.cos(2 * math.pi * i / seg), w + r * math.sin(2 * math.pi * i / seg), z1)) for i in range(seg)]
    fs = [bm.faces.new(c0), bm.faces.new(c1[::-1])] + [bm.faces.new((c0[i], c0[(i + 1) % seg], c1[(i + 1) % seg], c1[i])) for i in range(seg)]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
ndl = 0; ntile = 0; tn = math.tan(math.radians(8.5))
for k, f_ in frs.items():
    pl = layout[k]; nL = f_.L
    pw = [P] * len(pl) if k == 'D' else [(nL - OPEN) / 2] * 2
    for i in range(len(pl) - 1):
        ac_ = (pl[i] + pw[i] + pl[i + 1]) / 2; wc = (-DEPTH + WI) / 2
        cylf(f_, ac_, wc, CEIL - 0.05, CEIL, 0.09, SCM); cylf(f_, ac_, wc, CEIL - 0.055, CEIL - 0.05, 0.065, LENS); ndl += 1
    a0, a1 = (4.63, 22.93) if k == 'D' else (0.0, nL)
    ea0, ea1 = (a0, a1 + 0.30) if k == 'D' else (-0.30, a1)
    def ez(a, w): return zt(k, min(max(a, a0), a1)) + 0.01 - tn * w
    r = 0.075; w0, w1 = 0.30, 0.62
    for ac_ in np.arange(ea0 + 0.16, ea1 - 0.1, 0.26):
        rings = []
        for w in (w0, w1):
            zb = ez(ac_, w) - 0.01
            rings.append([bm.verts.new(f_.V(ac_ + r * math.cos(math.pi * j / 8), w, zb + r * 0.9 * math.sin(math.pi * j / 8))) for j in range(9)])
        A_, B_ = rings
        fs = [bm.faces.new(A_), bm.faces.new(B_[::-1])] + [bm.faces.new((A_[j], A_[j + 1], B_[j + 1], B_[j])) for j in range(8)] + [bm.faces.new((A_[8], A_[0], B_[0], B_[8]))]
        for f in fs: f.material_index = TILE
        bmesh.ops.recalc_face_normals(bm, faces=fs); ntile += 1
print('co loggia downlights', ndl, 'eave edge tiles', ntile, flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['co_windows_steps'] = 'co: curved-wall windows 1+2+2+2+1 over cn arches 2-4; one mitred step run SB %.2f -> E1 -> E2, R %.3f T %.3f' % (SB, RS, TS)
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('co 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b2).overlap(RBV)), flush=True); b2.free()
for nm, s, u, z, ts, tu, tz in (('wedge', 80.5, 10.5, 131.85, 73.0, 19.0, 130.9), ('wcl', 66.5, 26.0, 133.3, 55.0, 27.5, 138.8), ('eave', 64.0, 31.5, 133.9, 60.5, 27.0, 135.7)):
    L_ = P3(s, u, z); T_ = P3(ts, tu, tz); print('co CAM', nm, 'LOC=%.2f,%.2f,%.2f TGT=%.2f,%.2f,%.2f' % (*L_, *T_), flush=True)
print('co roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('co main: SAVED', flush=True)
