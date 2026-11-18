import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m'];dg=bpy.context.evaluated_depsgraph_get()
m=T.evaluated_get(dg).to_mesh();bm=bmesh.new();bm.from_mesh(m);bm.transform(T.matrix_world);BV=BVHTree.FromBMesh(bm)
cu=bpy.data.objects['WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade'];W=cu.matrix_world;Wi=W.inverted()
G=bpy.data.objects.get('WS68_RHD_ground_northDTM')
if G:
    gm=G.evaluated_get(dg).to_mesh();gb=bmesh.new();gb.from_mesh(gm);gb.transform(G.matrix_world);GB=BVHTree.FromBMesh(gb)
ch=0
for v in cu.data.vertices:
    p=W@v.co
    h=BV.ray_cast(Vector((p.x+0.4,p.y,400)),Vector((0,0,-1)),1000)[0]
    g=GB.ray_cast(Vector((p.x-0.4,p.y,400)),Vector((0,0,-1)),1000)[0] if G else None
    print('P86 cv y%.1f z%.2f terr %s ws68 %s'%(p.y,p.z,round(h.z,2) if h else None,round(g.z,2) if g else None))
    if h and p.z>h.z+0.03 and p.z>(g.z if g else -1e9)+0.03:
        top=max(h.z,g.z if g else h.z)+0.02
        v.co=Wi@Vector((p.x,p.y,top));ch+=1
print('A86 curtain verts clamped',ch)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('A86 saved curtain')
