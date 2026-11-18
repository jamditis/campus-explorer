"""Session ci2 (Oct 19 ~7:45 PM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes ci as entry; SAVE=1 saves).
RUN ORDER: runs scripts/kasser_ridge_coping_hip_20261019ci.py first (SAVE forced 0 -> ch -> cg -> cf), THEN, in the roof object mesh:
 1) (kept, harmless) SE-jog area: east-end tile verts (mat 0, s > 34, not eave-attached) that the ci envelope snap dropped below the tile eave
    height ZE (134.11 m MEASURED, ch) are lifted to ZE, so the tile no longer dips into a pit below the wall top. NOTE: the visible dark notch at the SE jog is the tile valley behind the 137.8 m jog
    eave band, NOT fixed by this (the JOG=1 'cricket' lift was tested and opened a hole -> default off).
 2) NE corner grey wedge: the roof shader paints faces with normal z > threshold as membrane grey; east-end mat-0 faces that are flat at
    the eave height (normal z > FLATN) are re-assigned to the eave tile material (slot 1, 'Eave_tile_top_soffit_under__kasser_cg').
Idempotent (each run starts from the ci state). 4a BVH printed for the roof vs the cf npz (trees excluded)."""
import bpy, bmesh, os, runpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_ridge_coping_hip_20261019ci.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(x, y): p = np.array([x, y]) - A; return float(p @ n), float(p @ d)
ZE = float(os.environ.get('ZE', '134.11')); FLATN = float(os.environ.get('FLATN', '0.95'))
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; M = ro.matrix_world.copy(); Mi = M.inverted()
bm = bmesh.new(); bm.from_mesh(me); bm.transform(M); bm.normal_update()
def eaveatt(v): return any(f.material_index != 0 for f in v.link_faces)
east = [f for f in bm.faces if f.material_index == 0 and su(*f.calc_center_median().xy)[0] > 34]
lift = []
for v in set(v for f in east for v in f.verts):
    if eaveatt(v) or v.co.z >= ZE: continue
    lift.append(ZE - v.co.z); v.co.z = ZE
# jog pocket: tile behind the S-facade jog eave band sat up to ~5 m below the band top (dark pit). Lift tile verts to a 31 deg
# 'cricket' surface falling away from the band's top line: z >= ZB - tan(31 deg) * xy-distance to the band top edges (jog region only).
ZB = float(os.environ.get('ZB', '137.83')); TANP = np.tan(np.radians(30.96)); JOG = os.environ.get('JOG', '0') == '1'   # ci2 test t3: JOG=1 opened a hole + pale triangles at the jog -> OFF (notch NOT fixed)
segs = []
for e in bm.edges:
    if not e.is_boundary or e.link_faces[0].material_index != 2: continue
    c = (e.verts[0].co + e.verts[1].co) / 2; s_, u_ = su(c.x, c.y)
    if 48 < s_ < 60 and 0 < u_ < 10 and abs(c.z - ZB) < 0.35: segs.append((np.array(e.verts[0].co.xy[:]), np.array(e.verts[1].co.xy[:])))
def dseg(p):
    best = 1e9
    for a, b in segs:
        ab = b - a; t = np.clip((p - a) @ ab / max(ab @ ab, 1e-12), 0, 1); best = min(best, float(np.linalg.norm(p - (a + t * ab))))
    return best
jl = []
if JOG and segs:
    for v in set(v for f in east for v in f.verts):
        if eaveatt(v): continue
        s_, u_ = su(v.co.x, v.co.y)
        if not (44 < s_ < 62 and -2 < u_ < 14): continue
        zc = ZB - TANP * dseg(np.array(v.co.xy[:]))
        if zc > v.co.z + 0.01: jl.append(zc - v.co.z); v.co.z = zc
print('ci2 jog band top segs', len(segs), 'cricket-lifted verts', len(jl), 'max', round(max(jl), 3) if jl else 0, flush=True)
bm.normal_update()
flat = [f for f in east if f.normal.z > FLATN]
for f in flat: f.material_index = 1
print('ci2 lifted', len(lift), 'max', round(max(lift), 3) if lift else 0, '| flat east faces -> eave tile', len(flat), round(sum(f.calc_area() for f in flat), 2), 'm2', flush=True)
z = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = z['tris']; ob = z['obj']; nm = z['names']; kp = np.array([not str(nm[i]).startswith('NT_') for i in ob]); T = T[kp]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
print('ci2 4a roof overlap pairs', len(BVHTree.FromBMesh(bm).overlap(RB)), flush=True)
bm.transform(Mi); bm.to_mesh(me); bm.free(); me.update()
ro['ci2_jog_wedge'] = f'lifted {len(lift)} verts to {ZE}; {len(flat)} flat east faces -> slot 1'
if SAVE: bpy.ops.wm.save_mainfile(); print('ci2 main: SAVED', flush=True)
