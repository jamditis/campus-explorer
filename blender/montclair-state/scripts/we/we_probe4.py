import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
for n in ['QT_soil_edge_313027428_UNVERIFIED','QT_soil_edge_313027430_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','QT_soil_edge_313027437_UNVERIFIED','QT_soil_edge_313027432_UNVERIFIED']:
    t=O[n]; s=O[n.replace('QT_soil_edge_','QS_footway_')]
    V=[s.matrix_world@v.co for v in s.data.vertices]; B=BVHTree.FromPolygons(V,[tuple(p.vertices) for p in s.data.polygons])
    dz=[];tp=[]
    for p in t.data.polygons:
        ws=[t.matrix_world@t.data.vertices[i].co for i in p.vertices]
        d=[B.find_nearest(w)[3] for w in ws]; o=np.argsort(d)
        inn=[ws[k] for k in o[:2]]; out=[ws[k] for k in o[2:]]
        dz.append(np.mean([w.z for w in inn])-np.mean([w.z for w in out]))
        c=sum(inn,Vector())/2; h=B.ray_cast(Vector((c.x,c.y,c.z+2)),Vector((0,0,-1)))
        if h[0] is not None: tp.append(h[0].z-c.z)
    print('R',n[13:22],'inner-outer dz',np.percentile(dz,[10,50,90]).round(3),'slabtop-inner',np.percentile(tp,[10,50,90]).round(3) if tp else None,len(tp),flush=True)
