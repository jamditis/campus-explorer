"""Session cq (Oct 20 ~3:40 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cp; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_steps_lidar_southeave_20261020cp.py with SAVE 0 (-> co -> cn -> cm -> cl -> ck -> cj -> ci2 -> ci -> ch -> cg -> cf),
then the cq work:
 1. SOUTH ROOF JOIN: the cj shed (roof face 0, s 1.80-46.57, + face 36, s 46.57-53.07) ended at a drifting outer edge u 0.006 -> 0.279 while the
    eave slab (408 / 4630) ends at u 0.020, leaving a 0-0.26 m slot that cp covered with 179 0.04 m terracotta strips (1074 faces; a light band
    from above). cq deletes the strips, moves the shed's outer-edge verts (and the vertical stucco skirt under that edge) onto u 0.020 ON the
    shed plane (z = a x + b y + c, rms 4e-6), snaps the slab top verts onto the same plane (was up to 0.010 m off at s 2), deletes the slab's
    inner side faces (412, 4634; now internal) and welds coincident verts -> one continuous roof plane from the eave edge (u -0.60) to the
    set-back wall (u 3.25). The s 46.57-53.67 slab top (4630) was maroon from above; it becomes roof tile (roofc copied from 408's verts) and the
    cp tile-edge tiles there (which sat on the old shed edge, u ~0.26) slide out along the plane to the real eave edge (u ~-0.58) like s < 46.57.
 2. LEFTOVER AUDIT at the steps / cheeks / plaza edge (cm/cn/co/cp delete boxes): coplanar overlapping faces in the step zone (s > 54 or the
    east front), by plane bins + interior sample tests; a face fully covered by a coplanar face of the same surface role is deleted.
 3. 4a BVH vs the cf RHD npz (must be 0 pairs)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector, geometry
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_steps_lidar_southeave_20261020cp.py', run_name='__main__')
A = G['A']; d = G['d']; n = G['n']; su = G['su']; P3 = G['P3']
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']
names = [x.name if x else None for x in me.materials]; mi = names.index
TILE = mi('Kasser_tile_edge_terracotta_co'); WST = mi('Wall_stucco_mission')
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
rc = bm.verts.layers.float_color.get('roofc')
def fsu(f): return [su(v.co) for v in f.verts]
# ---------- 1a. delete cp's slot strips (6-face boxes, TILE material, all u in [-0.1, 0.45]); tiles have 9-vert rings / u < -0.2 or > 0.25 rings
strip = [f for f in bm.faces if f.material_index == TILE and len(f.verts) == 4 and all(-0.1 < u < 0.45 for s, u in fsu(f)) and all(135.85 < v.co.z < 136.10 for v in f.verts)]
sv = {v for f in strip for v in f.verts}
print('cq slot strip faces deleted', len(strip), flush=True)
bmesh.ops.delete(bm, geom=strip, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in sv if v.is_valid and not v.link_faces], context='VERTS')
bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
# identify faces by geometry (indices shift after deletes)
def find(mat, smin, smax, umin, umax, nz=None, nv=None):
    out = []
    for f in bm.faces:
        if f.material_index != mat or (nv and len(f.verts) != nv): continue
        ss = fsu(f); s_ = [a for a, b in ss]; u_ = [b for a, b in ss]
        if abs(min(s_) - smin) < 0.03 and abs(max(s_) - smax) < 0.03 and abs(min(u_) - umin) < 0.01 and abs(max(u_) - umax) < 0.01:
            if nz is None or (f.normal.z > 0.9) == nz: out.append(f)
    return out
shed0 = find(0, 1.80, 46.57, 0.006, 3.250); shed36 = find(0, 46.57, 53.07, 0.245, 3.250)
slab = find(0, 2.00, 46.57, -0.600, 0.020, nz=True); MAR = mi('Kasser_window_frame_maroon_cj')
slab2 = find(MAR, 46.57, 53.67, -0.600, 0.020, nz=True)
in1 = [f for f in find(WST, 2.00, 46.57, 0.020, 0.020) if f.normal.z < 0.1]; in2 = [f for f in find(MAR, 46.57, 53.67, 0.020, 0.020) if f.normal.z < 0.1]
print('cq found shed', len(shed0), len(shed36), 'slab', len(slab), len(slab2), 'slab inner sides', len(in1), len(in2), flush=True)
assert len(shed0) == 1 and len(shed36) == 1 and len(slab) == 1 and len(slab2) == 1
P = np.array([v.co[:] for v in shed0[0].verts]); M = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]; K = np.linalg.lstsq(M, P[:, 2], rcond=None)[0]
def zpl(x, y): return K[0] * x + K[1] * y + K[2]
UJ = 0.020
edge = [v for f in (shed0[0], shed36[0]) for v in f.verts if su(v.co)[1] < 0.30]
moved = 0; skirt_bot = set()
for v in set(edge):
    s, u = su(v.co); q = P3(s, UJ, 0); v.co = Vector((q[0], q[1], zpl(q[0], q[1]))); moved += 1
    for f in v.link_faces:
        if f.material_index == WST and abs(f.normal.z) < 0.1:
            for w in f.verts:
                if w.co.z < 135.45 and all(g.material_index == WST for g in w.link_faces): skirt_bot.add(w)
for w in skirt_bot:
    s, u = su(w.co)
    if 0.0 < u < 0.31: q = P3(s, UJ, 0); w.co = Vector((q[0], q[1], w.co.z))
print('cq shed edge verts moved to u %.3f on the shed plane' % UJ, moved, 'skirt bottom verts moved', len(skirt_bot), flush=True)
# slab tops onto the plane
mx = 0
for f in (slab[0], slab2[0]):
    for v in f.verts:
        z = zpl(v.co.x, v.co.y); mx = max(mx, abs(v.co.z - z)); dz = z - v.co.z
        v.co.z = z
print('cq slab top verts snapped to the shed plane, max move %.4f' % mx, flush=True)
# roofc for the s 46.57-53.67 slab top -> copy from slab 408 verts (same u side), material -> roof
if rc is not None:
    ref = {round(su(v.co)[1], 2): v[rc][:] for v in slab[0].verts}
    for v in slab2[0].verts:
        k = min(ref, key=lambda r: abs(r - su(v.co)[1])); v[rc] = ref[k]
    print('cq roofc copied to slab2 verts', {k: tuple(round(c, 3) for c in vv) for k, vv in ref.items()}, flush=True)
slab2[0].material_index = 0
bmesh.ops.delete(bm, geom=in1 + in2, context='FACES')
ev = [v for v in set(edge) if v.is_valid] + [v for f in (slab[0], slab2[0]) for v in f.verts]
r = bmesh.ops.remove_doubles(bm, verts=list(set(ev)), dist=0.003)
print('cq weld done', flush=True)
# tiles s > 46.5 sat on the old shed edge (u ~0.26): slide out along the plane to the slab edge like s < 46.57
dzdu = K[0] * d[0] + K[1] * d[1]
# cq dry run 2: without an s/u/z cap this also caught co's EAST-front tile course (1309 faces) -> south eave s 46.45-53.8 only
tf = [f for f in bm.faces if f.material_index == TILE and all(46.45 < s < 53.8 and 0.15 < u < 0.70 for s, u in fsu(f)) and all(135.85 < v.co.z < 136.30 for v in f.verts)]
tv = {v for f in tf for v in f.verts}
ref_u = [min(u for s, u in fsu(f)) for f in bm.faces if f.material_index == TILE and len(f.verts) == 9 and all(20 < s < 46 for s, u in fsu(f))]
UT = float(np.percentile(ref_u, 10)) if ref_u else -0.603   # ring A (outer) of each reference tile; the median mixed in ring B (u +0.32) -> -0.443 in save 2
# per tile (connected island): cq save 1 used ONE shift from the global min u (a transition tile at u ~0.08) -> tiles landed 0.18 m inboard
isl = []; seen = set()
for f in tf:
    if f in seen: continue
    comp = set(); st = [f]
    while st:
        g = st.pop()
        if g in comp: continue
        comp.add(g); seen.add(g)
        for v in g.verts:
            for h in v.link_faces:
                if h.material_index == TILE and h not in comp: st.append(h)
    isl.append(comp)
DUs = []
for comp in isl:
    vs = {v for g in comp for v in g.verts}; mu = min(su(v.co)[1] for v in vs); DU = UT - mu; DUs.append(DU)
    for v in vs:
        s, u = su(v.co); q = P3(s, u + DU, 0); v.co = Vector((q[0], q[1], v.co.z + dzdu * DU))
DU = float(np.mean(DUs)) if DUs else 0
print('cq per-tile shifts: tiles', len(isl), 'du min %.3f max %.3f' % (min(DUs), max(DUs)) if DUs else '', 'target ring u %.3f' % UT, flush=True)
print('cq tiles s>46.5 slid out: faces', len(tf), 'verts', len(tv), 'du %.3f dz %.4f' % (DU, dzdu * DU), flush=True)
# ---------- 2. leftover audit in the step zone
STEPm = mi('Kasser_step_concrete_cm'); NOS = mi('Kasser_step_nosing_cm'); ST = mi('Arcade_stucco_white_ck'); APR = mi('Kasser_apron_concrete_cm')
FLR = mi('Arcade_concrete_floor_ck'); CURB = mi('Arcade_concrete_curb_ck'); RAIL = mi('Arcade_rail_maroon_ck')
AUD = {STEPm, NOS, ST, APR, FLR, CURB}
bm.faces.ensure_lookup_table()
cand = []
for f in bm.faces:
    if f.material_index not in AUD or f.calc_area() < 1e-4: continue
    ss = fsu(f); s_ = [a for a, b in ss]
    if max(v.co.z for v in f.verts) > 133.0 or min(s_) < 54.0: continue
    cand.append(f)
bins = {}
for f in cand:
    nn = f.normal.normalized(); c = f.calc_center_median(); off = nn.dot(c)
    key = (round(nn.x, 2), round(nn.y, 2), round(nn.z, 2), round(off / 0.004))
    bins.setdefault(key, []).append(f)
def tris(f): return [(f.verts[0].co, f.verts[i].co, f.verts[i + 1].co) for i in range(1, len(f.verts) - 1)]
def inside(p, f, nn):
    for a, b, c in tris(f):
        if geometry.intersect_point_tri(p, a, b, c): return True
    return False
def samples(f):
    c = f.calc_center_median(); out = [c]
    for v in f.verts: out.append(c.lerp(v.co, 0.8))
    return out
pairs = []; dele = set()
for key, fs in bins.items():
    if len(fs) < 2: continue
    # include neighbours in adjacent offset bins
    for k2 in ((key[0], key[1], key[2], key[3] + 1),):
        fs = fs + bins.get(k2, [])
    for i, f in enumerate(fs):
        for g in fs[i + 1:]:
            if f is g or not f.is_valid or not g.is_valid: continue
            if set(f.verts) == set(g.verts): pairs.append((f, g, 'same verts')); continue
            nn = f.normal
            sf = samples(f); sg = samples(g)
            ff = sum(inside(p - nn * nn.dot(p - g.verts[0].co), g, nn) for p in sf); gg = sum(inside(p - nn * nn.dot(p - f.verts[0].co), f, nn) for p in sg)
            if ff >= 2 or gg >= 2:
                pairs.append((f, g, '%d/%d %d/%d' % (ff, len(sf), gg, len(sg))))
print('cq audit candidates', len(cand), 'coplanar overlapping pairs', len(pairs), flush=True)
for f, g, why in pairs:
    def desc(x):
        ss = fsu(x); s_ = [a for a, b in ss]; u_ = [b for a, b in ss]; z_ = [v.co.z for v in x.verts]
        return '%s nv%d s %.3f-%.3f u %.3f-%.3f z %.3f-%.3f n %.2f,%.2f,%.2f a %.4f' % (names[x.material_index], len(x.verts), min(s_), max(s_), min(u_), max(u_), min(z_), max(z_), *x.normal, x.calc_area())
    print('  PAIR', why, '|', desc(f), '||', desc(g), flush=True)
    # cq dry run 1: a blanket 'covered -> delete' rule took nosing tops/fronts (intended 1-4 mm overlays on the treads) -> explicit rules only
    if {f.material_index, g.material_index} == {STEPm, ST}:
        stp, wal = (f, g) if f.material_index == STEPm else (g, f)
        nn = stp.normal
        if all(inside(p - nn * nn.dot(p - wal.verts[0].co), wal, nn) for p in samples(stp)): dele.add(stp)   # (b) flight-A step side inside the cheek wall plane
# (a) leftover cheek box (pre-cp SB 73.62 position minus 0.072: s 72.328-76.533, u 5.6-6.0; cp removed only its top at 72.33-72.83)
seed = [f for f in bm.faces if f.material_index == ST and all(5.59 < u < 6.01 for s, u in fsu(f)) and abs(min(s for s, u in fsu(f)) - 72.328) < 0.01]
comp = set(); stack = list(seed)
while stack:
    f = stack.pop()
    if f in comp: continue
    comp.add(f)
    for v in f.verts:
        for g in v.link_faces:
            if g not in comp and g.material_index == ST: stack.append(g)
print('cq leftover cheek component faces', len(comp), 'u range %.3f..%.3f' % (min(su(v.co)[1] for f in comp for v in f.verts), max(su(v.co)[1] for f in comp for v in f.verts)) if comp else '', 's range %.3f..%.3f' % (min(su(v.co)[0] for f in comp for v in f.verts), max(su(v.co)[0] for f in comp for v in f.verts)) if comp else '', flush=True)
if comp and len(comp) <= 24 and all(5.59 < su(v.co)[1] < 6.01 for f in comp for v in f.verts): dele |= comp
# (c) co's inverted fill sliver (s 73.20-73.22) under/inside cp's plaza edge strip
sl = [f for f in bm.faces if f.material_index == STEPm and all(73.195 < s < 73.225 and 5.99 < u < 14.51 for s, u in fsu(f)) and all(131.44 < v.co.z < 131.81 for v in f.verts)]
print('cq co fill sliver faces', len(sl), flush=True); dele |= set(sl)
dele = [f for f in dele if f.is_valid]
print('cq audit leftover faces deleted (fully covered by a coplanar face)', len(dele), flush=True)
bmesh.ops.delete(bm, geom=dele, context='FACES')
# (d) cp's plaza edge strip started at s 73.10, 0.05 m under the plaza slab top (ends 73.153): start it at 73.153 (no coplanar overlap)
mv = [v for v in bm.verts if abs(su(v.co)[0] - 73.10) < 0.003 and 5.99 < su(v.co)[1] < 14.51 and 131.44 < v.co.z < 131.81 and all(g.material_index == STEPm for g in v.link_faces)]
for v in mv:
    s, u = su(v.co); q = P3(73.153, u, 0); v.co = Vector((q[0], q[1], v.co.z))
print('cq plaza edge strip start verts moved 73.10 -> 73.153', len(mv), flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['cq_south_roof_join'] = 'cq: shed edge -> u %.3f on the shed plane, slab joined, %d slot strips removed, %d audit leftovers deleted' % (UJ, len(strip) // 6, len(dele))
# ---------- 3. 4a
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
for o in (ro, wo):
    b3 = bmesh.new(); b3.from_mesh(o.data); b3.transform(o.matrix_world)
    print('cq 4a overlap pairs', o.name, len(BVHTree.FromBMesh(b3).overlap(RBV)), flush=True); b3.free()
# section check of the joined roof: ray down at u -0.5..3.2 every 0.05 at s 5/20/35/50: lowest hit z must follow the plane (no slot)
b4 = bmesh.new(); b4.from_mesh(me); b4.transform(rm); bv = BVHTree.FromBMesh(b4)
for S in (2.5, 5.0, 8.0, 20.0, 35.0, 46.0, 47.0, 50.0, 52.8):
    bad = 0; tot = 0
    for u in np.arange(-0.55, 3.2, 0.05):
        p = P3(S, u, 138.5); h = bv.ray_cast(p, Vector((0, 0, -1)), 4.0); tot += 1
        if u < 0.6 and (h[0] is None or h[0].z < 135.7): bad += 1
    print('cq roof section s %.2f: %d/%d rays at u -0.55..0.6 reach below 135.7 (slot to the arcade skin)' % (S, bad, tot), flush=True)
b4.free()
print('cq roof faces', len(me.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cq main: SAVED', flush=True)
