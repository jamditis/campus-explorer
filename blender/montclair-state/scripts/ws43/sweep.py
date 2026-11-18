import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type=='MESH' and any(k in o.name for k in ('Cole Hall','CCOM','Communication','Morehead','Kasser')) and not o.hide_render:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('BB',o.name[:50],round(min(p.x for p in bb)),round(max(p.x for p in bb)),round(min(p.y for p in bb)),round(max(p.y for p in bb)))
def tree(n):
    ob=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); return BVHTree.FromBMesh(bm)
T=tree('Terrain_LiDAR_DTM_1m')
P={n:tree(n) for n in ['Footpaths_OSM','Roads_OSM','WS27_CollegeAve_carriageway_2020ortho','COLE_plaza_deck_bs'] if n in bpy.data.objects}
hits=[]
for x in np.arange(-200,140,1.0):
    for y in np.arange(-130,130,1.0):
        t=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
        if not t[0]: continue
        for n,b in P.items():
            r=b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),600)
            # pavement top hit; check terrain above pavement: cast from pavement up
            if r[0]:
                up=T.ray_cast(r[0]+Vector((0,0,-0.005)),Vector((0,0,1)),0.5)
                if up[0] and t[0].z>r[0].z+0.01: hits.append((round(x),round(y),n[:10],round(t[0].z-r[0].z,2)))
print('SW n',len(hits))
# cluster by 5m cells
from collections import defaultdict
c=defaultdict(list)
for h in hits: c[(h[0]//5*5,h[1]//5*5,h[2])].append(h[3])
for k,v in sorted(c.items(),key=lambda kv:-len(kv[1]))[:40]: print('SW',k,len(v),max(v))
