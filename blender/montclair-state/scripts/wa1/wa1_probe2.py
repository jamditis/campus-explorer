import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
W=bvh(O['WV_stone_west_LiDAR_patch_UNVERIFIED'])
def wz(x,y):
    h=W.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
for nm in ['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED']:
    ob=O[nm]; rows=[]
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co; g=wz(p.x,p.y)
        if g is not None: rows.append((round(p.y),round((p.z-g)*100,1)))
    print(nm,'n over WV',len(rows))
    import collections; d=collections.defaultdict(list)
    for y,z in rows: d[y//5*5].append(z)
    for y in sorted(d): print(' y',y,len(d[y]),'min/med/max',min(d[y]),float(np.median(d[y])),max(d[y]))
# polygons of soil edge: classify by normal z
t=O['QT_soil_edge_546643369_UNVERIFIED']
nz=[p.normal.z for p in t.data.polygons]; print('soil nz',np.percentile(nz,[0,25,50,75,100]))
