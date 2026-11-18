"""wy fix2: lift the WU (and WT) north-edge verts in the Reid-hole x-range
onto the 2017 DTM / shared WF edge.

wu_fix snapped WU's open north edge to the skirt (because WF had a hole there)
before wu_fix3 faded the band. Restoring pre_fix3 undid the fade but left that
original skirt snap, so the y=320 seam was still up to ~48 cm low at x83-89.
This pass sets those verts to DTM and matches the shared y=320 edge to WF.
Grass in the same band is moved by the same delta. No new faces.
"""
import bpy, json, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
SAVE = os.environ.get('SAVE') == '1'
PN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
WUN = 'WU_richardson_reid_LiDAR_patch_UNVERIFIED'
WTN = 'WT_richardson_west_LiDAR_patch_UNVERIFIED'
X0, Y0 = 50.0, 320.0
GX0, GY0 = 40, 140
xmin, xmax = 67.0, 111.0
O = bpy.data.objects
rep = json.load(open('data/wy/fix_report.json'))

D = np.load('data/wf/east_dorm_dtm_1m.npz')
filled = D['dtm_filled']; H, W = filled.shape

def hcell(i, j):
    zs = []
    for jj in (j - 1, j):
        for ii in (i - 1, i):
            if 0 <= ii < W and 0 <= jj < H and np.isfinite(filled[jj, ii]):
                zs.append(filled[jj, ii])
    return float(np.mean(zs)) if zs else None

G = np.load('data/wo/chm_grid_sw_1m.npz')
kd = [f for f in G.files if f.endswith('dtm')][0]
L = G[kd].copy()
for _ in range(40):
    n = np.isnan(L)
    if not n.any():
        break
    P = np.pad(L, 1, constant_values=np.nan)
    nb = np.stack([P[0:-2, 1:-1], P[2:, 1:-1], P[1:-1, 0:-2], P[1:-1, 2:],
                   P[0:-2, 0:-2], P[2:, 2:], P[0:-2, 2:], P[2:, 0:-2]])
    with np.errstate(all='ignore'):
        m = np.nanmean(nb, axis=0)
    L[n] = m[n]

def dtm_xy(x, y):
    if y >= 319.5:
        return hcell(int(round(x - X0)), int(round(y - Y0)))
    i = int(round(x)) - GX0; j = int(round(y)) - GY0
    zs = [L[jj, ii] for jj in (j - 1, j) for ii in (i - 1, i)
          if 0 <= jj < L.shape[0] and 0 <= ii < L.shape[1] and np.isfinite(L[jj, ii])]
    return float(np.mean(zs)) if zs else None

dg = bpy.context.evaluated_depsgraph_get()

def make_bvh(o):
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    b = BVHTree.FromPolygons([o.matrix_world @ v.co for v in m.vertices],
                             [tuple(p.vertices) for p in m.polygons])
    e.to_mesh_clear()
    return b

def hz(b, x, y):
    if b is None:
        return None
    h = b.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))
    return None if h[0] is None else h[0].z

P = O[PN]; BWF = make_bvh(P)
BOLD = {n: make_bvh(O[n]) for n in (WUN, WTN) if O.get(n)}

def lift(obj, tag, x1, x2):
    me = obj.data; mw = obj.matrix_world; mi = mw.inverted()
    n = 0; dzs = []
    for v in me.vertices:
        c = mw @ v.co
        if c.y < 311.5 or not (x1 <= c.x <= x2):
            continue
        z = None
        if abs(c.y - 320.0) <= 0.7:
            z = hz(BWF, c.x, 320.35)
        if z is None:
            z = dtm_xy(c.x, c.y)
        if z is None:
            continue
        dz = z - c.z
        if abs(dz) < 0.002:
            continue
        c.z = z
        v.co = mi @ c
        n += 1; dzs.append(dz)
    me.update()
    rec = dict(moved=n,
               dz=[round(float(min(dzs)), 4), round(float(np.median(dzs)), 4),
                   round(float(max(dzs)), 4)] if dzs else None)
    print('LIFT', tag, rec, flush=True)
    return rec

rep['fix2_wu'] = lift(O[WUN], 'WU', xmin, xmax)
rep['fix2_wt'] = lift(O[WTN], 'WT', 67.0, 80.6)

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BNEW = {n: make_bvh(O[n]) for n in (WUN, WTN) if O.get(n)}

def top(B, x, y):
    best = None
    for k, b in B.items():
        z = hz(b, x, y)
        if z is not None and (best is None or z > best):
            best = z
    return best

grass = {}
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED',
             'QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o = O.get(name)
    if not o:
        continue
    me = o.data; mw = o.matrix_world; mi = mw.inverted()
    k = 0; mx = 0.0
    for v in me.vertices:
        c = mw @ v.co
        if not (xmin - 2 <= c.x <= xmax + 2 and 308 <= c.y <= 322):
            continue
        a0 = top(BOLD, c.x, c.y); a1 = top(BNEW, c.x, c.y)
        if a0 is None or a1 is None:
            continue
        d = a1 - a0
        if abs(d) < 0.002:
            continue
        c.z += d; v.co = mi @ c; k += 1; mx = max(mx, abs(d))
    me.update()
    grass[name[:2]] = [k, round(mx, 3)]
    print('GRASS2', name[:2], k, round(mx, 3), flush=True)
rep['fix2_grass'] = grass

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BWF = make_bvh(P); BWU = make_bvh(O[WUN]); BWT = make_bvh(O[WTN])
seam = []
gaps = []
for x in range(69, 110, 2):
    rec = dict(x=x,
               wf=None if hz(BWF, x, 320.3) is None else round(hz(BWF, x, 320.3), 3),
               wu=None if hz(BWU, x, 319.7) is None else round(hz(BWU, x, 319.7), 3),
               wt=None if hz(BWT, x, 319.7) is None else round(hz(BWT, x, 319.7), 3),
               dtm=None if dtm_xy(x, 320.0) is None else round(dtm_xy(x, 320.0), 3))
    if rec['wf'] is not None and rec['wu'] is not None:
        rec['wf_wu'] = round(rec['wf'] - rec['wu'], 3); gaps.append(abs(rec['wf_wu']))
    if rec['wf'] is not None and rec['wt'] is not None:
        rec['wf_wt'] = round(rec['wf'] - rec['wt'], 3); gaps.append(abs(rec['wf_wt']))
    seam.append(rec)
    print('SEAM2', rec, flush=True)
rep['fix2_seam'] = seam
rep['fix2_seam_abs_max'] = round(max(gaps), 3) if gaps else None
print('SEAM abs max', rep['fix2_seam_abs_max'], flush=True)
json.dump(rep, open('data/wy/fix_report.json', 'w'), indent=1)
if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED', flush=True)
else:
    print('NO SAVE', flush=True)
