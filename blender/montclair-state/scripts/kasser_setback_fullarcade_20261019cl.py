"""Session cl (Oct 19 ~10:30 PM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes ck; SAVE=1 saves). Run ONLY this script.
RUN ORDER: sets the ck params NBAY 15 / S_ENDX 53.07 / EAST_OPEN 1 / ROOFU1 0.35, runs scripts/kasser_level4_arcade_20261019ck.py with SAVE 0
(-> cj -> ci2 -> ci -> ch -> cg -> cf), so the level-4 open arcade runs the FULL south side (Joe 9:53 PM), then:
 1. SKIRT (Joe 9:09 PM): the white band above the south tile shed is a REAL set-back upper storey (LiDAR class 6: shed 135.56->136.36 over
    u 0-3.0, then a step of ~3.8 m within <0.5 m to 140.1 (s<24) / 141.56 (s 24-47) at u ~3.25; MEASURED). cj put that face at u 2.5 (its
    zone line), so the shed stopped 0.75 m short and the face read as a skirt rising off the eave. Fix: zone verts at u 2.5 moved to the
    measured face u 3.25 (shed continues on its fitted plane), raised parapet band u 3.25-5.0 at the measured 140.1 / 141.56 tops with
    coping, maroon eave trim at the top of the face + square dark-framed windows one per bay (News12 photo: set-back white wall with square
    windows and a dark-red eave trim; window size/height photo-scaled, UNVERIFIED).
 2. East end: shed + tile eave continued over s 46.6-53.07 (LiDAR shed 135.63->135.98 there, MEASURED); walls + roof east faces opened in the
    gallery span at the SE corner (s 53.07); 3 risers inside the gallery 131.40 -> 131.87 (terrace MEASURED: LiDAR class 1/6 plateau 131.86-131.95
    over s 53-62, u 1-7); terrace slab s 53.07-61.0 (u 1.0-5.4/6.6) at 131.87 with a stucco retaining face down to the street (128.5-128.7 MEASURED).
    Front steps (street 128.7 -> 130.24 at s 61-64, MEASURED rise) are NOT modelled (terrain only).
 3. A small downlight per bay on the gallery ceiling (Joe's photo).
All geometry goes into the roof object's mesh (north picks it up through the Kasser link). 4a BVH printed vs the cf RHD npz (trees excluded)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ.update({'SAVE': '0', 'NBAY': os.environ.get('NBAY', '15'), 'S_ENDX': os.environ.get('S_ENDX', '53.07'), 'EAST_OPEN': '1', 'ROOFU1': '0.35'})
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_level4_arcade_20261019ck.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
def P3(s, u, z): q = xy(s, u); return Vector((q[0], q[1], z))
UF = float(os.environ.get('UFACE', '3.25')); U_SS = 2.5; S_ENDX = float(os.environ['S_ENDX']); FLOOR = 131.4; ZT = 135.40; CEIL = ZT - 0.10
TERR = 131.87; BAY = 3.3; P = 0.70; S0 = 1.95; NB = int(os.environ['NBAY'])
# ---- LiDAR: same SS (south shed) fit + tower rect as cj, plus per-s band heights
z = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); px, py, pz, pc = z['x'], z['y'], z['z'], z['c']
m = (pc == 6) & (px > -265) & (px < -150) & (py > -80) & (py < 30)
PS = (px[m] - A[0]) * n[0] + (py[m] - A[1]) * n[1]; PU = (px[m] - A[0]) * d[0] + (py[m] - A[1]) * d[1]; PZ = pz[m]
k = (PZ > 148.5) & (PS > 38) & (PS < 64) & (PU > -2) & (PU < 20); TW0 = float(np.percentile(PS[k], 2)); TW1 = float(np.percentile(PS[k], 98)); TW2 = float(np.percentile(PU[k], 2))
k = (PS > -1.7) & (PS < TW0 - 0.3) & (PU > -3.7) & (PU < U_SS - 0.3) & (PZ > 134.5); SS = np.polyfit(PU[k], PZ[k], 1)
def ssz(u): return float(SS[1] + SS[0] * u)
bands = []
for s0 in np.arange(2.0, TW0 - 0.5, 1.0):
    kb = (PS >= s0) & (PS < s0 + 1) & (PU > 3.4) & (PU < 4.9); kr = (PS >= s0) & (PS < s0 + 1) & (PU > 5.3) & (PU < 8.0)
    kf = (PS >= s0) & (PS < s0 + 1) & (PU > 2.6) & (PU < 3.1)
    if kb.sum() > 3: bands.append((s0, float(np.median(PZ[kb])), float(np.median(PZ[kr])) if kr.sum() > 3 else np.nan, float(np.median(PZ[kf])) if kf.sum() > 2 else np.nan))
bands = np.array(bands); hi = bands[:, 1] > 140.8; split = float(bands[np.argmax(hi), 0]) if hi.any() else TW0
SEG = [(2.0, split, float(np.median(bands[~hi, 1]))), (split, TW0, float(np.median(bands[hi, 1])))]
print('cl LiDAR TW0', round(TW0, 2), 'SS', np.round(SS, 4), 'ss(3.25)', round(ssz(UF), 2), '| face u', UF, '| band segs', [(round(a, 1), round(b, 1), round(c, 2)) for a, b, c in SEG],
      '| roof behind band', round(float(np.nanmedian(bands[~hi, 2])), 2), round(float(np.nanmedian(bands[hi, 2])), 2), '| shed at u 2.6-3.1', round(float(np.nanmedian(bands[:, 3])), 2), flush=True)
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']; wm = wo.matrix_world
names = [x.name if x else None for x in me.materials]
GL, FR, TILE, FAS, COP, STU = names.index('Kasser_window_glass_cj'), names.index('Kasser_window_frame_maroon_cj'), 0, 2, 5, 3
FLM, SCM = names.index('Arcade_concrete_floor_ck'), names.index('Arcade_sconce_bronze_ck'); ARC_ST = names.index('Arcade_stucco_white_ck')
lm = bpy.data.materials.get('Arcade_downlight_lens_cl') or bpy.data.materials.new('Arcade_downlight_lens_cl'); lm.use_nodes = True
bb = lm.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value = (1.0, 0.86, 0.66, 1); bb.inputs['Emission Color'].default_value = (1.0, 0.86, 0.66, 1); bb.inputs['Emission Strength'].default_value = 4.0
if lm.name not in names: me.materials.append(lm)
LENS = [x.name if x else None for x in me.materials].index(lm.name)
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
ckv = {v for f in bm.faces if f.material_index >= 8 for v in f.verts}
# ---- 1a. move the cj setback face u 2.5 -> 3.25 (s < TW0)
mv = 0; mvz = 0
for v in bm.verts:
    if v in ckv: continue
    s, u = su(v.co)
    if abs(u - U_SS) < 0.006 and -3.5 < s < TW0 + 0.01:
        v.co += Vector((d[0] * (UF - u), d[1] * (UF - u), 0)); mv += 1
        if 135.0 < v.co.z < 137.6 and abs(v.co.z - ssz(U_SS)) < 0.05: v.co.z = ssz(UF); mvz += 1
print('cl setback face verts moved', mv, 'shed-top verts re-planed', mvz, flush=True)
# ---- 1b. s_of_tower zone (TW0..53.07, u < 3.25): flat 136.2 -> shed plane (LiDAR shows the shed continuing)
tf = [f for f in bm.faces if f.material_index < 8 and f.normal.z > 0.9 and TW0 - 0.1 < su(f.calc_center_median())[0] < TW1 and su(f.calc_center_median())[1] < TW2 and 135.5 < f.calc_center_median().z < 137.0]
co = xy(0, UF); g = list({e for f in tf for e in f.edges}) + tf + list({v for f in tf for v in f.verts})
bmesh.ops.bisect_plane(bm, geom=g, dist=1e-4, plane_co=Vector((co[0], co[1], 0)), plane_no=Vector((d[0], d[1], 0)))
nre = 0
for v in bm.verts:
    if v in ckv or v.co.z < 135.5 or v.co.z > 137.0: continue
    s, u = su(v.co)
    if TW0 - 0.01 < s < S_ENDX + 0.2 and u < UF - 0.05: v.co.z = ssz(u); nre += 1
print('cl s_of_tower verts -> shed plane', nre, flush=True)
# ---- 1c/2. east-face opening of the roof prism at the SE corner (gallery span u 0.3-2.45, below ZT)
def eastface(f, s0, s1, u1, zmax):
    c = f.calc_center_median(); s, u = su(c)
    return s0 < s < s1 and u < u1 and abs(f.normal.z) < 0.2 and abs(Vector((*n, 0)).dot(f.normal)) > 0.9 and f.material_index < 8 and c.z < zmax
def bis_sel(bm, sel, co, no):
    c = [f for f in bm.faces if sel(f)]; g = list({e for f in c for e in f.edges}) + c + list({v for f in c for v in f.verts})
    bmesh.ops.bisect_plane(bm, geom=g, dist=1e-4, plane_co=Vector(co), plane_no=Vector(no))
q = xy(0, 2.45)
bis_sel(bm, lambda f: eastface(f, 52.5, 53.6, 6.2, 140), (q[0], q[1], 0), (d[0], d[1], 0)); bis_sel(bm, lambda f: eastface(f, 52.5, 53.6, 6.2, 140), (0, 0, ZT), (0, 0, 1))
de = [f for f in bm.faces if eastface(f, 52.5, 53.6, 2.45, ZT) and max(v.co.z for v in f.verts) < ZT + 0.005]
bmesh.ops.delete(bm, geom=de, context='FACES'); print('cl roof east-face faces deleted', len(de), flush=True)
# ---- geometry helpers
def box(s0, s1, u0, u1, z0, z1, mat):
    c = [(s0, u0), (s1, u0), (s1, u1), (s0, u1)]
    lo = [bm.verts.new(P3(s, u, z0)) for s, u in c]; hi_ = [bm.verts.new(P3(s, u, z1)) for s, u in c]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi_)] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi_[(i + 1) % 4], hi_[i])) for i in range(4)]
    for f in fs: f.material_index = mat
    return fs
def cyl(s, u, z0, z1, r, mat, seg=12):
    lo = [bm.verts.new(P3(s, u, z0) + Vector((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), 0))) for i in range(seg)]
    hi_ = [bm.verts.new(v.co + Vector((0, 0, z1 - z0))) for v in lo]
    fs = [bm.faces.new(lo[::-1]), bm.faces.new(hi_)] + [bm.faces.new((lo[i], lo[(i + 1) % seg], hi_[(i + 1) % seg], hi_[i])) for i in range(seg)]
    for f in fs: f.material_index = mat
nf0 = len(bm.faces)
# 1d. parapet band (MEASURED tops), coping, maroon eave trim, square windows (News12, photo-scaled)
zb = ssz(UF)
for s0, s1, ztop in SEG:
    box(s0, s1, UF, 5.0, zb, ztop - 0.12, STU); box(s0 - 0.05, s1, UF - 0.06, 5.06, ztop - 0.12, ztop, COP)
    box(s0, s1, UF - 0.32, UF, ztop - 0.55, ztop - 0.20, FR); box(s0, s1, UF - 0.36, UF - 0.30, ztop - 0.60, ztop - 0.18, FR)   # dark-red eave trim (News12), depth UNVERIFIED
    box(s0, s1, UF - 0.04, UF, zb + 0.02, zb + 0.20, STU)                                                                       # base course above the shed flashing
WW, WH = 1.30, 1.30; WZ0 = zb + 0.95; nwin = 0
for i in range(NB):
    sc_ = S0 + i * BAY + P + (BAY - P) / 2
    if sc_ + WW / 2 > TW0 - 0.4: continue
    box(sc_ - WW / 2, sc_ + WW / 2, UF - 0.06, UF + 0.01, WZ0, WZ0 + WH, FR); box(sc_ - WW / 2 + 0.10, sc_ + WW / 2 - 0.10, UF - 0.075, UF - 0.03, WZ0 + 0.10, WZ0 + WH - 0.10, GL)
    box(sc_ - WW / 2 - 0.06, sc_ + WW / 2 + 0.06, UF - 0.12, UF, WZ0 - 0.07, WZ0, STU); nwin += 1
print('cl setback windows', nwin, 'z', round(WZ0, 2), round(WZ0 + WH, 2), flush=True)
# 2a. tile eave continued s TW0..S_ENDX on the same plane as cj (0.6 m overhang + fascia)
c4 = [(TW0, -0.6), (S_ENDX + 0.6, -0.6), (S_ENDX + 0.6, 0.02), (TW0, 0.02)]
hv = [bm.verts.new(P3(s, u, ssz(u) + 0.01)) for s, u in c4]; lv = [bm.verts.new(P3(s, u, ssz(u) - 0.18)) for s, u in c4]
fs = [bm.faces.new(hv), bm.faces.new(lv[::-1])] + [bm.faces.new((lv[i], lv[(i + 1) % 4], hv[(i + 1) % 4], hv[i])) for i in range(4)]
for f in fs: f.material_index = TILE if f.normal.z > 0.2 else FAS
# 2b. gallery east end: 3 risers 131.40 -> 131.87 (terrace MEASURED), terrace slab + stucco retaining face to the street
R3 = (TERR - FLOOR) / 3
for kk in (1, 2, 3): box(S_ENDX - (4 - kk) * 0.30, S_ENDX, 0.30, 2.45, FLOOR - 0.05, FLOOR + kk * R3, FLM)
box(S_ENDX, 57.05, 1.0, 5.39, 128.3, TERR - 0.02, ARC_ST); box(57.05, 61.0, 1.0, 6.6, 128.3, TERR - 0.02, ARC_ST)
box(S_ENDX, 57.05, 1.0, 5.39, TERR - 0.02, TERR, FLM); box(57.05, 61.0, 1.0, 6.6, TERR - 0.02, TERR, FLM)
box(S_ENDX - 0.02, 61.0, 0.96, 1.06, TERR - 0.02, TERR + 0.08, ARC_ST)                                                        # terrace edge coping (UNVERIFIED)
# 2c. terrace guard (a 3.3 m drop to the street must have one; LiDAR shows no solid parapet at u 1.0, so an open maroon rail like the arcade's;
#     form/height UNVERIFIED placeholder) + stucco reveal joints on the retaining face at the arcade bay rhythm
JTM = names.index('Arcade_joint_dark_ck'); RLM = names.index('Arcade_rail_maroon_ck')
for sp in np.arange(S_ENDX + 0.15, 61.0, 1.5): box(sp - 0.025, sp + 0.025, 1.10, 1.15, TERR + 0.08, TERR + 1.07, RLM)
box(S_ENDX + 0.1, 61.0, 1.09, 1.16, TERR + 1.02, TERR + 1.07, RLM)
for zr in (TERR + 0.25, TERR + 0.55, TERR + 0.82): box(S_ENDX + 0.1, 61.0, 1.115, 1.135, zr, zr + 0.025, RLM)
for js in np.arange(S0 + 15 * BAY + 0.35 + BAY, 61.0, BAY): box(js - 0.008, js + 0.008, 0.985, 1.0, 128.3, TERR - 0.15, JTM)
box(S_ENDX, 61.0, 0.985, 1.0, 130.20, 130.216, JTM)
# 3. downlight per bay (Joe's photo)
for i in range(NB):
    sc_ = S0 + i * BAY + P + (BAY - P) / 2; cyl(sc_, 1.375, CEIL - 0.05, CEIL, 0.09, SCM, 16); cyl(sc_, 1.375, CEIL - 0.055, CEIL - 0.05, 0.065, LENS, 16)
print('cl faces added', len(bm.faces) - nf0, flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
# ---- walls: open the east face in the gallery span at the SE corner
wb = bmesh.new(); wb.from_mesh(wo.data); wb.transform(wm)
def weast(f, u1): c = f.calc_center_median(); s, u = su(c); return 52.5 < s < 53.6 and u < u1 and abs(f.normal.z) < 0.2 and abs(Vector((*n, 0)).dot(f.normal)) > 0.9
for co_, no_ in (((q[0], q[1], 0), (d[0], d[1], 0)), ((0, 0, FLOOR), (0, 0, 1))):
    c = [f for f in wb.faces if weast(f, 6.2)]; g = list({e for f in c for e in f.edges}) + c + list({v for f in c for v in f.verts})
    bmesh.ops.bisect_plane(wb, geom=g, dist=1e-4, plane_co=Vector(co_), plane_no=Vector(no_))
de = [f for f in wb.faces if weast(f, 2.45) and f.calc_center_median().z > FLOOR]
bmesh.ops.delete(wb, geom=de, context='FACES'); print('cl walls east-face faces deleted', len(de), flush=True)
wb.transform(wm.inverted()); wb.to_mesh(wo.data); wb.free(); wo.data.update()
ro['cl_setback_fullarcade'] = 'cl: setback face u %.2f, band %s, arcade s %.2f-%.2f %d bays, terrace %.2f' % (UF, [(round(a, 1), round(b, 1), round(c, 2)) for a, b, c in SEG], S0, S_ENDX, NB, TERR)
# ---- 4a BVH vs RHD npz
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm_ = zz['names']; kp = np.array([not str(nm_[i]).startswith('NT_') for i in ob]); T = T[kp]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('cl 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b2).overlap(RB)), flush=True); b2.free()
print('cl roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cl main: SAVED', flush=True)
