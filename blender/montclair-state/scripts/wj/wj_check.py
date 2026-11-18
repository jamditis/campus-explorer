import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
B={k:bvh(n) for k,n in (('wf','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'),('ext','WJ_south_gully_LiDAR_patch_ext_UNVERIFIED'),('sk','Context_skirt_3DEP_ortho_4km'))}
for t in ('004','006','007','008','011','023','015','003'):
    o=bpy.data.objects['TL_tree_%s_UNVERIFIED'%t]; p=o.matrix_world.translation
    r={k:(round(b.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))[0].z,2) if b.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))[0] else None) for k,b in B.items()}
    print('T',t,round(p.x,1),round(p.y,1),'z',round(p.z,2),r,'dz',o.get('wj_dz'),'prev',{k:o[k] for k in o.keys() if k.endswith('_dz')})
