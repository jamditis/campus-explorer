import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G={n:bvh(O[n]) for n in O.keys() if n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','Context_skirt','QW_DTM'))}
print('ground',list(G))
def gz(x,y):
    zs=[]
    for k,b in G.items():
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None: zs.append((h[0].z,k))
    return zs
s=O['QS_footway_546643369_UNVERIFIED']; t=O['QT_soil_edge_546643369_UNVERIFIED']
print('mods',[m.type for m in s.modifiers],[m.type for m in t.modifiers])
for name,ob in(('slab',s),('soil',t)):
    out=[]
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co; zs=gz(p.x,p.y)
        if zs: 
            top=max(zs)[0]; out.append(p.z-top)
    a=np.array(out); print(name,len(ob.data.vertices),len(a),[round(float(x)*100,1) for x in np.percentile(a,[0,10,50,90,100])])
print('soil faces',len(t.data.polygons))
for p in list(t.data.polygons)[:6]:
    print([tuple(round(c,2) for c in t.matrix_world@t.data.vertices[i].co) for i in p.vertices])
for i,v in enumerate(list(t.data.vertices)[:16]):
    c=t.matrix_world@v.co; print(i,tuple(round(x,3) for x in c),[(round(z,3),k[:8]) for z,k in gz(c.x,c.y)])
