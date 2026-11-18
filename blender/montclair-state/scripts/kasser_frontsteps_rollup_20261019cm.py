"""Session cm (Oct 19 ~11:30 PM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cl; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_setback_fullarcade_20261019cl.py with SAVE 0 (-> ck -> cj -> ci2 -> ci -> ch -> cg -> cf), then:
 1. FRONT STEPS (LiDAR class 1/2, 0.25-0.5 m bins, MEASURED rises):
    A. south flight: street 128.72 (s < 60.8) -> landing 130.24 (s > 64), u -4.35..0.95, 9 risers (0.169) x 0.33 treads, climbing +s;
       stair placed so its inner-corner line stays >= the LiDAR profile + 2 cm (shift vs the LiDAR mid printed). Stucco cheek walls:
       south u -4.75..-4.35 (sloped top, UNVERIFIED), north = the terrace-edge wall u 0.95..1.9, top 132.11 (MEASURED 132.08-132.11, s 62-70).
       Maroon pipe handrails both sides = code-required PLACEHOLDER, UNVERIFIED (this flight is out of frame in the Commons photo; style copied
       from the photo's front-step rails).
    B. east front steps: plaza 131.77 (s < 72.5) -> lower walk 130.16 (s > 76), u 6.0..14.5, 10 risers (0.161) x 0.345, descending +s;
       south cheek u 5.6..6.0 (sloped top, UNVERIFIED); north end left open (LiDAR edge turns diagonal NW beyond u 15, not modelled). Two maroon
       pipe rails at u 8.5 / 12.0 (the Commons east photo shows maroon rails at intervals on the long front steps; positions UNVERIFIED).
       Plaza paving at 131.80 from the walls' east face (s ~65.2) to the top step, 1.5 m joints (UNVERIFIED).
    Landing slab 130.25 s 63.4-68.0 under the flight A top.
 2. Under the arcade west end (News12 photo): stucco cover panel over the generic ground-floor window grid s 1.85-9.25 (to pier 3's east edge),
    people door (0.9 x 2.2) + roll-up door (4.2 x 3.4, ribbed) + concrete apron; sizes photo-scaled UNVERIFIED. Corner panel s 51.45-53.10 hides
    the clipped window beside the terrace retaining face.
 3. One eave red: every roof-mesh face on the cj fascia slot (brown) -> the maroon trim/frame slot (photos show one dark red). Downpipe (light
    grey, News12) at s 1.74 between the RHD SE core gap and the arcade west end.
All geometry goes into the roof object's mesh (north picks it up through the Kasser link). 4a BVH printed vs the cf RHD npz (trees excluded)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_setback_fullarcade_20261019cl.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
def P3(s, u, z): q = xy(s, u); return Vector((q[0], q[1], z))
z = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); px, py, pz, pc = z['x'], z['y'], z['z'], z['c']
g = ((pc == 1) | (pc == 2)) & (px > -270) & (px < -150) & (py > -110) & (py < 0)
GS = (px[g] - A[0]) * n[0] + (py[g] - A[1]) * n[1]; GU = (px[g] - A[0]) * d[0] + (py[g] - A[1]) * d[1]; GZ = pz[g]
def prof(s0, s1, u0, u1, step=0.25):
    out = []
    for s in np.arange(s0, s1, step):
        k = (GS >= s) & (GS < s + step) & (GU >= u0) & (GU < u1)
        if k.sum() > 2: out.append((s + step / 2, float(np.median(GZ[k]))))
    return np.array(out)
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']; wm = wo.matrix_world
names = [x.name if x else None for x in me.materials]
FR, FAS, STU = names.index('Kasser_window_frame_maroon_cj'), 2, 3
FLM = names.index('Arcade_concrete_floor_ck'); ARC_ST = names.index('Arcade_stucco_white_ck'); RLM = names.index('Arcade_rail_maroon_ck')
JTM = names.index('Arcade_joint_dark_ck'); DFR = names.index('Arcade_door_frame_white_ck')
def mk(name, col, rough, metal=0.0, bump=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if m.name not in [x.name if x else None for x in me.materials]: me.materials.append(m)
    return [x.name if x else None for x in me.materials].index(m.name)
STEP = mk('Kasser_step_concrete_cm', (0.50, 0.49, 0.46), 0.85)
NOSE = mk('Kasser_step_nosing_cm', (0.42, 0.41, 0.39), 0.8)
ROLL = mk('Kasser_rollup_door_cm', (0.80, 0.80, 0.78), 0.45, 0.3)
PDOOR = mk('Kasser_people_door_cm', (0.82, 0.82, 0.80), 0.4, 0.1)
PIPE = mk('Kasser_downpipe_grey_cm', (0.62, 0.62, 0.60), 0.45, 0.4)
APR = mk('Kasser_apron_concrete_cm', (0.47, 0.46, 0.44), 0.9)
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
# ---- 3a. one eave red
nf = 0
print('cm roof slots', list(enumerate(names)), flush=True)
for f in bm.faces:
    if f.material_index == FAS: f.material_index = FR; nf += 1
print('cm fascia faces -> maroon', nf, flush=True)
def box(s0, s1, u0, u1, z0, z1, mat):
    if s1 < s0: s0, s1 = s1, s0
    c = [(s0, u0), (s1, u0), (s1, u1), (s0, u1)]
    lo = [bm.verts.new(P3(s, u, z0)) for s, u in c]; hi_ = [bm.verts.new(P3(s, u, z1)) for s, u in c]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi_)] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi_[(i + 1) % 4], hi_[i])) for i in range(4)]
    for f in fs: f.material_index = mat
    return fs
def prism_sz(poly, u0, u1, mat):   # convex polygon in (s, z), extruded u0..u1
    a = [bm.verts.new(P3(s, u0, zz)) for s, zz in poly]; b = [bm.verts.new(P3(s, u1, zz)) for s, zz in poly]
    fs = [bm.faces.new(a), bm.faces.new(b[::-1])] + [bm.faces.new((a[(i + 1) % len(a)], a[i], b[i], b[(i + 1) % len(a)])) for i in range(len(a))]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
def pipe(p0, p1, r, mat, seg=10):
    p0, p1 = Vector(p0), Vector(p1); ax = (p1 - p0).normalized(); t = ax.orthogonal().normalized(); b2 = ax.cross(t)
    lo = [bm.verts.new(p0 + r * (math.cos(2 * math.pi * i / seg) * t + math.sin(2 * math.pi * i / seg) * b2)) for i in range(seg)]
    hi_ = [bm.verts.new(v.co + (p1 - p0)) for v in lo]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi_)] + [bm.faces.new((lo[i], lo[(i + 1) % seg], hi_[(i + 1) % seg], hi_[i])) for i in range(seg)]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
nf0 = len(bm.faces)
# ---- 1. flights
def prof_max(s0, s1, bands, step=0.25):
    # per-u-band medians, then the MAX per s bin: the LiDAR rise is skewed (earlier on the north side of flight A), so fitting the all-band
    # median let the 1 m terrain poke ~0.27 m through the north half (cm test T2, ray probe at s 62 / u 0.5: terrain 129.50 vs stair 129.23)
    ps = [dict((round(s, 3), zz) for s, zz in prof(s0, s1, a, b, step)) for a, b in bands]
    keys = sorted(set().union(*[set(p.keys()) for p in ps]))
    return np.array([(k, max(p[k] for p in ps if k in p)) for k in keys])
TN = '/workspace/nj-scenes/montclair-state/north/data/day_heroes/cm/terrain_steps_cm.npz'   # north/scripts/probe_terrain_kasser_steps_20261019cm.py (read-only)
TZ = np.load(TN)['su_z'] if os.path.exists(TN) else None
def with_terrain(pr, u0, u1):
    # the north 1 m terrain (bz ext) is smoother than the LiDAR and rises ~0.5 m earlier on flight A's north side: fit to max(LiDAR, rendered terrain)
    if TZ is None: return pr
    out = []
    for s, zz in pr:
        k = (np.abs(TZ[:, 0] - s) <= 0.13) & (TZ[:, 1] >= u0) & (TZ[:, 1] <= u1)
        out.append((s, max(zz, float(TZ[k, 2].max())) if k.any() else zz))
    return np.array(out)
def fit_flight(pr, zb, zt, nR, T, sdir, x_guess):
    """x0 = s of the bottom riser. Stair surface at s (distance t=(s-x0)*sdir from the bottom riser): zb for t<0, zb+(k+1)R for k*T<=t<(k+1)T (k<nR-1), zt beyond.
    Pick the x0 nearest the LiDAR-mid guess with stair_surface >= profile + 0.02 everywhere (inner corners clear the terrain)."""
    R = (zt - zb) / nR
    def surf(s, x0):
        t = (s - x0) * sdir
        if t < 0: return zb
        k = int(t // T)
        return zt if k >= nR - 1 else zb + (k + 1) * R
    best = None
    for dx in np.arange(0, 1.5, 0.01):
        x0 = x_guess - sdir * dx
        tt = [(s, zz) for s, zz in pr if 0 <= (s - x0) * sdir <= (nR - 1) * T]
        viol = max(zz + 0.01 - surf(s, x0) for s, zz in tt)
        if viol <= 0: best = x0; break
    if best is None: best = x_guess - sdir * 0.6
    tt = [(s, zz) for s, zz in pr if 0 <= (s - best) * sdir <= (nR - 1) * T]
    print('cm fit: max LiDAR above stair %.3f, max stair above LiDAR %.3f' % (max(zz - surf(s, best) for s, zz in tt), max(surf(s, best) - zz for s, zz in tt)), flush=True)
    return best, R
def build_flight(x0, sdir, nR, R, T, zb, u0, u1, base):
    for k in range(nR):
        sa = x0 + sdir * k * T; sb = x0 + sdir * ((k + 1) * T if k < nR - 1 else (k * T + 0.40))
        ztop = zb + (k + 1) * R
        box(sa, sb, u0, u1, base, ztop - 0.04, STEP)
        box(sa - sdir * 0.025, sb, u0, u1, ztop - 0.04, ztop, NOSE if k < nR - 1 else STEP)   # precast tread with 25 mm nosing
    return x0 + sdir * (nR - 1) * T
# A. south flight (climbs +s)
prA = prof_max(59.0, 66.0, [(-4.0, -2.0), (-2.0, 0.0), (0.0, 0.95)]); prA_l = prA.copy(); prA = with_terrain(prA, -4.35, 0.95); zbA, ztA, nRA, TA = 128.72, 130.24, 9, 0.33
midA = float(np.interp((zbA + ztA) / 2, prA_l[:, 1], prA_l[:, 0])); guessA = midA - (nRA - 1) * TA / 2
x0A, RA = fit_flight(prA, zbA, ztA, nRA, TA, +1, guessA)
xtA = build_flight(x0A, +1, nRA, RA, TA, zbA, -4.35, 0.95, 128.35)
print('cm flight A: LiDAR mid %.2f, bottom riser s %.2f (guess %.2f, shift %.2f), top riser %.2f, R %.3f T %.2f' % (midA, x0A, guessA, x0A - guessA, xtA, RA, TA), flush=True)
# landing slab at the top of A
box(xtA + 0.39, 68.0, -4.75, 0.95, 129.80, 130.25, STEP)
# cheek walls A: south sloped (nosing line + 0.30), north = terrace-edge wall (MEASURED top 132.11)
prism_sz([(x0A - 0.30, 128.35), (68.0, 128.35), (68.0, ztA + 0.30), (xtA + 0.30, ztA + 0.30), (x0A - 0.05, zbA + 0.30 + RA), (x0A - 0.30, zbA + 0.30 + RA)], -4.75, -4.35, ARC_ST)
box(x0A - 0.30, 71.0, 0.95, 1.90, 128.35, 132.07, ARC_ST); box(x0A - 0.33, 71.03, 0.92, 1.93, 132.07, 132.11, ARC_ST)
# handrails A (maroon pipe, 0.90 over the nosing line, 0.15 m in from each cheek)
for ur in (-4.20, 0.80):
    p0 = P3(x0A - 0.30, ur, zbA + 0.90); p1 = P3(x0A, ur, zbA + RA + 0.90 - 0.0); p2 = P3(xtA, ur, ztA + 0.90); p3 = P3(xtA + 0.35, ur, ztA + 0.90)
    pipe(p0, p1, 0.022, RLM); pipe(p1, p2, 0.022, RLM); pipe(p2, p3, 0.022, RLM)
    for t in (0.0, 0.5, 1.0):
        sp = x0A + t * (xtA - x0A); zt_ = zbA + RA * (1 + t * (nRA - 1)); pipe(P3(sp, ur, zt_ - 0.05), P3(sp, ur, zt_ + 0.90), 0.02, RLM)
# B. east front steps (descend +s): parametrise from the bottom (street side) climbing -s
prB = prof_max(70.5, 78.5, [(6.0, 9.0), (9.0, 12.0), (12.0, 14.5)]); prB = with_terrain(prB, 6.0, 14.5); zbB, ztB, nRB, TB = 130.16, 131.80, 10, 0.345
midB = float(np.interp((zbB + ztB) / 2, prB[::-1, 1], prB[::-1, 0])); guessB = midB + (nRB - 1) * TB / 2
x0B, RB_ = fit_flight(prB, zbB, ztB, nRB, TB, -1, guessB)
xtB = build_flight(x0B, -1, nRB, RB_, TB, zbB, 6.0, 14.5, 129.80)
print('cm flight B: LiDAR mid %.2f, bottom riser s %.2f (guess %.2f, shift %.2f), top riser %.2f, R %.3f T %.3f' % (midB, x0B, guessB, x0B - guessB, xtB, RB_, TB), flush=True)
# rails on B: the Commons east photo shows maroon pipe rails at intervals on the long front steps (positions UNVERIFIED)
for ur in (8.5, 12.0):
    p0 = P3(x0B + 0.30, ur, zbB + 0.90); p1 = P3(x0B, ur, zbB + RB_ + 0.90); p2 = P3(xtB, ur, ztB + 0.90); p3 = P3(xtB - 0.35, ur, ztB + 0.90)
    pipe(p0, p1, 0.022, RLM); pipe(p1, p2, 0.022, RLM); pipe(p2, p3, 0.022, RLM)
    for tq in (0.0, 0.5, 1.0):
        sp = x0B + tq * (xtB - x0B); zt_ = zbB + RB_ * (1 + tq * (nRB - 1)); pipe(P3(sp, ur, zt_ - 0.05), P3(sp, ur, zt_ + 0.90), 0.02, RLM)
# plaza paving at the top of B (LiDAR plateau 131.76-131.87, MEASURED) from the walls' east face to the top step; 1.5 m joints UNVERIFIED
se = []
for f in wo.data.polygons:
    c = wm @ f.center; s, u = su(c); nw = (wm.to_3x3() @ f.normal)
    if 6 < u < 14.5 and 131.9 < c.z < 136 and abs(nw.x * n[0] + nw.y * n[1]) > 0.9 and 55 < s < xtB: se.append(s)
SE_ = max(se) if se else 66.0; print('cm walls east face s at u 6-14.5', round(SE_, 2), len(se), flush=True)
box(SE_ - 0.05, xtB - 0.40, 6.0, 14.5, 131.45, ztB, STEP)
for js in np.arange(xtB - 0.40 - 1.5, SE_, -1.5): box(js - 0.006, js + 0.006, 6.0, 14.5, ztB, ztB + 0.003, JTM)
for ju in np.arange(7.5, 14.5, 1.5): box(SE_, xtB - 0.40, ju - 0.006, ju + 0.006, ztB, ztB + 0.003, JTM)
prism_sz([(x0B + 0.30, 129.80), (xtB - 0.80, 129.80), (xtB - 0.80, ztB + 0.30), (xtB - 0.30, ztB + 0.30), (x0B + 0.05, zbB + 0.30 + RB_), (x0B + 0.30, zbB + 0.30 + RB_)], 5.6, 6.0, ARC_ST)
# ---- 2. west end under the arcade: face line of the walls' S face
uf = []
for f in wo.data.polygons:
    c = wm @ f.center; s, u = su(c); nw = (wm.to_3x3() @ f.normal)
    if 1.8 < s < 12 and c.z < 131 and abs(nw.x * d[0] + nw.y * d[1]) > 0.9 and u < 5: uf.append(u)
UW = float(np.median(uf)) if uf else 0.0
uc = []
for f in wo.data.polygons:
    c = wm @ f.center; s, u = su(c); nw = (wm.to_3x3() @ f.normal)
    if 48 < s < 53 and c.z < 131 and abs(nw.x * d[0] + nw.y * d[1]) > 0.9 and u < 5: uc.append(u)
UC = float(np.median(uc)) if uc else 0.25; print('cm walls S face u at the SE corner', round(UC, 3), len(uc), flush=True)
print('cm walls S face u at the west end', round(UW, 3), len(uf), flush=True)
prW = prof(1.5, 13.0, -3.0, -0.5, 0.5); gz = lambda s: float(np.interp(s, prW[:, 0], prW[:, 1]))
box(1.85, 9.25, UW - 0.035, UW + 0.01, 125.0, 131.38, ARC_ST)                       # cover panel over the generic window grid
box(51.45, 53.10, UC - 0.035, UC + 0.30, 127.6, 131.38, ARC_ST)                                # corner panel (clipped window)
box(53.06, 53.11, UC, 1.0, 127.6, 131.38, ARC_ST)                                                 # + the sliver on the east return up to the terrace face
# people door (s 2.15-3.05) + frame
zp = gz(2.6) + 0.02
box(2.05, 3.15, UW - 0.075, UW - 0.03, zp, zp + 2.30, DFR); box(2.15, 3.05, UW - 0.085, UW - 0.06, zp, zp + 2.20, PDOOR)
box(2.88, 2.95, UW - 0.11, UW - 0.08, zp + 0.95, zp + 1.05, PIPE)                     # lever
# roll-up door (s 3.45-7.65, 3.4 m) in a stucco reveal, ribbed slats, hood box
za = max(gz(s) for s in np.arange(3.3, 7.9, 0.25)) + 0.02
box(3.30, 7.95, UW - 0.75, UW - 0.03, za - 0.25, za, APR)                              # concrete apron (top flat at the door sill)
box(3.35, 3.45, UW - 0.10, UW - 0.03, za, za + 3.50, DFR); box(7.65, 7.75, UW - 0.10, UW - 0.03, za, za + 3.50, DFR); box(3.35, 7.75, UW - 0.10, UW - 0.03, za + 3.40, za + 3.50, DFR)
box(3.45, 7.65, UW - 0.06, UW - 0.04, za, za + 3.40, ROLL)
for zr in np.arange(za + 0.08, za + 3.38, 0.08): box(3.45, 7.65, UW - 0.068, UW - 0.06, zr, zr + 0.012, JTM)
box(3.45, 7.65, UW - 0.075, UW - 0.06, za, za + 0.06, JTM)                              # bottom bar
print('cm doors: people door z %.2f, roll-up sill %.2f' % (zp, za), flush=True)
# ---- 3b. downpipe (News12) at s 1.74, u UW-0.42, from grade to just under the eave soffit
ze = 135.30
pipe(P3(1.74, UW - 0.42, gz(1.74) + 0.05), P3(1.74, UW - 0.42, ze), 0.05, PIPE)
pipe(P3(1.74, UW - 0.42, gz(1.74) + 0.05), P3(1.74, UW - 0.62, gz(1.74) + 0.02), 0.05, PIPE)  # shoe
for zc in np.arange(gz(1.74) + 1.0, ze, 2.0): box(1.69, 1.79, UW - 0.37, UW - 0.30, zc, zc + 0.06, PIPE)  # wall brackets
print('cm faces added', len(bm.faces) - nf0, flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['cm_frontsteps_rollup'] = 'cm: flight A x0 %.2f..%.2f 9x%.3f; flight B x0 %.2f..%.2f 10x%.3f; doors + cover panel s 1.85-9.25; fascia->maroon' % (x0A, xtA, RA, x0B, xtB, RB_)
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm_ = zz['names']; kp = np.array([not str(nm_[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('cm 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b2).overlap(RBV)), flush=True); b2.free()
print('cm roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cm main: SAVED', flush=True)
