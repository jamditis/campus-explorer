import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
ob=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); T=BVHTree.FromBMesh(bm)
L=['T_LondonPlane_L1_0154','T_LondonPlane_L1_0176','T_PinOak_L1_0193','T_RedMaple_L1_0160','T_RedMaple_L1_0166','T_RedMaple_L1_0214','T_RedMaple_L1_0237','T_RedMaple_L1_0126','T_PinOak_L1_0174']
for n in L:
    o=bpy.data.objects[n]; x,y,_=o.matrix_world.translation; zb=min((o.matrix_world@Vector(c)).z for c in o.bound_box)
    g=min(T.ray_cast(Vector((x+dx,y+dy,zb+60)),Vector((0,0,-1)),200)[0].z for dx,dy in ((0,0),(0.4,0),(-0.4,0),(0,0.4),(0,-0.4)))
    dz=(g-0.2)-zb; o.location.z+=dz; print('ST',n,'dz',round(dz,2))
bpy.ops.wm.save_mainfile()
