import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
N=['Terrain_LiDAR_DTM_1m','QI_east_edge_LiDAR_terrain_patch','Context_skirt_3DEP_ortho_4km']
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=N
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); T={}
for o in d.objects:
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); T[o.name]=BVHTree.FromBMesh(bm)
import collections; res=collections.Counter(); zs=[]
x=88.0
while x<102:
    y=-62.0
    while y<-48:
        ht=T['Terrain_LiDAR_DTM_1m'].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        if ht is None or ht.z<50:
            hq=T['QI_east_edge_LiDAR_terrain_patch'].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
            hs=T['Context_skirt_3DEP_ortho_4km'].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
            k='QI' if hq is not None else ('skirt' if hs is not None else 'void')
            res[k]+=1
            if hs is not None: zs.append(hs.z)
        y+=0.1
    x+=0.1
print('S50',dict(res), 'skirt z range', (min(zs),max(zs)) if zs else None)
# neighbour terrain height
h=T['Terrain_LiDAR_DTM_1m'].ray_cast(Vector((94,-50,300)),Vector((0,0,-1)))[0]; print('S50 terrain near', h.z if h else None)
