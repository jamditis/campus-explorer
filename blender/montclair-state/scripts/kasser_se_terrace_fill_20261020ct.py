"""Session ct (Oct 20 ~6:40 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cs; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_south_downpipes_20261020cs.py with SAVE 0 (-> cr -> cq -> ... -> cf; SB 73.20), then the ct work:
 SE TERRACE FILL: the cs match view (Commons 13252662863, CC BY-SA 2.0, 2014) showed a green pocket between the plaza and Kasser's
 SE corner where the photo has one continuous low white wall from the pavilion to the front steps with the terrace behind it.
 LiDAR (data/pts_crop.npz, class 1) is a flat plateau at 131.8-131.9 m over that whole pocket (x -191..-180, y -50..-58), while main had
 only DTM terrain at 129.3-130.3 there: cl's terrace slab stopped at s 61.0 and the front-steps plaza starts near s 68. So the terrace is
 continued: 0.25 m cells in the Kasser s/u frame over s 60.9-70.5, u 0.96-15 that are (a) on the LiDAR plateau (median 131.6-132.05,
 MEASURED) and (b) not already covered by built geometry above 131.3 (roof-object/walls ray cast from 133.2 down; terrain ignored);
 top at TERR 131.87 (cl, MEASURED), stucco side faces down to 128.3 only on boundary edges whose neighbour is lower than 131.5
 (so the wall face toward the plaza reads as one continuous white wall), coping + the same open maroon rail as cl along south-facing
 boundary edges (rail form UNVERIFIED placeholder, as cl). All geometry goes into the Kasser roof mesh (north picks it up through the
 ce link). 4a BVH vs the cf RHD npz (must be 0 pairs)."""
import bpy, bmesh, os, runpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_south_downpipes_20261020cs.py', run_name='__main__')
su = G['su']; P3 = G['P3']
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']
names = [x.name if x else None for x in me.materials]
ARC_ST, FLM, RLM = names.index('Arcade_stucco_white_ck'), names.index('Arcade_concrete_floor_ck'), names.index('Arcade_rail_maroon_ck')
TERR = 131.87; Z0 = 128.3; C = 0.25
S0, S1, U0, U1 = 60.9, 72.4, 0.96, 15.0   # ct t1: extended 70.5 -> 72.4 (green notch up to the front-steps cheek at s 72.40)
def wbvh(o):
    b = bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t = BVHTree.FromBMesh(b); b.free(); return t
# remove previous ct faces (idempotent; chain rebuilds anyway, but keep guard)
RB = wbvh(ro); WB = wbvh(wo)
others = [wbvh(bpy.data.objects[n]) for n in ('COLE_plaza_deck_bs', 'COLE_plaza_edge_bs') if n in bpy.data.objects]
z = np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); px, py, pz, pc = z['x'], z['y'], z['z'], z['c']
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
m = (pc == 1) | (pc == 2)
PS = (px - A[0]) * n[0] + (py - A[1]) * n[1]; PU = (px - A[0]) * d[0] + (py - A[1]) * d[1]
k = m & (PS > S0 - 1) & (PS < S1 + 1) & (PU > U0 - 1) & (PU < U1 + 1); PS, PU, PZ = PS[k], PU[k], pz[k]
ns, nu = int(round((S1 - S0) / C)), int(round((U1 - U0) / C))
DN = Vector((0, 0, -1))
def built_top(s, u):
    q = P3(s, u, 133.2); best = None
    for t in (RB, WB, *others):
        h = t.ray_cast(q, DN, 6.0)
        if h[0] is not None and (best is None or h[0].z > best): best = h[0].z
    return best
Q = np.zeros((ns, nu), bool); TOP = np.full((ns, nu), np.nan)
for i in range(ns):
    for j in range(nu):
        s = S0 + (i + 0.5) * C; u = U0 + (j + 0.5) * C
        kk = (np.abs(PS - s) < 0.5) & (np.abs(PU - u) < 0.5)
        bt = built_top(s, u); TOP[i, j] = bt if bt is not None else -1
        if kk.sum() < 2: continue
        med = float(np.median(PZ[kk]))
        if 131.6 <= med <= 132.05 and (bt is None or bt < 131.3): Q[i, j] = True
# regularise (ct dry 1: LiDAR-only mask gave a ragged south edge at u 4.5-4.9 and islands): s <= 63.4 -> fill from u 2.21 (j 5);
# s > 63.4 -> fill from u 4.71 (j 15); cells u 2.21-4.71 at s > 63.4 = a LOWER paved landing at the zone's LiDAR median (MEASURED)
SJ = int(round((63.4 - S0) / C)); Q2 = np.zeros_like(Q)
for i in range(ns):
    for j in range(nu):
        if TOP[i, j] > 131.3: Q[i, j] = False; continue
        if i < SJ and j >= 5 and j <= 22: Q[i, j] = True
        if i >= SJ:
            if 15 <= j <= 20: Q[i, j] = True
            elif j < 15 and j >= 5:
                Q[i, j] = False; Q2[i, j] = TOP[i, j] < 129.5
            elif j > 20:
                Q[i, j] = Q[i, j - 1] and (Q[i, j] or S0 + i * C >= 70.4)   # east of s 70.4: column-fill north up to the first built cell
for i in range(ns):
    for j in range(nu):
        if Q[i, j] and sum(Q[a, b] for a, b in ((i-1, j), (i+1, j), (i, j-1), (i, j+1)) if 0 <= a < ns and 0 <= b < nu) < 2: Q[i, j] = False
