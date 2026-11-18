import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('SK',len(sk.data.vertices),len(sk.data.polygons),[m.name+':'+m.type for m in sk.modifiers],[round(x,1) for x in sk.matrix_world.translation], sk.get('UNVERIFIED'), list(sk.keys())[:10])
tb=[ter.matrix_world@Vector(c) for c in ter.bound_box]; print('TERBB',[round(min(c.x for c in tb),1),round(max(c.x for c in tb),1),round(min(c.y for c in tb),1),round(max(c.y for c in tb),1)], [m.name+':'+m.type for m in ter.modifiers])
def bvh(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return b
bs=bvh(sk); bt=bvh(ter)
above=[];cnt=0
x0,x1=min(c.x for c in tb),max(c.x for c in tb); y0,y1=min(c.y for c in tb),max(c.y for c in tb)
x=x0
while x<x1:
    y=y0
    while y<y1:
        hs=bs.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); ht=bt.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if hs[0] and ht[0]:
            cnt+=1
            if hs[0].z>ht[0].z-0.02: above.append((round(hs[0].z-ht[0].z,2),round(x),round(y)))
        y+=4
    x+=4
above.sort(reverse=True)
print('OVERLAP cells',cnt,'skirt above DTM',len(above),above[:15])
import collections
print('XHIST',collections.Counter((a[1]//20*20,a[2]//20*20) for a in above).most_common(20))
