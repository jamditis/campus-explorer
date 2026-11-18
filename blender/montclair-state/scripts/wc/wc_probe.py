import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
GN=[n for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
print(GN)
G={n:bvh(O[n]) for n in GN}
for wn in ['QS_footway_313027436_UNVERIFIED','QS_footway_313027435_UNVERIFIED','QS_footway_313027429_UNVERIFIED']:
    o=O[wn]; V=np.array([o.matrix_world@v.co for v in o.data.vertices]); print(wn,V.min(0).round(2),V.max(0).round(2))
    W=bvh(o)
    for y in np.arange(314,326,0.5):
        row=[]
        for x in np.arange(30,90,0.1):
            h=W.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
            if h[0] is not None: row.append((x,h[0].z))
        if not row: continue
        xs=[r[0] for r in row]; zt=np.mean([r[1] for r in row])
        out=[]
        for x in (min(xs)-0.5,max(xs)+0.5):
            zz={n[:4]:round(h[0].z-zt,3) for n,b in G.items() for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None}
            out.append((round(x,2),zz))
        print(' y',y,'x',round(min(xs),2),round(max(xs),2),'top',round(zt,3),out)
for n in GN:
    o=O[n]; V=np.array([o.matrix_world@v.co for v in o.data.vertices]); print(n,V.min(0).round(1),V.max(0).round(1),len(V))
