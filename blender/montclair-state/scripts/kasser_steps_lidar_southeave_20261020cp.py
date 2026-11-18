"""Session cp (Oct 20 ~2:35 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes co; SAVE=1 saves). Run ONLY this script.
RUN ORDER: sets SB=73.20 (env, unless given) and runs scripts/kasser_windows_steps_20261020co.py with SAVE 0 (-> cn -> cm -> cl -> ck -> cj ->
ci2 -> ci -> ch -> cg -> cf), then the cp work:
 1. STEPS BACK ON THE LiDAR LINE: north terrain was clamped first (north/scripts/terrain_clamp_kasser_steps_20261020cp.py PASS 1, north
    saved; it rewrote cm/terrain_steps_cm.npz), so co's one mitred run now starts at the MEASURED plateau edge SB 73.20 (was 73.62) and
    cm flight A refits itself to max(LiDAR, clamped terrain) = the LiDAR line.
 1b. Plaza edge strip on the south segment (closes a slot left by co's delete box once SB < 73.22).
 2. ROLL-UP DOOR WIDTH (News12 photo, refs/bv/x_rhd_fire_news12_20240221.jpg): measured against the arcade bay rhythm (3.3 m pitch ~ 38 px),
    the photo's roll-up door starts ~0.6 m inside arch 1 and runs past the arch 1/2 pier to the photo edge (>= 4.6 m wide, ~3.0-3.4 m tall),
    while cm built 4.2 m (s 3.45-7.65) with cover-panel wall to its east. Door widened to s 3.45-8.85 (5.4 m; east end = cover panel 9.25
    - 0.40 jamb; photo-scaled, UNVERIFIED beyond the photo edge). Height/sill unchanged. The generic windows east of the cover panel are
    OUTSIDE the photo frame: no evidence, left as built.
 3. SOUTH EAVE TILE EDGE COURSE (+ fill of a 0.1-0.2 m slot between the cj shed and the eave slab that showed the arcade skin as a white stripe from above, cp test 3): co's barrel-tile edge (r 0.075, 0.26 m pitch, own terracotta material) along the cj/cl south tile eave,
    placed by ray-casting the eave's outer edge and top surface per tile (UNVERIFIED sizes, Commons/News12 photos show red barrel tile).
4a BVH printed vs the cf RHD npz."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'; os.environ.setdefault('SB', '73.20')
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_windows_steps_20261020co.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
def P3(s, u, z): q = xy(s, u); return Vector((q[0], q[1], z))
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world; rmi = rm.inverted()
wo = bpy.data.objects['Alexander Kasser Theater walls']
names = [x.name if x else None for x in me.materials]; mi = names.index
ROLL, JTM, DFR, APR = mi('Kasser_rollup_door_cm'), mi('Arcade_joint_dark_ck'), None, None
for nm_ in names:
    if nm_ and 'frame' in nm_.lower() and 'door' in nm_.lower(): DFR = mi(nm_)
TILE = mi('Kasser_tile_edge_terracotta_co')
print('cp materials', [names[i] for i in (ROLL, JTM, TILE)], 'door frame', names[DFR] if DFR is not None else None, flush=True)
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
def fsu(f): return [su(v.co) for v in f.verts]
def boxsu(s0, s1, u0, u1, z0, z1, mat):
    c = [(s0, u0), (s1, u0), (s1, u1), (s0, u1)]
    lo = [bm.verts.new(P3(s, u, z0)) for s, u in c]; hi = [bm.verts.new(P3(s, u, z1)) for s, u in c]
    fs = [bm.faces.new(lo), bm.faces.new(hi)] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i])) for i in range(4)]
    for f in fs: f.material_index = mat
    bmesh.ops.recalc_face_normals(bm, faces=fs)
# ---------- 1b. plaza edge on the south segment (cp final 0236 oblique: a black slot along the top riser, cheek -> P1): co's flight-B delete box
# (s 73.15-77.4) also took cn's plaza slab edge face at s 73.22, and co's fill box (73.22 -> SB) closed it only while SB > 73.22; with SB 73.20
# that box is a 0.02 m inverted sliver. Close the edge with a solid strip under the plaza top (same STEP material, top = plaza 131.80).
ST = mi('Arcade_stucco_white_ck'); STEPm = mi('Kasser_step_concrete_cm'); SBv = float(os.environ['SB'])
# cp 0244 oblique still showed the band black: a LEFTOVER old tread/nosing prism at s 73.128-73.498 (top 131.596/131.636, from before co; it
# starts 0.02 m short of co's 73.15 delete box so it survived, hidden under co's fill until SB < 73.22) z-fights the new first tread -> delete it.
SPm = {STEPm, mi('Kasser_step_nosing_cm')}
def _lo(f):
    ss = [s for s, u in fsu(f)]; uu = [u for s, u in fsu(f)]
    if f.material_index not in SPm or max(v.co.z for v in f.verts) > 131.70 or min(uu) < 5.99 or max(uu) > 14.51: return False
    if not all(73.12 < s < 73.50 for s in ss): return False
    return min(ss) < 73.135 or all(abs(s - 73.473) < 0.004 or abs(s - 73.498) < 0.004 for s in ss)
lo_ = [f for f in bm.faces if _lo(f)]
# cp 0249 oblique: a dark square on the cheek top = a LEFTOVER cm cheek top face (s 72.33-72.83, z 132.10; co's ST delete box starts at 72.70)
# coplanar with the new cheek top (72.40-73.30 at SB 73.20) -> delete it
lo_ += [f for f in bm.faces if f.material_index == ST and all(72.30 < s < 72.85 and 5.59 < u < 6.01 for s, u in fsu(f)) and all(abs(v.co.z - 132.10) < 0.005 for v in f.verts) and min(s for s, u in fsu(f)) < 72.35]
print('cp leftover tread faces deleted', len(lo_), flush=True); bmesh.ops.delete(bm, geom=lo_, context='FACES')
if SBv < 73.22:
    boxsu(73.10, 73.22, 6.0, 14.5, 131.45, 131.80, STEPm); print("cp plaza edge strip s 73.10-73.22 (plaza slab ends at 73.15 after the co delete box; 0241 test still showed a 0.02 m slot at 73.15-73.17)", flush=True)
# ---------- 2. roll-up door 4.2 -> 5.4 m
rf = [f for f in bm.faces if f.material_index == ROLL and all(3.3 < s < 7.8 for s, u in fsu(f))]
za = min(v.co.z for f in rf for v in f.verts); uR = [u for f in rf for s, u in fsu(f)]; UW = max(uR) + 0.04
print('cp roll-up faces', len(rf), 'sill %.2f' % za, 'UW %.3f' % UW, flush=True)
def in_door(f, mats):
    if f.material_index not in mats: return False
    return all(3.30 < s < 7.80 and UW - 0.125 < u < UW - 0.025 for s, u in fsu(f)) and all(za - 0.01 < v.co.z < za + 3.52 for v in f.verts)
mats = {ROLL, JTM} | ({DFR} if DFR is not None else set())
dl = [f for f in bm.faces if in_door(f, mats)]
# the east jamb (s 7.65-7.75) only; keep the west jamb at 3.35-3.45
dl = [f for f in dl if f.material_index != DFR or min(s for s, u in fsu(f)) > 7.5 or max(s for s, u in fsu(f)) > 7.70]
print('cp roll-up door faces deleted', len(dl), flush=True)
bmesh.ops.delete(bm, geom=dl, context='FACES')
# grade along the wider span (LiDAR class 1/2, 1.0-3.0 m out) to check the sill
zp = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); gk = (zp['c'] == 1) | (zp['c'] == 2)
GS = (zp['x'][gk] - A[0]) * n[0] + (zp['y'][gk] - A[1]) * n[1]; GU = (zp['x'][gk] - A[0]) * d[0] + (zp['y'][gk] - A[1]) * d[1]; GZ = zp['z'][gk]
kk = (GS > 7.5) & (GS < 9.0) & (GU > UW - 3.0) & (GU < UW - 0.8)
print('cp LiDAR grade s 7.5-9.0 median %.2f vs sill %.2f' % (float(np.median(GZ[kk])) if kk.sum() else -1, za), flush=True)
SE = 8.85
fr_m = DFR if DFR is not None else JTM
boxsu(SE, SE + 0.10, UW - 0.10, UW - 0.03, za, za + 3.50, fr_m); boxsu(3.35, SE + 0.10, UW - 0.10, UW - 0.03, za + 3.40, za + 3.50, fr_m)
boxsu(3.45, SE, UW - 0.06, UW - 0.04, za, za + 3.40, ROLL)
for zr in np.arange(za + 0.08, za + 3.38, 0.08): boxsu(3.45, SE, UW - 0.068, UW - 0.06, zr, zr + 0.012, JTM)
boxsu(3.45, SE, UW - 0.075, UW - 0.06, za, za + 0.06, JTM)
# apron: cm's runs s 3.30-7.95; extend 7.95 -> SE + 0.30 at the same top
APRm = None
ap = [f for f in bm.faces if all(3.2 < s < 8.05 and UW - 0.80 < u < UW - 0.0 for s, u in fsu(f)) and abs(max(v.co.z for v in f.verts) - za) < 0.005 and min(v.co.z for v in f.verts) > za - 0.27 and f.normal.z > 0.9]
if ap: APRm = ap[0].material_index
print('cp apron top faces found', len(ap), 'mat', names[APRm] if APRm is not None else None, flush=True)
if APRm is not None: boxsu(7.95, SE + 0.30, UW - 0.75, UW - 0.03, za - 0.25, za, APRm)
# ---------- 3. south eave barrel-tile edge course
bm.transform(rm.inverted()); bm.to_mesh(me); me.update(); bm.free()
bvh = BVHTree.FromObject(ro, bpy.context.evaluated_depsgraph_get()) if False else None
b2 = bmesh.new(); b2.from_mesh(me); b2.transform(rm); bvh = BVHTree.FromBMesh(b2)
def hit_down(s, u, ztop=137.2):
    r = bvh.ray_cast(P3(s, u, ztop), Vector((0, 0, -1)), 2.0)
    return (r[0].z, r[2]) if r[0] is not None else (None, None)
fmat = {f.index: f.material_index for f in b2.faces}
tiles = []; GAPS = []
for s in np.arange(1.0, 54.5, 0.26):
    # outermost eave point: scan u outward (south = -u) from the face
    ue = None; gap = []; zin = []
    for u in np.arange(UW + 0.6, UW - 1.2, -0.02):
        z, fi = hit_down(s, u)
        if z is not None and 135.0 < z < 137.0 and fmat[fi] == 0:
            ue = u
            if UW - 0.25 < u < UW + 0.6: zin.append((u, z))
        elif z is not None and UW - 0.2 < u < UW + 0.45 and z < 135.7: gap.append(u)   # cp test 3: a 0.1-0.2 m slot between the cj shed and the eave slab shows the arcade skin top (white stripe from above)
    if gap and len(zin) > 4: GAPS.append((s, min(gap), max(gap), np.polyfit([a for a, b in zin], [b for a, b in zin], 1)))
    if ue is None: continue
    zi, _ = hit_down(s, ue + 0.30); ze, _ = hit_down(s, ue + 0.02)
    if zi is None or ze is None or zi < ze: continue
    tiles.append((s, ue, ze, zi))
print('cp south eave tile positions', len(tiles), 's %.2f..%.2f' % (tiles[0][0], tiles[-1][0]) if tiles else '', flush=True)
bm = b2; r = 0.075
# fill the shed/eave slot: a 0.04 m terracotta strip on the fitted shed plane, 0.08 m past the slot each side, per 0.26 m of s (own tile-edge material:
# new faces have no 'roofc' attribute for the roof tile shader)
for s, g0, g1, (k1, k0) in GAPS:
    for u0_, u1_ in ((g0 - 0.08, g1 + 0.08),):
        z0 = k1 * u0_ + k0; z1 = k1 * u1_ + k0
        c = [(s - 0.135, u0_, z0), (s + 0.135, u0_, z0), (s + 0.135, u1_, z1), (s - 0.135, u1_, z1)]
        hi = [bm.verts.new(P3(a, b, zz + 0.012)) for a, b, zz in c]; lo = [bm.verts.new(P3(a, b, zz - 0.03)) for a, b, zz in c]
        fs = [bm.faces.new(hi), bm.faces.new(lo[::-1])] + [bm.faces.new((lo[i], lo[(i + 1) % 4], hi[(i + 1) % 4], hi[i])) for i in range(4)]
        for f in fs: f.material_index = TILE
        bmesh.ops.recalc_face_normals(bm, faces=fs)
print('cp shed/eave slot fill strips', len(GAPS), 's %.2f..%.2f' % (GAPS[0][0], GAPS[-1][0]) if GAPS else '', 'slot u %.2f..%.2f' % (min(g[1] for g in GAPS), max(g[2] for g in GAPS)) if GAPS else '', flush=True)
for s, ue, ze, zi in tiles:
    rings = []
    for u, z in ((ue - 0.02, ze - (zi - ze) * 0.04 / 0.28), (ue + 0.30, zi)):
        rings.append([bm.verts.new(P3(s + r * math.cos(math.pi * j / 8), u, z + r * 0.9 * math.sin(math.pi * j / 8))) for j in range(9)])
    A_, B_ = rings
    fs = [bm.faces.new(A_), bm.faces.new(B_[::-1])] + [bm.faces.new((A_[j], A_[j + 1], B_[j + 1], B_[j])) for j in range(8)] + [bm.faces.new((A_[8], A_[0], B_[0], B_[8]))]
    for f in fs: f.material_index = TILE
    bmesh.ops.recalc_face_normals(bm, faces=fs)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['cp_steps_rollup_tiles'] = 'cp: steps SB %s (LiDAR edge) after the north clamp; roll-up s 3.45-%.2f; south eave tile edge %d' % (os.environ['SB'], SE, len(tiles))
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b3 = bmesh.new(); b3.from_mesh(o.data); b3.transform(o.matrix_world)
    print('cp 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b3).overlap(RBV)), flush=True); b3.free()
for nm, s, u, z, ts, tu, tz in (('stile', 30.0, -6.5, 133.2, 33.0, 0.0, 135.9), ('rollup', 6.0, -14.0, 129.8, 6.2, 0.0, 130.6)):
    L_ = P3(s, u, z); T_ = P3(ts, tu, tz); print('cp CAM', nm, 'LOC=%.2f,%.2f,%.2f TGT=%.2f,%.2f,%.2f' % (*L_, *T_), flush=True)
print('cp roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cp main: SAVED', flush=True)
