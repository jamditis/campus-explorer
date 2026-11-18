import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m'];dg=bpy.context.evaluated_depsgraph_get()
m=T.evaluated_get(dg).to_mesh();bm=bmesh.new();bm.from_mesh(m);bm.transform(T.matrix_world);BV=BVHTree.FromBMesh(bm)
cu=bpy.data.objects['WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade'];W=cu.matrix_world;Wi=W.inverted()
tops={}
for v in cu.data.vertices:
    p=W@v.co;h=BV.ray_cast(Vector((p.x+0.4,p.y,400)),Vector((0,0,-1)),1000)[0]
    if h: tops[round(p.y,1)]=p.z
ch=0
for v in cu.data.vertices:
    p=W@v.co;k=round(p.y,1)
    h=BV.ray_cast(Vector((p.x+0.4,p.y,400)),Vector((0,0,-1)),1000)[0]
    if not h and k in tops and p.z>tops[k]-1.5:
        v.co=Wi@Vector((p.x,p.y,tops[k]-2.0));ch+=1
cu.data.update();print('A86 curtain bottom verts lowered',ch,'of',len(cu.data.vertices)-len(tops))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A86 saved curtain b')