kz = (PS > 63.4) & (PS < S1) & (PU > 2.3) & (PU < 4.6); Z2 = float(np.median(PZ[kz])) if kz.sum() > 5 else 130.8
print('ct lower landing LiDAR median', round(Z2, 2), 'n', int(kz.sum()), 'p10/p90', np.round(np.percentile(PZ[kz], [10, 90]), 2) if kz.sum() > 5 else None, flush=True)
print('ct terrace cells', int(Q.sum()), 'area m2', round(Q.sum() * C * C, 1), flush=True)
for j in range(nu - 1, -1, -2): print('ct U%5.2f ' % (U0 + j * C), ''.join('#' if Q[i, j] else ('=' if Q2[i, j] else ('b' if TOP[i, j] > 131.3 else '.')) for i in range(ns)), flush=True)
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
nf0 = len(bm.faces)
VV = {}
def vt(i, j, zz):
    key = (i, j, round(zz, 3))
    if key not in VV: VV[key] = bm.verts.new(P3(S0 + i * C, U0 + j * C, zz))
    return VV[key]
for i in range(ns):
    for j in range(nu):
        if Q[i, j]:
            f = bm.faces.new((vt(i, j, TERR), vt(i + 1, j, TERR), vt(i + 1, j + 1, TERR), vt(i, j + 1, TERR)))
            f.material_index = FLM
for i in range(ns):
    for j in range(nu):
        if Q2[i, j]:
            f = bm.faces.new((vt(i, j, Z2), vt(i + 1, j, Z2), vt(i + 1, j + 1, Z2), vt(i, j + 1, Z2))); f.material_index = FLM
            for (di, dj, a, b) in ((0, -1, (i, j), (i + 1, j)), (1, 0, (i + 1, j), (i + 1, j + 1)), (0, 1, (i + 1, j + 1), (i, j + 1)), (-1, 0, (i, j + 1), (i, j))):
                ii, jj = i + di, j + dj
                if 0 <= ii < ns and 0 <= jj < nu and (Q[ii, jj] or Q2[ii, jj] or TOP[ii, jj] > Z2): continue
                bm.faces.new((vt(*a, Z0), vt(*b, Z0), vt(*b, Z2), vt(*a, Z2))).material_index = ARC_ST
def low(i, j):
    if 0 <= i < ns and 0 <= j < nu:
        return (not Q[i, j]) and (TOP[i, j] < TERR - 0.01 or Q2[i, j])   # ct f1: was < 131.5 -> a 7 cm open step showed dark where the terrace meets the 131.80 front plaza
    return True
nside = 0; south_edges = []
for i in range(ns):
    for j in range(nu):
        if not Q[i, j]: continue
        for (di, dj, a, b) in ((0, -1, (i, j), (i + 1, j)), (1, 0, (i + 1, j), (i + 1, j + 1)), (0, 1, (i + 1, j + 1), (i, j + 1)), (-1, 0, (i, j + 1), (i, j))):
            if low(i + di, j + dj):
                f = bm.faces.new((vt(*a, Z0), vt(*b, Z0), vt(*b, TERR), vt(*a, TERR))); f.material_index = ARC_ST; nside += 1
                if dj == -1: south_edges.append((i, j))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[nf0:])
def box(s0, s1, u0, u1, z0, z1, mat):
    vs = [bm.verts.new(P3(s, u, zz)) for zz in (z0, z1) for (s, u) in ((s0, u0), (s1, u0), (s1, u1), (s0, u1))]
    for q in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new([vs[x] for x in q]).material_index = mat
# coping + rail along south-facing boundary runs (merge consecutive cells with same j)
runs = []
for (i, j) in sorted(south_edges, key=lambda t: (t[1], t[0])):
    if runs and runs[-1][2] == j and runs[-1][1] == i: runs[-1][1] = i + 1
    else: runs.append([i, i + 1, j])
for i0, i1, j in runs:
    sa, sb, uu = S0 + i0 * C, S0 + i1 * C, U0 + j * C
    if sb - sa < 0.5: continue
    box(sa, sb, uu - 0.04, uu + 0.06, TERR - 0.02, TERR + 0.08, ARC_ST)
    for sp in np.arange(sa + 0.15, sb, 1.5): box(sp - 0.025, sp + 0.025, uu + 0.10, uu + 0.15, TERR + 0.08, TERR + 1.07, RLM)
    box(sa, sb, uu + 0.09, uu + 0.16, TERR + 1.02, TERR + 1.07, RLM)
    for zr in (TERR + 0.25, TERR + 0.55, TERR + 0.82): box(sa, sb, uu + 0.115, uu + 0.135, zr, zr + 0.025, RLM)
print('ct faces added', len(bm.faces) - nf0, 'sides', nside, 'south runs', [(round(S0 + a * C, 2), round(S0 + b * C, 2), round(U0 + j * C, 2)) for a, b, j in runs], flush=True)
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
ro['ct_se_terrace_fill'] = 'ct: SE terrace continued s %.1f-%.1f on the LiDAR plateau (%d cells, top %.2f MEASURED), rail UNVERIFIED' % (S0, S1, int(Q.sum()), TERR)
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(T))])
for o in (ro, wo):
    print('ct 4a overlap pairs', o.name, len(wbvh(o).overlap(RBV)), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('ct main kasser: SAVED', flush=True)
