import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh
o=bpy.data.objects.get('T_RedMaple_L1_0511'); print('TREE',o.type,[round(x,3) for x in o.location],o.parent,[c.name for c in o.users_collection], o.instance_type)
cap=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps']
bm=bmesh.new(); bm.from_mesh(cap.data); t=BVHTree.FromBMesh(bm)
for ob in bpy.data.objects:
    if ob.type not in('MESH','EMPTY'): continue
    p=ob.matrix_world.translation
    h=t.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
    if h[0] is not None: print('INCAP',ob.name,ob.type,round(p.z-h[0].z,3),[c.name for c in ob.users_collection])
for ob in bpy.data.collections['OH_SCH_Win_red_frame_20261031oh'].all_objects: print('WINC',ob.name,ob.type,len(ob.data.vertices) if ob.type=='MESH' else '',[m.name for m in ob.data.materials] if ob.type=='MESH' else '')
