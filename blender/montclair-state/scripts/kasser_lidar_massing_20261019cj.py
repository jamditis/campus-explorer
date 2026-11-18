"""Session cj (Oct 19 ~8:35 PM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes ci2; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_jog_wedge_cleanup_20261019ci2.py first (SAVE forced 0 -> ci -> ch -> cg -> cf), THEN replaces the mesh of
'Alexander Kasser Theater roof (LiDAR)' with a LiDAR-true MASSING above the wall top (133.93 m):
 Finding (cj): the ch/ci 31-degree hip was fitted to the generator's draped hip mesh, NOT to the 2023 LiDAR. The class-6 LiDAR points
 (data/pts_crop.npz) show: flat-roof fly tower ~151.4 m (west-centre), a low-pitch red-tile GABLE over the auditorium (ridge E-W, ~147.3),
 a curved-top white stucco EAST front wall (arc top ~147.7) = the wall in the PD Commons photo (photo = EAST facade, its left tower =
 Kasser's own SE tower ~150.9 m with a low tile pyramid), a tile shed loggia in front of the east wall (~137.4 -> ~135.9), a tile strip along
 the south, and flat membrane roofs ~139.5-141.6 m elsewhere. Zone heights/bounds are MEASURED from the points inside each zone
 (median / fitted planes); zone split lines are hand-chosen from a 3 m LiDAR table (UNVERIFIED to +-1 m); curved-wall thickness 0.6 m,
 south-strip pitch fallback 22 deg, pyramid form UNVERIFIED.
 Old hip mesh kept as fake-user mesh 'ci2_orig_kasser_roof_hip' (revert = assign it back). The hip-eave objects (soffit/fascia, barrel eave
 course) are hidden (render + viewport), not deleted. North picks this up via the existing Kasser link (same object names).
Idempotent (each run starts from the ci2 state). 4a BVH printed vs the cf RHD npz (trees excluded)."""
import bpy, bmesh, os, runpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_jog_wedge_cleanup_20261019ci2.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
ZW = 133.93
# ---------- LiDAR (class 6) in the deck frame
z = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); px, py, pz, pc = z['x'], z['y'], z['z'], z['c']
m = (pc == 6) & (px > -265) & (px < -150) & (py > -80) & (py < 30)
PS = (px[m] - A[0]) * n[0] + (py[m] - A[1]) * n[1]; PU = (px[m] - A[0]) * d[0] + (py[m] - A[1]) * d[1]; PZ = pz[m]
def sel(s0, s1, u0, u1, ins=0.7, zmin=-1e9):
    k = (PS > s0 + ins) & (PS < s1 - ins) & (PU > u0 + ins) & (PU < u1 - ins) & (PZ > zmin); return k
def med(s0, s1, u0, u1, fb=136.2):
    k = sel(s0, s1, u0, u1); return float(np.median(PZ[k])) if k.sum() > 8 else fb
def rng(k, a, lo=2, hi=98): return float(np.percentile(a[k], lo)), float(np.percentile(a[k], hi))
k = (PZ > 150.5) & (PS > 3) & (PS < 35) & (PU > 5) & (PU < 50); FT = rng(k, PS) + rng(k, PU); FTZ = float(np.median(PZ[k]))
k = (PZ > 148.5) & (PS > 38) & (PS < 64) & (PU > -2) & (PU < 20); TW = list(rng(k, PS) + rng(k, PU)); TWZ = float(np.percentile(PZ[k], 99)); TWE = float(np.percentile(PZ[k], 5))
WALL = float(os.environ.get('WALL', '55.0'))   # east face of the curved wall: LiDAR 0.5 m s-profiles at u 20/27/35/42 drop 146-147.7 -> 137 between s 54.5 and 55.0 (MEASURED, cj)
k = (PZ > 142.6) & (PS > FT[1] + 1) & (PS < TW[0] - 1) & (PU > 8) & (PU < 52); AU0, AU1 = rng(k, PU, 1, 99)
print('cj tower pre-clamp', np.round(TW, 2), flush=True)
TWOV = float(os.environ.get('TWOV', '1.0')); TWPOD = 141.1   # tower: LiDAR >148.5 footprint includes the cap overhang -> shaft inset TWOV (UNVERIFIED, photo shows a wide flared cap); podium ring at the lobby roof height (UNVERIFIED)
CWT = float(os.environ.get('CWT', '1.4'))   # LiDAR top plateau s 53.5-54.9 (MEASURED +-0.5 m)
# gable fit on the auditorium (exclude curved wall strip)
k = sel(FT[1], min(TW[0], WALL - CWT), AU0, AU1, 0.8, 142.0) & (PZ < 148.5); us, zs = PU[k], PZ[k]
best = None
for ur in np.arange(AU0 + 5, AU1 - 5, 0.1):
    X = np.c_[np.ones_like(us), -np.abs(us - ur)]; c, res, *_ = np.linalg.lstsq(X, zs, rcond=None); r = float(np.sqrt(np.mean((X @ c - zs) ** 2)))
    if best is None or r < best[0]: best = (r, ur, c[0], c[1])
