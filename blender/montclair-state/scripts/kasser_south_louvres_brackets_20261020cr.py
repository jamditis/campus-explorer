"""Session cr (Oct 20 ~4:45 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cq; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_south_roof_join_audit_20261020cq.py with SAVE 0 (-> cp -> co -> ... -> cf; SB 73.20), then the cr work:
 CAMERA MATCH (Commons File:Montclair State University (13252662863).jpg, CC BY-SA 2.0, Fuji JX650 f 4.65 mm -> F ~3473 px at 4608 wide;
 crop_..._groundfloor_cq.jpg sits at (700, 2152) in the original, found by template match): top-down 3-DOF camera fit to the 7 visible arcade
 arch centres. A bay shift k is not observable from the arcade alone (sliding), so the SE tower decides it: k=0 (the photo's rightmost arch =
 bay 15, s 48.5-51.8) puts the tower's SW/SE corners at x 1727/2127 (= the receding S face 360-443 px in the 960 px image, big E window right
 of it), k=1/2 would put the S/E corner inside the big E window -> k=0. Fit rms 4.5 px; predicted piers 95.9/156.3/223.1/297.3/380.3/473.7 px
 vs observed 96/152.5/219.5/295/377.5/475 (crop px). Camera ~ s 89.5, u -15.2 (on the amphitheater plaza), yaw 142 deg.
 1. SOUTH GROUND FLOOR, eastern bays (photo covers s ~27.0-50.8 at the wall): stucco cover panel s 26.80-51.45 over the generic window grid
    (like cm's s 1.85-9.25 panel; the corner panel 51.45-53.10 already exists), then 4 NARROW dark windows (0.72 m wide, centres 30.61 +
    1.75 i) and 6 grey LOUVRED panels (1.22 m wide, centres 37.61 + 1.75 j, slat pitch 0.10 m) - one ~1.75 m rhythm in the photo. Heads/sills
    from the photo's vertical scale at bay 14 (arcade floor 131.40 / eave soffit): louvres 128.80-130.10, windows 129.00-130.00, all
    photo-scaled = UNVERIFIED. s 9.25-26.80 (next to the roll-up; no photo) keeps the generic windows.
 2. SOUTH EAVE BRACKETS: dark timber brackets (horizontal arm under the soffit + diagonal knee strut to the arcade wall) at every arcade pier
    (s 2.3 + 3.3 k, k 0..14, + the corner pier at 52.4); the photo shows one per pier over s 32-48.5; west of s 27 = UNVERIFIED (assumed same).
 3. NOSING / RISER z-fight (cq Next 4): every cm/co nosing island (material Kasser_step_nosing_cm, linked faces) is moved 2 mm out along the
    area-weighted horizontal normal of its vertical faces, so its front face no longer lies in the riser's plane (was a 3-4 mm coplanar band).
    Check: vertical NOSE faces whose plane is within 0.5 mm of a vertical STEP face's plane (and overlapping it), before/after.
 4. 4a BVH vs the cf RHD npz (must be 0 pairs)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_south_roof_join_audit_20261020cq.py', run_name='__main__')
A = G['A']; d = G['d']; n = G['n']; su = G['su']; P3 = G['P3']
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']; wm = wo.matrix_world
def mk(name, col, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if m.name not in [x.name if x else None for x in me.materials]: me.materials.append(m)
    return [x.name if x else None for x in me.materials].index(m.name)
names = [x.name if x else None for x in me.materials]; mi = names.index
ARC_ST = mi('Arcade_stucco_white_ck'); GL = mi('Kasser_window_glass_cj'); JTM = mi('Arcade_joint_dark_ck')
LFR = mk('Kasser_louvre_frame_grey_cr', (0.44, 0.44, 0.43), 0.55, 0.3)
LSL = mk('Kasser_louvre_slat_grey_cr', (0.42, 0.42, 0.41), 0.5, 0.3)
LBK = mk('Kasser_louvre_back_dark_cr', (0.06, 0.06, 0.06), 0.9)
WFR = mk('Kasser_narrow_window_frame_cr', (0.30, 0.30, 0.30), 0.5, 0.2)
TIM = mk('Kasser_eave_bracket_timber_cr', (0.075, 0.052, 0.036), 0.75)
# wall face of the walls object S face: it is SKEWED vs the s axis (u 0.044 at s 8 -> ~0.27 at s 53), so fit u = a + b s from the vertical
# S-face vertices over s 20-53 and build the panel + louvres + windows along that line (a straight-u panel hid behind the wall at s 27-30
# in test t5: the generic window showed through).
pv = []
for f in wo.data.polygons:
    c = wm @ f.center; s_, u_ = su(c); nw = (wm.to_3x3() @ f.normal)
    if 20 < s_ < 53.1 and c.z < 131.5 and abs(nw.x * d[0] + nw.y * d[1]) > 0.9 and u_ < 1.0:
        for vi in f.vertices: pv.append(su(wm @ wo.data.vertices[vi].co))
pv = np.array(pv); WB, WA = np.polyfit(pv[:, 0], pv[:, 1], 1); res = pv[:, 1] - (WA + WB * pv[:, 0])
def uw(s_): return float(WA + WB * s_)
UF = uw(39.0)
print('cr walls S face line u = %.4f + %.5f s (rms %.4f, max %.4f, n %d); u at s 26.8 / 51.45 = %.3f / %.3f' % (WA, WB, float(np.sqrt((res ** 2).mean())), float(abs(res).max()), len(pv), uw(26.8), uw(51.45)), flush=True)
# LiDAR ground along the south face (u -3..-0.5)
z = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); px, py, pz, pc = z['x'], z['y'], z['z'], z['c']
g = ((pc == 1) | (pc == 2)) & (px > -270) & (px < -150) & (py > -110) & (py < 0)
GS = (px[g] - A[0]) * n[0] + (py[g] - A[1]) * n[1]; GU = (px[g] - A[0]) * d[0] + (py[g] - A[1]) * d[1]; GZ = pz[g]
def gz(s, w=0.75):
    k = (GS > s - w) & (GS < s + w) & (GU > -3.0) & (GU < -0.5)
    return float(np.median(GZ[k])) if k.sum() > 2 else float('nan')
print('cr LiDAR grade at the S face', [(s, round(gz(s), 2)) for s in (27, 30, 33, 36, 39, 42, 45, 48, 51)], flush=True)
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm); nf0 = len(bm.faces)
def quad(ps, mat):
    vs = [bm.verts.new(p) for p in ps]; f = bm.faces.new(vs); f.material_index = mat; return f
def box(s0, s1, u0, u1, z0, z1, mat):
    c = [P3(s, u, zz) for zz in (z0, z1) for u in (u0, u1) for s in (s0, s1)]
    for ix in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): quad([c[i] for i in ix], mat)
def boxw(s0, s1, du0, du1, z0, z1, mat):   # box whose u faces follow the skewed wall line: u = uw(s) + du
    c = [P3(s_, uw(s_) + du, zz) for zz in (z0, z1) for du in (du0, du1) for s_ in (s0, s1)]
    for ix in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): quad([c[i] for i in ix], mat)
def beam(p0, p1, w, h, mat):   # oriented box from p0 to p1 (in a vertical plane), width w (horizontal, perpendicular), height h
    p0 = Vector(p0); p1 = Vector(p1); ax = (p1 - p0).normalized(); side = Vector((float(n[0]), float(n[1]), 0)).normalized()
    up = ax.cross(side).normalized()
    if up.z < 0: up = -up
    c = [p0 + side * (sx * w / 2) + up * (sz * h / 2) + (p1 - p0) * t for t in (0, 1) for sz in (-1, 1) for sx in (-1, 1)]
    for ix in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): quad([c[i] for i in ix], mat)
# ---------- 1. cover panel + narrow windows + louvres (all offsets du relative to the skewed wall line)
DP = -0.035                                       # panel face 3.5 cm proud of the wall (as cm)
gmin = min(gz(s_) for s_ in np.arange(26.8, 51.5, 1.0) if not math.isnan(gz(s_)))
boxw(26.80, 51.45, DP, 0.01, gmin - 0.30, 131.38, ARC_ST)
print('cr cover panel s 26.80-51.45 du %.3f..0.01 z %.2f..131.38' % (DP, gmin - 0.30), flush=True)
NW = []
for i in range(4):
    c = 30.61 + 1.75 * i; w = 0.72; z0 = max(129.00, gz(c) + 0.35); z1 = 130.00
    boxw(c - w / 2, c + w / 2, DP - 0.045, DP + 0.005, z0, z1, WFR)                       # frame
    boxw(c - w / 2 + 0.06, c + w / 2 - 0.06, DP - 0.050, DP - 0.035, z0 + 0.06, z1 - 0.06, GL)   # glass
    boxw(c - w / 2 - 0.03, c + w / 2 + 0.03, DP - 0.09, DP + 0.005, z0 - 0.05, z0, ARC_ST)   # sill
    NW.append((round(c, 2), round(z0, 2)))
LV = []
for j in range(6):
    c = 37.61 + 1.75 * j; w = 1.22; z0 = max(128.80, gz(c) + 0.30); z1 = 130.10
    boxw(c - w / 2, c + w / 2, DP - 0.050, DP + 0.005, z0, z0 + 0.06, LFR); boxw(c - w / 2, c + w / 2, DP - 0.050, DP + 0.005, z1 - 0.06, z1, LFR)
    boxw(c - w / 2, c - w / 2 + 0.06, DP - 0.050, DP + 0.005, z0, z1, LFR); boxw(c + w / 2 - 0.06, c + w / 2, DP - 0.050, DP + 0.005, z0, z1, LFR)
    boxw(c - w / 2 + 0.06, c + w / 2 - 0.06, DP - 0.012, DP - 0.002, z0 + 0.06, z1 - 0.06, LBK)       # dark void behind the slats
    sa, sb = c - w / 2 + 0.06, c + w / 2 - 0.06
    for zs in np.arange(z0 + 0.10, z1 - 0.07, 0.10):                                     # slats, tilted (front edge lower)
        p0 = P3(sa, uw(sa) + DP - 0.045, zs - 0.025); p1 = P3(sb, uw(sb) + DP - 0.045, zs - 0.025)
        a0 = P3(sa, uw(sa) + DP - 0.012, zs + 0.025); a1 = P3(sb, uw(sb) + DP - 0.012, zs + 0.025)
        quad([p0, p1, a1, a0], LSL); quad([a0, a1, p1, p0], LSL)
    LV.append((round(c, 2), round(z0, 2)))
print('cr narrow windows (centre s, sill z)', NW, 'louvres (centre s, bottom z)', LV, flush=True)
# ---------- 2. eave brackets: probe soffit underside z and the arcade wall face u at each pier
b4 = bmesh.new(); b4.from_mesh(me); b4.transform(rm); bv = BVHTree.FromBMesh(b4)
piers = [2.3 + 3.3 * k for k in range(15)] + [52.4]; nb = 0; rep = []
for s in piers:
    hs = bv.ray_cast(P3(s, -0.45, 133.5), Vector((0, 0, 1)), 4.0)              # soffit underside just inside the eave edge
    if hs[0] is None: rep.append((s, 'no soffit')); continue
    zs = hs[0].z
    dirw = Vector((float(d[0]), float(d[1]), 0))
    hw = bv.ray_cast(P3(s, -1.5, zs - 0.35), dirw, 3.0)                          # arcade wall face under the soffit
    if hw[0] is None: rep.append((s, 'no wall')); continue
    uw = su(hw[0])[1]
    he = bv.ray_cast(P3(s, -1.2, zs - 0.02), dirw, 3.0)                          # eave edge (fascia) face at soffit level
    ue = su(he[0])[1] if he[0] is not None else -0.60
    if not (-1.2 < uw < 0.4) or uw - ue < 0.15: rep.append((s, 'odd', round(zs, 2), round(uw, 2), round(ue, 2))); continue
    uo = ue + 0.06                                                               # arm end just inside the fascia
    beam(P3(s, uw - 0.002, zs - 0.07), P3(s, uo, zs - 0.07), 0.10, 0.14, TIM)    # horizontal arm (top 0 mm under the soffit)
    kz = zs - 0.14 - max(0.35, (uw - uo) * 1.1)
    beam(P3(s, uw - 0.045, kz), P3(s, uw - 0.045 - (uw - uo) * 0.75, zs - 0.14), 0.08, 0.08, TIM)   # diagonal knee strut
    box(s - 0.06, s + 0.06, uw - 0.03, uw - 0.002, kz - 0.05, zs - 0.02, TIM)                  # wall plate
    nb += 1; rep.append((round(s, 2), round(zs, 2), round(uw, 3), round(ue, 3)))
b4.free()
print('cr brackets placed', nb, rep, flush=True)
# ---------- 3. nosing islands 2 mm off the riser planes
NOSEm = mi('Kasser_step_nosing_cm'); STEPm = mi('Kasser_step_concrete_cm')
def coplanar_count():
    st = [f for f in bm.faces if f.material_index == STEPm and abs(f.normal.z) < 0.1]
    no = [f for f in bm.faces if f.material_index == NOSEm and abs(f.normal.z) < 0.1]
    bins = {}
    for f in st:
        nrm = f.normal; k = (round(nrm.x, 2), round(nrm.y, 2)); bins.setdefault(k, []).append((nrm.dot(f.calc_center_median()), f))
    cnt = 0; hit = []
    for f in no:
        nrm = f.normal; k = (round(nrm.x, 2), round(nrm.y, 2)); c = f.calc_center_median(); off = nrm.dot(c)
        for o_, g in bins.get(k, []):
            if abs(o_ - off) < 0.0005:
                gc = g.calc_center_median()
                if (gc - c).length < 0.5 * (math.sqrt(f.calc_area()) + math.sqrt(g.calc_area())) + 3.0: cnt += 1; hit.append(f); break
    return cnt, len(no), hit
bm.faces.ensure_lookup_table()
print('cr nosing faces coplanar with a riser BEFORE', coplanar_count()[:2], flush=True)
seen = set(); nisl = 0
for f0 in bm.faces:
    if f0.material_index != NOSEm or f0.index in seen: continue
    isl = []; stack = [f0]; seen.add(f0.index)
    while stack:
        f = stack.pop(); isl.append(f)
        for e in f.edges:
            for g in e.link_faces:
                if g.material_index == NOSEm and g.index not in seen: seen.add(g.index); stack.append(g)
    v = Vector((0, 0, 0))
    for f in isl:
        if abs(f.normal.z) < 0.1 and f.calc_area() > 0.002: v += Vector((f.normal.x, f.normal.y, 0)) * f.calc_area()
    if v.length < 1e-6: continue
    v.normalize(); vs = {x for f in isl for x in f.verts}
    if any(g.material_index != NOSEm for x in vs for g in x.link_faces): continue      # shares verts with concrete -> leave (not an overlay island)
    for x in vs: x.co += v * 0.002
    nisl += 1
print('cr nosing islands moved 2 mm out', nisl, flush=True)
c2 = coplanar_count(); print('cr nosing faces coplanar with a riser after the island pass', c2[:2], flush=True)
# pass 2: remaining coplanar NOSE faces (islands with mixed normals / shared verts): move that face's own verts 2 mm along its normal
# (only verts whose faces are all NOSE, so no concrete face is touched; the attached nosing top/end faces stretch by 2 mm)
mv2 = 0
for f in c2[2]:
    nrm = Vector((f.normal.x, f.normal.y, 0)).normalized()
    for x in f.verts:
        if all(g.material_index == NOSEm for g in x.link_faces): x.co += nrm * 0.002; mv2 += 1
print('cr pass 2 verts moved', mv2, flush=True)
print('cr nosing faces coplanar with a riser AFTER', coplanar_count()[:2], flush=True)
print('cr faces added', len(bm.faces) - nf0, flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['cr_south_louvres_brackets'] = 'cr: cover panel s 26.80-51.45, 4 narrow windows (30.61+1.75i), 6 louvres (37.61+1.75j), %d eave brackets; photo 13252662863 camera match k=0; UNVERIFIED sizes' % nb
# ---------- 4. 4a
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b3 = bmesh.new(); b3.from_mesh(o.data); b3.transform(o.matrix_world)
    print('cr 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b3).overlap(RBV)), flush=True); b3.free()
print('cr roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cr main: SAVED', flush=True)
