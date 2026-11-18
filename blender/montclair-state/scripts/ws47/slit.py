import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=['Terrain_LiDAR_DTM_1m']
sc=bpy.context.scene; o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
import collections; miss=[]
x=60.0
while x<160:
    y=-90.0
    while y<-40:
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if h is None or h.z<50: miss.append((round(x,1),round(y,1)))
        y+=0.1
    x+=0.1
print('S47 fine misses',len(miss))
c=collections.Counter((int(a//5)*5,int(b//5)*5) for a,b in miss); print('S47 cells',c.most_common(15))