GR, UR, ZR, KT = best
# curved wall arc: max per 1 m u-bin in the wall strip, quadratic fit
k = sel(WALL - CWT, WALL, TW[3], AU1, 0.1); ub = np.arange(TW[3], AU1, 1.0); pts = []
for u0 in ub:
    kk = k & (PU >= u0) & (PU < u0 + 1)
    if kk.sum() > 3: pts.append((u0 + 0.5, float(np.percentile(PZ[kk], 95))))
pts = np.array(pts); ARC = np.polyfit(pts[:, 0], pts[:, 1], 2); arc = lambda u: float(np.polyval(ARC, u)); arc_rms = float(np.sqrt(np.mean((np.polyval(ARC, pts[:, 0]) - pts[:, 1]) ** 2)))
# east loggia shed plane z = a + b s
k = sel(WALL, 70, TW[3], AU1, 0.5, 134.5) & (PZ < 140.0); EL = np.polyfit(PS[k], PZ[k], 1) if k.sum() > 20 else np.array([-0.2, 137.4 + 0.2 * WALL])
# south strip shed z = a + b u (fallback 22 deg about the mean if nearly flat)
U_SS = 2.5; k = sel(-2, TW[0], -4, U_SS, 0.3, 134.5)
SS = np.polyfit(PU[k], PZ[k], 1) if k.sum() > 20 else np.array([0.0, 136.2])
ss_note = 'fitted'
if SS[0] < 0.2: mz = float(np.mean(PZ[k])) if k.sum() else 136.2; SS = np.array([np.tan(np.radians(22)), mz - np.tan(np.radians(22)) * 1.2]); ss_note = 'fallback 22deg about measured mean %.2f' % mz
print('cj zones FT', np.round(FT, 2), round(FTZ, 2), '| TW', np.round(TW, 2), round(TWE, 2), round(TWZ, 2), '| WALL s', round(WALL, 2), 'AU u', round(AU0, 2), round(AU1, 2),
      '| gable ridge u', round(UR, 2), 'z', round(ZR, 2), 'pitch', round(np.degrees(np.arctan(KT)), 2), 'rms', round(GR, 3), '| arc', np.round(ARC, 4), 'rms', round(arc_rms, 3), 'centre', round(arc(-ARC[1] / (2 * ARC[0])), 2),
      '| EL', np.round(EL, 3), '| SS', np.round(SS, 3), ss_note, flush=True)
SMIN, SMAX, UMIN, UMAX = -3, 72, -5, 58
Z = []  # (name, s0, s1, u0, u1, kind, param)
Z.append(('south_strip', SMIN, TW[0], UMIN, U_SS, 'fn', lambda s, u: SS[1] + SS[0] * u))
Z.append(('s_of_tower', TW[0], TW[1], UMIN, TW[2], 'flat', None))
Z.append(('se_low', TW[1], SMAX, UMIN, TW[3], 'flat', None))
Z.append(('se_tower_podium', TW[0], TW[1], TW[2], TW[3], 'flat', None))
Z.append(('west_s', SMIN, FT[0], U_SS, 29.0, 'flat', None))
Z.append(('west_n', SMIN, FT[0], 29.0, UMAX, 'flat', None))
Z.append(('s_of_fly', FT[0], FT[1], U_SS, FT[2], 'flat', None))
Z.append(('lobby_s', FT[1], TW[0], U_SS, AU0, 'flat', None))
Z.append(('fly_tower', FT[0], FT[1], FT[2], FT[3], 'flat', None))
Z.append(('n_of_fly', FT[0], FT[1], FT[3], UMAX, 'flat', None))
Z.append(('auditorium', FT[1], TW[0], AU0, AU1, 'gable', None))
Z.append(('auditorium_e', TW[0], WALL - CWT, TW[3], AU1, 'gable', None))
Z.append(('curved_wall', WALL - CWT, WALL, TW[3], AU1, 'arc', None))
Z.append(('n_of_aud', FT[1], WALL, AU1, UMAX, 'flat', None))
Z.append(('east_loggia', WALL, SMAX, TW[3], AU1, 'fn', lambda s, u: EL[1] + EL[0] * s))
Z.append(('ne_low', WALL, SMAX, AU1, UMAX, 'flat', None))
# ---------- footprint = walls top ring (largest loop of top edges at ZW)
wo = bpy.data.objects['Alexander Kasser Theater walls']; wm = wo.matrix_world
wb = bmesh.new(); wb.from_mesh(wo.data); wb.transform(wm)
te = [e for e in wb.edges if all(abs(v.co.z - ZW) < 0.02 for v in e.verts) and len(e.link_faces) >= 1 and any(abs(f.normal.z) < 0.3 for f in e.link_faces)]
adj = {}
for e in te:
    a, b = e.verts; adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
