"""uh pass2: stronger curl flatten on QXP/QY south edge near seam (y~245-250)."""
import bpy, os
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
dg = bpy.context.evaluated_depsgraph_get()

def caster(n):
    o = bpy.data.objects.get(n)
    if not o: return lambda x,y: None
    e = o.evaluated_get(dg); mw = o.matrix_world; iw = mw.inverted()
    d = (iw.to_3x3() @ Vector((0,0,-1))).normalized()
    def f(x,y):
        r = e.ray_cast(iw @ Vector((x,y,400)), d)
        return (mw @ r[1]).z if r[0] else None
    return f
UG = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA = caster('SA_ground_lower_patch_UNVERIFIED')
DT = caster('Terrain_LiDAR_DTM_1m')
def gnd(x,y):
    for c in (UG, SA, DT):
        z = c(x,y)
        if z is not None: return z
    return None

def fix(name, off=0.04):
    o = bpy.data.objects[name]; me = o.data; mw = o.matrix_world; imw = mw.inverted()
    # find boundary verts
    eu = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = set()
    for ek, c in eu.items():
        if c == 1: bvi.update(ek)
    # column tops in region
    cols = {}
    region = []
    for v in me.vertices:
        p = mw @ v.co
        if -68 < p.x < -40 and 244.0 < p.y < 251.0:
            region.append(v.index)
            k = (round(p.x/0.03), round(p.y/0.03))
            cols[k] = max(cols.get(k, -1e9), p.z)
    n = 0
    for vi in region:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x/0.03), round(p.y/0.03))
        top = cols[k]; is_top = abs(p.z - top) < 1e-4
        gz = gnd(p.x, p.y)
        if gz is None: continue
        # neighbour tops
        neigh = [cols[(k[0]+dx,k[1]+dy)] for dx in (-2,-1,0,1,2) for dy in (-2,-1,0,1,2)
                 if (dx or dy) and (k[0]+dx,k[1]+dy) in cols]
        if not neigh: continue
        med = sorted(neigh)[len(neigh)//2]
        if is_top:
            # flatten if: boundary, or above med+2cm, or above ground+5cm, or y<249 curl zone
            is_b = vi in bvi
            over = p.z > med + 0.02 or p.z > gz + 0.05 or (is_b and abs(p.z - (gz+off)) > 0.015)
            if over or (p.y < 249.0 and abs(p.z - (gz+off)) > 0.02):
                target = min(gz + off, med + 0.005) if neigh else gz + off
                # prefer smooth to ground+off in curl zone
                if p.y < 248.5 or is_b:
                    target = gz + off
                if abs(target - p.z) > 0.001:
                    p.z = target; v.co = imw @ p; n += 1
    # re-enforce bottoms
    cols2 = {}
    for vi in region:
        p = mw @ me.vertices[vi].co
        k = (round(p.x/0.03), round(p.y/0.03))
        cols2[k] = max(cols2.get(k, -1e9), p.z)
    for vi in region:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x/0.03), round(p.y/0.03))
        top = cols2[k]
        if abs(p.z - top) < 1e-4: continue
        want = top - 0.28
        if p.z < top - 0.05 and abs(p.z - want) > 0.04:
            p.z = want; v.co = imw @ p; n += 1
    me.update(); print('UH_CURL2', name, n, 'bvi_in_region', sum(1 for vi in region if vi in bvi))
    return n

n1 = fix('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
n2 = fix('QY_plaza_rim_band_313024781_UNVERIFIED', off=0.035)
print('UH_CURL2 total', n1+n2)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
