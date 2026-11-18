import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G={n[:2]:bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))}
holes=[]; rows={}
for x in np.arange(52,74,0.1):
    for y in np.arange(318.0,321.0,0.05):
        hit={k:b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] for k,b in G.items()}
        if all(v is None for v in hit.values()): holes.append((round(x,1),round(y,2)))
print('holes',len(holes))
import collections
c=collections.defaultdict(list)
for x,y in holes: c[round(x)].append(y)
for k in sorted(c): print(k, min(c[k]),max(c[k]),len(c[k]))
# WF and WT y-extent at sample x
for x in (56,60,62,64,66,70):
    for k in ('WT','WF'):
        ys=[y for y in np.arange(317,322,0.05) if G[k].ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None]
        print(x,k, (round(min(ys),2),round(max(ys),2)) if ys else None)