loops, seen = [], set()
for v0 in adj:
    if v0 in seen: continue
    loop = [v0]; seen.add(v0); prev = None; cur = v0
    while True:
        nx = [w for w in adj[cur] if w is not prev and w not in seen]
        if not nx: break
        prev, cur = cur, nx[0]; loop.append(cur); seen.add(cur)
    if len(loop) > 2: loops.append(loop)
def area(L): P = np.array([v.co.xy[:] for v in L]); return 0.5 * abs(np.dot(P[:, 0], np.roll(P[:, 1], 1)) - np.dot(P[:, 1], np.roll(P[:, 0], 1)))
loops.sort(key=area, reverse=True)
FP = [Vector((v.co.x, v.co.y)) for v in loops[0]]
print('cj footprint loop verts', len(FP), 'area', round(area(loops[0]), 1), 'm2; loops', len(loops), [round(area(L), 1) for L in loops[:4]], flush=True); wb.free()
# ---------- build
out = bmesh.new()
def clip_face(bm, s0, s1, u0, u1):
    for co, no in ((xy(s0, 0), -n), (xy(s1, 0), n), (xy(0, u0), -d), (xy(0, u1), d)):
        g = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=g, plane_co=Vector((co[0], co[1], 0)), plane_no=Vector((no[0], no[1], 0)), clear_outer=True)
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
info = []
for name, s0, s1, u0, u1, kind, fn in Z:
    if s1 - s0 < 0.05 or u1 - u0 < 0.05: continue
    bm = bmesh.new(); vs = [bm.verts.new((p.x, p.y, ZW)) for p in FP]; bm.faces.new(vs)
    clip_face(bm, s0, s1, u0, u1)
    if not bm.faces: bm.free(); continue
    a2 = sum(f.calc_area() for f in bm.faces)
    if a2 < 0.3: bm.free(); continue
    cuts = []
    if kind == 'gable': cuts = [UR]
    if kind == 'arc': cuts = list(np.arange(np.ceil(u0), u1, 1.0))
    for uc in cuts:
        co = xy(0, uc); g = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=g, plane_co=Vector((co[0], co[1], 0)), plane_no=Vector((d[0], d[1], 0)))
    bmesh.ops.dissolve_degenerate(bm, dist=0.01, edges=bm.edges[:])
    bot = bm.faces[:]
    r = bmesh.ops.extrude_face_region(bm, geom=bot)
    top = [v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)]
    zf = med(s0, s1, u0, u1)
    if name == 'se_tower_podium': zf = TWPOD
    for v in top:
        s, u = su(v.co)
        if kind == 'flat': v.co.z = zf
        elif kind == 'fn': v.co.z = fn(s, u)
        elif kind == 'gable': v.co.z = ZR - KT * abs(u - UR)
        elif kind == 'arc': v.co.z = arc(u)
    if kind == 'pyr':
        tf = [f for f in bm.faces if f not in bot and all(v in top for v in f.verts)]
        pr = bmesh.ops.poke(bm, faces=tf)
        for v in pr['verts']: v.co.z = TWZ
    bmesh.ops.delete(bm, geom=bot, context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:  # outward check: side faces should point away from the zone centre, tops up
        if f.normal.z < -0.5: f.normal_flip()
    zt = [v.co.z for v in top]; info.append((name, round(a2, 1), round(min(zt), 2), round(max(zt), 2)))
    tmp = bpy.data.meshes.new('cj_tmp'); bm.to_mesh(tmp); bm.free(); out.from_mesh(tmp); bpy.data.meshes.remove(tmp)
# tower shaft (inset, no footprint clip needed: inside TW) + pyramid cap over the full TW rect
def box_prism(s0, s1, u0, u1, z0, z1):
    bm = bmesh.new(); vs = [bm.verts.new((*xy(s, u), z0)) for s, u in ((s0, u0), (s1, u0), (s1, u1), (s0, u1))]; f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f]); top = [v for v in r['geom'] if isinstance(v, bmesh.types.BMVert)]
    for v in top: v.co.z = z1
    bmesh.ops.delete(bm, geom=[f], context='FACES_ONLY'); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); return bm, top
