"""Session cn (Oct 20 ~12:45 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cm; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_frontsteps_rollup_20261019cm.py with SAVE 0 (-> cl -> ck -> cj -> ci2 -> ci -> ch -> cg -> cf), then:
 EAST LOGGIA (PD Commons east-facade photo refs/bt/MSU_Kasser_Theater_commons.jpg; PARALLEL_20261019_cm.md):
 The walls' east front is NOT on a constant s: the OSM footprint runs diagonally from (s 65.40, u 13.49) to (59.21, 35.57) (22.93 m, MEASURED
 footprint) and then along s ~59.2-59.4 to u 42.61 (7.04 m). Plaza floor 131.80 (LiDAR plateau 131.76-131.87, MEASURED); shed edge along the
 face 135.39 -> 136.09 (cj LiDAR fit, MEASURED). Built in a per-face frame (a along the face, w outward):
   face D (diagonal), a 4.63-22.93 (north of the SE-tower podium zone): 4 round arches on 5 white piers;
   face N (north return), a 0-7.04: the 5th arch (the photo's half-hidden right arch), stucco either side.
 Pier 0.80, opening (18.30 - 5*0.80)/4 = 3.575 m, springing 132.97, apex 134.76 (photo ratios: pier/opening ~0.22, springing ~1.2 m over the
 floor, apex ~0.6 m under the eave) = UNVERIFIED photo-scaled. No railings (photo). Open gallery depth 3.0 m (UNVERIFIED) with a flat white
 ceiling at 135.25 + transverse beams at every pier, concrete floor at 131.80 with joints on the pier lines, inner stucco wall with one dark
 glazed lobby storefront per bay (maroon frames; photo shows dark glazing behind the arches; sizes UNVERIFIED), closed end walls.
 Walls object: the face band above 131.80 in the arch span is bisected + deleted (generic shader windows go with it) and the walls' top cap
 (133.93) is cut out over the gallery; roof object: the stucco side faces 133.93 -> shed edge on those faces are replaced by the arcade skin.
 Plaza paving 131.80 continued 5 m out in front of both faces (LiDAR plateau, MEASURED level; extent UNVERIFIED).
All new geometry goes into the roof object's mesh (north picks it up through the Kasser link). 4a BVH printed vs the cf RHD npz (trees excluded)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_frontsteps_rollup_20261019cm.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
FLOOR = 131.80; P = 0.80; NBD = 4; DEPTH = float(os.environ.get('DEPTH', '3.0')); CEIL = 135.25
FACES = {'D': ((65.40, 13.49), (59.21, 35.57), 4.63, 22.93), 'N': ((59.21, 35.57), (59.44, 42.61), 0.0, None)}
OPEN = (22.93 - 4.63 - (NBD + 1) * P) / NBD; R = OPEN / 2; ZS = 134.76 - R; APEX = ZS + R
print('cn loggia: open %.3f R %.3f springing %.2f apex %.2f depth %.1f' % (OPEN, R, ZS, APEX, DEPTH), flush=True)
class Fr:
    def __init__(s_, p0, p1):
        s_.p0 = np.array(p0); v = np.array(p1) - s_.p0; s_.L = float(np.linalg.norm(v)); s_.t = v / s_.L; nn = np.array([s_.t[1], -s_.t[0]])
        s_.nn = nn if nn[0] > 0 else -nn
    def SU(s_, a, w): return s_.p0 + s_.t * a + s_.nn * w
    def V(s_, a, w, z): q = xy(*s_.SU(a, w)); return Vector((q[0], q[1], z))
    def aw(s_, co): q = np.array(su(co)) - s_.p0; return float(q @ s_.t), float(q @ s_.nn)
    def nworld(s_):   # outward normal in world xy
        q = n * s_.nn[0] + d * s_.nn[1]; return Vector((q[0], q[1], 0))
    def tworld(s_):
        q = n * s_.t[0] + d * s_.t[1]; return Vector((q[0], q[1], 0))
fr = {k: Fr(v[0], v[1]) for k, v in FACES.items()}
for k, f_ in fr.items(): print('cn face', k, 'L %.2f' % f_.L, flush=True)
spans = {'D': (4.63, 22.93), 'N': (0.0, fr['N'].L)}
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']; wm = wo.matrix_world
if 'cn_east_loggia' in ro.keys(): print('cn WARNING: already applied (chain should have rebuilt)', flush=True)
# ---------- 1. walls: delete the face band above FLOOR in the spans + cut the top cap over the galleries
bm = bmesh.new(); bm.from_mesh(wo.data); bm.transform(wm)
def bis(bm_, co, no, geom):
    g = list({e for f in geom for e in f.edges}) + list(geom) + list({v for f in geom for v in f.verts})
    bmesh.ops.bisect_plane(bm_, geom=g, dist=1e-4, plane_co=Vector(co), plane_no=Vector(no))
for k, f_ in fr.items():
    a0, a1 = spans[k]
    def onface(f): a, w = f_.aw(f.calc_center_median()); return abs(w) < 0.05 and -0.5 < a < f_.L + 0.5 and abs(f.normal.z) < 0.3
    for aa in (a0, a1): bis(bm, f_.V(aa, 0, 0), f_.tworld(), [f for f in bm.faces if onface(f)])
    bis(bm, (0, 0, FLOOR), (0, 0, 1), [f for f in bm.faces if onface(f)])
    dele = [f for f in bm.faces if onface(f) and a0 - 0.01 < f_.aw(f.calc_center_median())[0] < a1 + 0.01 and min(v.co.z for v in f.verts) > FLOOR - 0.005]
    print('cn walls face band deleted', k, len(dele), flush=True); bmesh.ops.delete(bm, geom=dele, context='FACES')
    def incap(f): a, w = f_.aw(f.calc_center_median()); return abs(f.normal.z) > 0.9 and f.calc_center_median().z > FLOOR and -DEPTH - 1.0 < w < 0.5 and a0 - 1.0 < a < a1 + 1.0
    for co, no in ((f_.V(a0, 0, 0), f_.tworld()), (f_.V(a1, 0, 0), f_.tworld()), (f_.V(0, -DEPTH, 0), f_.nworld())):
        bis(bm, co, no, [f for f in bm.faces if incap(f)])
    dele = [f for f in bm.faces if abs(f.normal.z) > 0.9 and f.calc_center_median().z > FLOOR and (lambda aw_: a0 < aw_[0] < a1 and -DEPTH < aw_[1] < 0.01)(f_.aw(f.calc_center_median()))]
    print('cn walls cap pieces deleted', k, len(dele), flush=True); bmesh.ops.delete(bm, geom=dele, context='FACES')
bm.transform(wm.inverted()); bm.to_mesh(wo.data); bm.free(); wo.data.update()
# ---------- 2. roof mesh: delete the stucco side faces on the faces in the spans; build the loggia
names = [x.name if x else None for x in me.materials]
def mi(nm): return names.index(nm)
ST, CE, FL, JT, GL, FR = mi('Arcade_stucco_white_ck'), mi('Arcade_ceiling_white_ck'), mi('Arcade_concrete_floor_ck'), mi('Arcade_joint_dark_ck'), mi('Kasser_window_glass_cj'), mi('Kasser_window_frame_maroon_cj')
STEP = mi('Kasser_step_concrete_cm')
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
ztop = {}
for k, f_ in fr.items():
    a0, a1 = spans[k]
    side = [f for f in bm.faces if abs(f.normal.z) < 0.3 and (lambda aw_: abs(aw_[1]) < 0.05 and a0 - 0.01 < aw_[0] < a1 + 0.01)(f_.aw(f.calc_center_median())) and f.material_index == 3 and min(v.co.z for v in f.verts) > 133.8]
    pts = sorted((f_.aw(v.co)[0], v.co.z) for f in side for v in f.verts if v.co.z > 134.5)
    ztop[k] = np.array(pts) if pts else np.array([(a0, 135.4), (a1, 135.4)])
    print('cn roof side faces deleted', k, len(side), 'edge z %.2f..%.2f' % (ztop[k][:, 1].min(), ztop[k][:, 1].max()), flush=True)
    bmesh.ops.delete(bm, geom=side, context='FACES')
def zt(k, a): return float(np.interp(a, ztop[k][:, 0], ztop[k][:, 1]))
nf0 = len(bm.faces)
def box(f_, a0, a1, w0, w1, z0, z1, mat):
    c = [(a0, w0), (a1, w0), (a1, w1), (a0, w1)]
    lo = [bm.verts.new(f_.V(a, w, z0)) for a, w in c]; hi = [bm.verts.new(f_.V(a, w, z1)) for a, w in c]
    fs = [bm.faces.new(lo), bm.faces.new(hi)] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i])) for i in range(4)]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
def prism_az(f_, poly, w0, w1, mat):
    a_ = [bm.verts.new(f_.V(a, w0, z)) for a, z in poly]; b_ = [bm.verts.new(f_.V(a, w1, z)) for a, z in poly]
    fs = [bm.faces.new(a_), bm.faces.new(b_[::-1])] + [bm.faces.new((a_[(i + 1) % len(a_)], a_[i], b_[i], b_[(i + 1) % len(a_)])) for i in range(len(a_))]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
WO, WI = 0.0, -0.60   # arcade skin depth (outer face on the old wall plane)
layout = {'D': [4.63 + i * (OPEN + P) for i in range(NBD + 1)]}
nL = fr['N'].L; side_ = (nL - OPEN) / 2
layout['N'] = [0.0, side_ + OPEN]   # two wide stucco piers, one arch
for k, f_ in fr.items():
    a0, a1 = spans[k]; pl = layout[k]
    pw = [P] * len(pl) if k == 'D' else [side_, side_]
    opens = [(pl[i] + pw[i], pl[i + 1]) for i in range(len(pl) - 1)]
    for p_, w_ in zip(pl, pw):
        box(f_, p_, p_ + w_, WI, WO, FLOOR - 0.40, zt(k, p_ + w_ / 2) - 0.005, ST)
        box(f_, p_ - 0.02, p_ + w_ + 0.02, WI - 0.02, WO + 0.02, ZS - 0.12, ZS, ST)     # impost band (UNVERIFIED)
        box(f_, p_ - 0.03, p_ + w_ + 0.03, WI - 0.03, WO + 0.03, FLOOR, FLOOR + 0.15, ST)  # plinth
    for sL, sR in opens:
        sc_ = (sL + sR) / 2; r_ = (sR - sL) / 2
        arc = [(sc_ - r_ * math.cos(math.pi * j / 24), ZS + r_ * math.sin(math.pi * j / 24)) for j in range(25)]
        prism_az(f_, [(sR, zt(k, sR) - 0.005), (sL, zt(k, sL) - 0.005)] + arc, WI, WO, ST)
    # gallery: floor, ceiling + beams, inner wall + storefronts, end walls
    box(f_, a0, a1, -DEPTH, WO, FLOOR - 0.35, FLOOR, FL)
    for p_, w_ in zip(pl, pw):
        for jx in (p_, p_ + w_): box(f_, jx - 0.006, jx + 0.006, -DEPTH, WI, FLOOR, FLOOR + 0.003, JT)
        box(f_, p_ + w_ / 2 - 0.13, p_ + w_ / 2 + 0.13, -DEPTH, WI, CEIL - 0.28, CEIL, CE)                     # transverse beam per pier
    box(f_, a0, a1, -DEPTH, WI, CEIL, CEIL + 0.12, CE)
    box(f_, a0, a1, -DEPTH - 0.30, -DEPTH, FLOOR - 0.35, CEIL + 0.12, ST)                                       # inner wall
    box(f_, a0 - 0.30, a0 + 0.05, -DEPTH, WI, FLOOR - 0.35, CEIL + 0.12, ST); box(f_, a1 - 0.05, a1 + 0.30, -DEPTH, WI, FLOOR - 0.35, CEIL + 0.12, ST)
    for sL, sR in opens:   # dark glazed lobby storefront per bay (photo: dark glazing behind the arches; sizes UNVERIFIED)
        g0, g1 = sL + 0.35, sR - 0.35; zh = FLOOR + 2.70
        box(f_, g0 - 0.08, g1 + 0.08, -DEPTH + 0.00, -DEPTH + 0.06, FLOOR, zh + 0.08, FR)
        box(f_, g0, g1, -DEPTH + 0.01, -DEPTH + 0.065, FLOOR + 0.06, zh, GL)
        nm_ = 3 if (g1 - g0) > 2.2 else 2
        for j in range(1, nm_): xm = g0 + (g1 - g0) * j / nm_; box(f_, xm - 0.035, xm + 0.035, -DEPTH + 0.01, -DEPTH + 0.08, FLOOR, zh, FR)
        box(f_, g0, g1, -DEPTH + 0.01, -DEPTH + 0.08, FLOOR + 2.15, FLOOR + 2.22, FR)    # transom bar
    # T1 fix: tile eave continued 0.6 m beyond the face on the shed plane (8.5 deg, cj fit) like the cj south eave (photo shows the
    # red-tile shed projecting over the arches); top tile, soffit under, maroon fascia (one red, cm). Overhang UNVERIFIED.
    OV = 0.6; tn = math.tan(math.radians(8.5)); ea0 = a0 if k == 'D' else -0.30
    def ez(a, w): return zt(k, min(max(a, a0), a1)) + 0.01 - tn * w
    c4 = [(ea0, -0.05), (a1 + (0.30 if k == 'D' else 0.0), -0.05), (a1 + (0.30 if k == 'D' else 0.0), OV), (ea0, OV)]
    hi = [bm.verts.new(f_.V(a, w, ez(a, w))) for a, w in c4]; lo = [bm.verts.new(f_.V(a, w, ez(a, w) - 0.18)) for a, w in c4]
    fs = [bm.faces.new(hi), bm.faces.new(lo[::-1])] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i])) for i in range(4)]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    for f in fs: f.material_index = 0 if f.normal.z > 0.2 else (1 if f.normal.z < -0.2 else FR)
# ---------- 3. plaza + diagonal front steps (T1 fix: the 5 m slab floated over the falling grade). LiDAR plateau 131.76-131.87 ends on a line
# from the cm flight B top corner (s 73.2, u 14.5) to ~1.9 m off the face D north end, then ~1.0 m off face N (MEASURED, 1 m bins); below it the
# grade falls to 130.4 (south) .. 131.4 (north). Steps descend outward from that edge (R 0.164 / T 0.345 like cm flight B), each tread only
# where the measured lower grade is below it, so the flight tapers out to the north (photo: steps the full width of the east front).
zpt = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); gx, gy, gz_, gc = zpt['x'], zpt['y'], zpt['z'], zpt['c']
gk = (gc == 1) | (gc == 2); GSn = (gx[gk] - A[0]) * n[0] + (gy[gk] - A[1]) * n[1]; GUn = (gx[gk] - A[0]) * d[0] + (gy[gk] - A[1]) * d[1]; GZn = gz_[gk]
E0 = (73.20, 14.50); E1 = tuple(fr['D'].SU(22.93, 1.90)); E2 = tuple(fr['N'].SU(7.04, 1.00))
Fd, Fn = fr['D'], fr['N']
poly = [tuple(Fd.SU(1.05, 0.0)), E0, E1, E2, tuple(Fn.SU(7.04, 0.0)), tuple(Fd.SU(22.93, 0.0))]
top = [bm.verts.new((*xy(s_, u_), FLOOR)) for s_, u_ in poly]; bot = [bm.verts.new((*xy(s_, u_), 130.0)) for s_, u_ in poly]
fs = [bm.faces.new(top), bm.faces.new(bot[::-1])] + [bm.faces.new((bot[i], bot[(i + 1) % len(poly)], top[(i + 1) % len(poly)], top[i])) for i in range(len(poly))]
bmesh.ops.recalc_face_normals(bm, faces=fs)
for f in fs: f.material_index = STEP
RS, TS = 0.164, 0.345
for si, sg in enumerate((Fr(E0, E1), Fr(E1, E2))):
    al = np.arange(0, sg.L + 1e-6, 0.5); zl = []
    for a in al:
        q = np.stack([GSn, GUn], 1) - sg.p0; aa = q @ sg.t; ww = q @ sg.nn
        kk = (np.abs(aa - a) < 1.0) & (ww > 2.5) & (ww < 4.5); zl.append(float(np.median(GZn[kk])) if kk.sum() > 3 else 131.8)
    zl = np.array(zl); nst = 0
    for kq in range(10):
        ztp = FLOOR - (kq + 1) * RS
        ok = zl < ztp + RS * 0.5
        if not ok[0]: break
        aend = al[np.argmin(ok)] if not ok.all() else sg.L
        if aend < 0.6: break
        # final fix: overlap the two runs 0.9 m at their shared corner E1 (the 16 deg turn left a dark crack between them in the north view)
        ea = aend + 0.9 if (si == 0 and aend >= sg.L - 1e-6) else aend; sa = -0.9 if si == 1 else 0.0
        box(sg, sa, ea, kq * TS - 0.025, (kq + 1) * TS, 129.6, ztp, STEP); nst += 1
        box(sg, sa, ea, kq * TS - 0.025, kq * TS + 0.03, ztp - 0.003, ztp + 0.0005, mi('Kasser_step_nosing_cm'))
    print('cn diagonal steps seg L %.2f treads %d lower grade %.2f..%.2f' % (sg.L, nst, zl.min(), zl.max()), flush=True)
# ---------- 4. SE tower (Commons east photo, PARALLEL cm): lantern ribbon of 2x2-light windows under the cap on every face, a thin maroon band
# at the shaft top, a 2-storey corner-ish curtain window (2 x 4 lights) on the E face above the podium, 2 small square windows, timber-style
# maroon brackets (3 per face) under the cap, a thicker maroon fascia. Shaft s 47.57-57.00 / u 7.63-16.95, podium 141.09, cap underside 149.16,
# fascia 149.16-149.51, cap overhang 1.0 m (cj, MEASURED/LiDAR-fit). Every window/bracket size + position here is photo-scaled = UNVERIFIED.
class FF:   # a shaft face: line p0->p1 in (s, u), explicit outward normal o
    def __init__(s_, p0, p1, o):
        s_.p0 = np.array(p0, float); v = np.array(p1, float) - s_.p0; s_.L = float(np.linalg.norm(v)); s_.t = v / s_.L; s_.nn = np.array(o, float)
    def V(s_, a, w, z): q = xy(*(s_.p0 + s_.t * a + s_.nn * w)); return Vector((q[0], q[1], z))
TS0, TS1, TU0, TU1 = 47.57, 57.00, 7.63, 16.95; ZP, ZC = 141.09, 149.16
TF = {'E': FF((TS1, TU0), (TS1, TU1), (1, 0)), 'W': FF((TS0, TU1), (TS0, TU0), (-1, 0)), 'N': FF((TS1, TU1), (TS0, TU1), (0, 1)), 'S': FF((TS0, TU0), (TS1, TU0), (0, -1))}
def winf(f_, c, wd, z0, z1, nx, nz):
    box(f_, c - wd / 2, c + wd / 2, -0.01, 0.06, z0, z1, FR); box(f_, c - wd / 2 + 0.08, c + wd / 2 - 0.08, -0.01, 0.075, z0 + 0.08, z1 - 0.08, GL)
    for j in range(1, nx): x_ = c - wd / 2 + wd * j / nx; box(f_, x_ - 0.04, x_ + 0.04, -0.01, 0.09, z0, z1, FR)
    for j in range(1, nz): z_ = z0 + (z1 - z0) * j / nz; box(f_, c - wd / 2, c + wd / 2, -0.01, 0.09, z_ - 0.04, z_ + 0.04, FR)
ntw = len(bm.faces)
for k, f_ in TF.items():
    L_ = f_.L
    box(f_, -0.05, L_ + 0.05, -0.01, 0.05, 146.70, 146.86, FR)                                   # thin maroon band at the shaft top
    for c in (L_ * 0.30, L_ * 0.70): winf(f_, c, 1.9, 147.05, 148.85, 2, 2)                        # lantern ribbon, 2 x (2x2 lights)
    for c in (L_ * 0.2, L_ * 0.5, L_ * 0.8):                                                         # brackets under the 1.0 m overhang
        box(f_, c - 0.10, c + 0.10, -0.01, 0.22, 148.20, ZC - 0.005, FR)                             # post on the wall
        box(f_, c - 0.10, c + 0.10, 0.0, 0.92, ZC - 0.24, ZC - 0.005, FR)                            # arm under the soffit
        pa, pb = f_.V(c, 0.20, 148.35), f_.V(c, 0.80, ZC - 0.22)                                     # diagonal brace (thin box along the strut)
        ax = (pb - pa); ln = ax.length; axn = ax.normalized(); sd = f_.V(c + 0.07, 0, 0) - f_.V(c, 0, 0); sd.z = 0; up = axn.cross(sd).normalized() * 0.07
        cs = [pa - sd - up, pa + sd - up, pa + sd + up, pa - sd + up]; ce = [v + ax for v in cs]
        vv = [bm.verts.new(v) for v in cs + ce]
        fs = [bm.faces.new(vv[0:4]), bm.faces.new(vv[4:8][::-1])] + [bm.faces.new((vv[i], vv[(i + 1) % 4], vv[4 + (i + 1) % 4], vv[4 + i])) for i in range(4)]
        bmesh.ops.recalc_face_normals(bm, faces=fs)
        for f in fs: f.material_index = FR
for k, f_ in {'E': FF((58.0, 6.63), (58.0, 17.95), (1, 0)), 'W': FF((46.57, 17.95), (46.57, 6.63), (-1, 0)), 'N': FF((58.0, 17.95), (46.57, 17.95), (0, 1)), 'S': FF((46.57, 6.63), (58.0, 6.63), (0, -1))}.items():
    box(f_, -0.04, f_.L + 0.04, -0.20, 0.03, 148.96, ZC + 0.02, FR)                                  # thicker fascia (photo: deep maroon band)
fe = TF['E']; winf(fe, fe.L * 0.42, 3.6, 141.45, 145.65, 2, 4)                                         # E face curtain window above the podium roof
winf(fe, fe.L * 0.82, 0.9, 144.60, 145.50, 1, 1)                                                       # small square right of it
fsn = TF['S']; winf(fsn, fsn.L * 0.70, 0.9, 144.60, 145.50, 1, 1)                                      # small square high on the S face
print('cn SE tower faces added', len(bm.faces) - ntw, flush=True)
print('cn faces added', len(bm.faces) - nf0, flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['cn_east_loggia'] = 'cn: east loggia 4 arches (face D a 4.63-22.93) + 1 (face N), open %.3f, spring %.2f, apex %.2f, floor %.2f, depth %.1f' % (OPEN, ZS, APEX, FLOOR, DEPTH)
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('cn 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b2).overlap(RBV)), flush=True); b2.free()
# camera helper coords (deck-frame faces -> world), printed for the render script
for k, a, w, z, ta, tw, tz in (('loggia', 7.0, 8.5, 133.45, 16.0, 0.0, 133.5), ('larch', 10.0, 3.2, 133.30, 13.6, -2.0, 133.7), ('lgal', 4.9, -1.6, 133.45, 22.0, -1.3, 133.2)):
    f_ = fr['D']; L_ = f_.V(a, w, z); T_ = f_.V(ta, tw, tz); print('cn CAM', k, 'LOC=%.2f,%.2f,%.2f TGT=%.2f,%.2f,%.2f' % (*L_, *T_), flush=True)
print('cn roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cn main: SAVED', flush=True)
