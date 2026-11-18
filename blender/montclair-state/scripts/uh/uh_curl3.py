"""uh pass3: thin QXP/QY south curtain over the UG lawn strip (was showing as curled white edge)."""
import bpy, os
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'

def thin_south_curtain(name, y_lo=248.2, y_hi=250.2, x0=-68.0, x1=-36.0, keep=0.04):
    o = bpy.data.objects[name]; me = o.data; mw = o.matrix_world; imw = mw.inverted()
    eu = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = set()
    for ek, c in eu.items():
        if c == 1: bvi.update(ek)
    # column tops in band
    cols = {}
    band = []
    for v in me.vertices:
        p = mw @ v.co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            band.append(v.index)
            k = (round(p.x / 0.03), round(p.y / 0.03))
            cols[k] = max(cols.get(k, -1e9), p.z)
    n = 0
    for vi in band:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x / 0.03), round(p.y / 0.03))
        top = cols[k]
        if abs(p.z - top) < 1e-4:
            continue  # leave tops
        # bottoms / mid: pull up toward top-keep, stronger on boundary and at south
        thickness = top - p.z
        if thickness < keep + 0.01: continue
        # weight by how south / how boundary
        w = 1.0
        if vi not in bvi:
            w = 0.7
        target = top - keep
        p.z = p.z * (1 - w) + target * w
        v.co = imw @ p; n += 1
    # also nudge tops at south boundary slightly down toward a soft lip (0.5 cm)
    for vi in band:
        if vi not in bvi: continue
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x / 0.03), round(p.y / 0.03))
        if abs(p.z - cols[k]) > 1e-4: continue
        if p.y < 249.4:
            p.z -= 0.005; v.co = imw @ p; n += 1
    me.update(); print('UH_CURL3', name, 'moved', n)
    return n

n1 = thin_south_curtain('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
n2 = thin_south_curtain('QY_plaza_rim_band_313024781_UNVERIFIED', keep=0.03)
print('UH_CURL3 total', n1 + n2)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