TH = 0.35
bm, _ = box_prism(TW[0] + TWOV, TW[1] - TWOV, TW[2] + TWOV, TW[3] - TWOV, TWPOD - 0.01, TWE - TH + 0.01)
tmp = bpy.data.meshes.new('cj_tmp'); bm.to_mesh(tmp); bm.free(); out.from_mesh(tmp); bpy.data.meshes.remove(tmp)
bm = bmesh.new(); c = [(TW[0], TW[2]), (TW[1], TW[2]), (TW[1], TW[3]), (TW[0], TW[3])]
lo = [bm.verts.new((*xy(s, u), TWE - TH)) for s, u in c]; hi = [bm.verts.new((*xy(s, u), TWE)) for s, u in c]
bm.faces.new(lo[::-1])
for i in range(4): bm.faces.new((lo[i], lo[(i+1) % 4], hi[(i+1) % 4], hi[i]))
ap = bm.verts.new((*xy((TW[0] + TW[1]) / 2, (TW[2] + TW[3]) / 2), TWZ))
for i in range(4): bm.faces.new((hi[i], hi[(i+1) % 4], ap))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
tmp = bpy.data.meshes.new('cj_tmp'); bm.to_mesh(tmp); bm.free(); out.from_mesh(tmp); bpy.data.meshes.remove(tmp)
info.append(('se_tower_shaft+cap', round((TW[1]-TW[0]-2*TWOV)*(TW[3]-TW[2]-2*TWOV), 1), round(TWE, 2), round(TWZ, 2)))
# curved east wall: band of tall windows just above the loggia roof, 4 pairs, from the PD Commons photo (photo-scaled; sizes UNVERIFIED;
# no lettering — the photo's 'ALEXANDER KASSER THEATER' letters are deliberately NOT modelled)
UC = -ARC[1] / (2 * ARC[0]); WIN = []
zb = EL[1] + EL[0] * WALL + 0.45; zt = zb + 3.9
for pc in (-9.75, -3.25, 3.25, 9.75):
    for off in (-1.4, 1.4):
        uc = UC + pc + off
        if uc - 1.15 < TW[3] + 0.5 or uc + 1.15 > AU1 - 0.5: continue
        WIN.append((uc - 1.15, uc + 1.15))
FR = 0.12
for u0, u1 in WIN:
    bm, _ = box_prism(WALL - 0.10, WALL + 0.05, u0, u1, zb, zt)          # frame box (maroon), proud 5 cm
    for f in bm.faces: f.material_index = 7
    gb, _ = box_prism(WALL - 0.10, WALL + 0.07, u0 + FR, u1 - FR, zb + FR, zt - FR)   # glass, 2 cm proud of the frame
    for f in gb.faces: f.material_index = 6
    for b in (bm, gb):
        tmp = bpy.data.meshes.new('cj_tmp'); b.to_mesh(tmp); b.free(); out.from_mesh(tmp); bpy.data.meshes.remove(tmp)
