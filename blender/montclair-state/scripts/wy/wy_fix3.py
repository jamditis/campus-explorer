"""wy fix3: snap WU/WT verts in the last 8 m south of y=320 (Reid-hole x-range)
to the WF edge height. Avoids the chm_grid NaN-fill at the y=320 tile edge that
left a ~14 cm dip at x85-87 after fix2."""
import bpy, json, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
SAVE = os.environ.get('SAVE') == '1'
PN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
WUN = 'WU_richardson_reid_LiDAR_patch_UNVERIFIED'
WTN = 'WT_richardson_west_LiDAR_patch_UNVERIFIED'
O = bpy.data.objects
rep = json.load(open('data/wy/fix_report.json'))

def ss(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)

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
BOLD = {n: make_bvh(O[n]) for n in (WUN, WTN)}

def snap(obj, tag, x1, x2):
    me = obj.data; mw = obj.matrix_world; mi = mw.inverted()
    n = 0; dzs = []
    for v in me.vertices:
        c = mw @ v.co
        if c.y < 312.0 or c.y > 320.6 or not (x1 <= c.x <= x2):
            continue
        zn = hz(BWF, c.x, 320.35)
        if zn is None:
            continue
        w = ss((c.y - 312.0) / 8.0)
        nz = c.z * (1 - w) + zn * w
        # near the shared edge, go all the way to WF
        if abs(c.y - 320.0) <= 1.05:
            nz = zn
        dz = nz - c.z
        if abs(dz) < 0.002:
            continue
        c.z = nz
        v.co = mi @ c
        n += 1; dzs.append(dz)
    me.update()
    rec = dict(moved=n,
               dz=[round(float(min(dzs)), 4), round(float(np.median(dzs)), 4),
                   round(float(max(dzs)), 4)] if dzs else None)
    print('SNAP', tag, rec, flush=True)
    return rec

rep['fix3_wu'] = snap(O[WUN], 'WU', 67.0, 111.0)
rep['fix3_wt'] = snap(O[WTN], 'WT', 67.0, 80.6)

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BNEW = {n: make_bvh(O[n]) for n in (WUN, WTN)}

def top(B, x, y):
    best = None
    for b in B.values():
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
        if not (65 <= c.x <= 113 and 308 <= c.y <= 322):
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
    print('GRASS3', name[:2], k, round(mx, 3), flush=True)
rep['fix3_grass'] = grass

bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BWF = make_bvh(P); BWU = make_bvh(O[WUN]); BWT = make_bvh(O[WTN])
seam = []; gaps = []
for x in range(69, 110, 2):
    rec = dict(x=x,
               wf=None if hz(BWF, x, 320.3) is None else round(hz(BWF, x, 320.3), 3),
               wu=None if hz(BWU, x, 319.7) is None else round(hz(BWU, x, 319.7), 3),
               wt=None if hz(BWT, x, 319.7) is None else round(hz(BWT, x, 319.7), 3))
    if rec['wf'] is not None and rec['wu'] is not None:
        rec['wf_wu'] = round(rec['wf'] - rec['wu'], 3); gaps.append(abs(rec['wf_wu']))
    if rec['wf'] is not None and rec['wt'] is not None:
        rec['wf_wt'] = round(rec['wf'] - rec['wt'], 3); gaps.append(abs(rec['wf_wt']))
    seam.append(rec)
    print('SEAM3', rec, flush=True)
rep['fix3_seam'] = seam
rep['fix3_seam_abs_max'] = round(max(gaps), 3) if gaps else None
print('SEAM3 abs max', rep['fix3_seam_abs_max'], flush=True)
json.dump(rep, open('data/wy/fix_report.json', 'w'), indent=1)
if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED', flush=True)
