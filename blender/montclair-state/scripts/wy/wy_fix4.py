"""wy fix4 (review): close the black y=320 seam crack.

WU/WT end exactly at y=320 and the new WF fill begins there, so the two
sheets met on a knife edge and a grazing eye/close-up looked through to the
void. Slide the north-edge verts 35 cm into WF and tuck them 3 cm under
(same overlap idea as the 1-cell tuck ring used on other tiles). Grass in
the band follows. No new faces.
"""
import bpy, json, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
SAVE = os.environ.get('SAVE') == '1'
WUN = 'WU_richardson_reid_LiDAR_patch_UNVERIFIED'
WTN = 'WT_richardson_west_LiDAR_patch_UNVERIFIED'
O = bpy.data.objects
rep = json.load(open('data/wy/fix_report.json'))
OVER = 0.35
TUCK = 0.03

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

BOLD = {n: make_bvh(O[n]) for n in (WUN, WTN)}

def edge_overlap(obj, tag, x1, x2):
    me = obj.data; mw = obj.matrix_world; mi = mw.inverted()
    n = 0
    for v in me.vertices:
        c = mw @ v.co
        if abs(c.y - 320.0) > 0.55 or not (x1 <= c.x <= x2):
            continue
        c.y += OVER
        c.z -= TUCK
        v.co = mi @ c
        n += 1
    me.update()
    rec = dict(moved=n, overlap=OVER, tuck=TUCK)
    print('OVERLAP', tag, rec, flush=True)
    return rec

rep['fix4_wu'] = edge_overlap(O[WUN], 'WU', 67.0, 111.0)
rep['fix4_wt'] = edge_overlap(O[WTN], 'WT', 67.0, 80.6)

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
        if not (65 <= c.x <= 113 and 318.5 <= c.y <= 321.5):
            continue
        a0 = top(BOLD, c.x, c.y); a1 = top(BNEW, c.x, c.y)
        if a0 is None or a1 is None:
            continue
        d = a1 - a0
        if abs(d) < 0.001:
            continue
        c.z += d; v.co = mi @ c; k += 1; mx = max(mx, abs(d))
    me.update()
    grass[name[:2]] = [k, round(mx, 3)]
    print('GRASS4', name[:2], k, round(mx, 3), flush=True)
rep['fix4_grass'] = grass
json.dump(rep, open('data/wy/fix_report.json', 'w'), indent=1)
if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED', flush=True)