# south tile eave: the News12 photo shows a projecting red-tile eave over the S-facade arcade; continue the fitted south shed plane
# OV_S beyond the S wall face (u = 0) as a 0.18 m thick tile slab + fascia. Overhang depth UNVERIFIED; starts at s 2.0 (clear of the RHD SE core gap).
OV_S = float(os.environ.get('OV_S', '0.6')); bm = bmesh.new(); s0e, s1e = 2.0, TW[0]
def pz_(u): return SS[1] + SS[0] * u
c4 = [(s0e, -OV_S), (s1e, -OV_S), (s1e, 0.02), (s0e, 0.02)]
hi = [bm.verts.new((*xy(s, u), pz_(u) + 0.01)) for s, u in c4]; lo = [bm.verts.new((*xy(s, u), pz_(u) - 0.18)) for s, u in c4]
bm.faces.new(hi); bm.faces.new(lo[::-1])
for i in range(4): bm.faces.new((lo[i], lo[(i+1) % 4], hi[(i+1) % 4], hi[i]))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
for f in bm.faces: f.material_index = 0 if f.normal.z > 0.2 else 2
for f in bm.faces: f.tag = True
tmp = bpy.data.meshes.new('cj_tmp'); bm.to_mesh(tmp); bm.free(); out.from_mesh(tmp); bpy.data.meshes.remove(tmp)
print('cj south eave slab s', s0e, round(s1e, 2), 'overhang', OV_S, 'z out', round(pz_(-OV_S), 2), flush=True)
print('cj east-wall windows', len(WIN), 'z', round(zb, 2), round(zt, 2), 'u', [round(a, 1) for a, b in WIN], flush=True)
for i in info: print('cj zone', *i, flush=True)
bmesh.ops.remove_doubles(out, verts=out.verts[:], dist=0.003)
out.normal_update()
for f in out.faces:
    if f.material_index in (6, 7): continue
    cz = f.calc_center_median(); s_, u_ = su(cz)
    if u_ < -0.05 and f.normal.z <= 0.2: f.material_index = 2; continue
    if f.normal.z > 0.2: f.material_index = 0
    else: f.material_index = 3
    if f.material_index in (6, 7): continue
    if TWE - TH - 0.02 < f.calc_center_median().z < TWE + 0.02 and f.normal.z < 0.2: f.material_index = 2
# curved-wall top faces -> coping; tag
for f in out.faces:
    s, u = su(f.calc_center_median())
    if f.normal.z > 0.2 and WALL - CWT - 0.05 < s < WALL + 0.05 and TW[3] < u < AU1: f.material_index = 5
# ---------- swap into the roof object
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; old = ro.data
roofc_med = None
if 'roofc' in old.attributes:
    at = old.attributes['roofc']; vals = np.zeros(len(at.data) * 4, np.float32); at.data.foreach_get('color', vals); vals = vals.reshape(-1, 4)
    roofc_med = np.median(vals[vals[:, 3] > 0.02], axis=0) if (vals[:, 3] > 0.02).any() else None; dom = at.domain; dtp = at.data_type
keep = bpy.data.meshes.get('ci2_orig_kasser_roof_hip')
if keep: bpy.data.meshes.remove(keep)
old.name = 'ci2_orig_kasser_roof_hip'; old.use_fake_user = True
me = bpy.data.meshes.new('Alexander Kasser Theater roof (LiDAR massing cj)')
for mat in old.materials: me.materials.append(mat)
while len(me.materials) < 6: me.materials.append(None)
def mk(name, col, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal; return m
me.materials.append(mk('Kasser_window_glass_cj', (0.025, 0.03, 0.035), 0.08, 0.0))      # slot 6 (UNVERIFIED tone)
me.materials.append(mk('Kasser_window_frame_maroon_cj', (0.16, 0.035, 0.03), 0.45, 0.3))  # slot 7, maroon like the RHD SE core frames (photo, UNVERIFIED tone)
out.transform(ro.matrix_world.inverted()); out.to_mesh(me); out.free()
if roofc_med is not None:
    a = me.attributes.new('roofc', dtp, dom); a.data.foreach_set('color', np.tile(roofc_med, len(a.data)).astype(np.float32))
ro.data = me
for nm in ('Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course'):
    o = bpy.data.objects[nm]; o.hide_render = True; o.hide_viewport = True; o.hide_set(True)
mt = bpy.data.materials['Roof_tile_or_membrane__kasser_cg']; nd = mt.node_tree.nodes.get('Math.037')
if nd and nd.operation == 'GREATER_THAN': nd.inputs[1].default_value = float(os.environ.get('NZTH', '0.9935')); print('cj membrane threshold ->', nd.inputs[1].default_value, flush=True)
ro['cj_lidar_massing'] = 'LiDAR massing (cj); old hip mesh = ci2_orig_kasser_roof_hip; hip eave objects hidden'
# ---------- 4a BVH (roof massing + walls) vs RHD npz
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm_ = zz['names']; kp = np.array([not str(nm_[i]).startswith('NT_') for i in ob]); T = T[kp]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world)
    print('cj 4a overlap pairs', o.name, len(BVHTree.FromBMesh(bm).overlap(RB)), flush=True); bm.free()
print('cj massing faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cj main: SAVED', flush=True)
