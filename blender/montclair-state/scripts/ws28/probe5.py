import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
print('mods',[(m.name,m.type) for m in o.modifiers],'verts',len(o.data.vertices),o.matrix_world.translation)
ev=o.evaluated_get(dg); me=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); TB=BVHTree.FromBMesh(bm); bm.free(); ev.to_mesh_clear()
def z(x,y):
    h=TB.ray_cast(Vector((x,y,175)),Vector((0,0,-1))); return h[0].z if h[0] else float('nan')
xs=list(range(-249,-180,3))
print('x   '+' '.join('%6d'%x for x in xs))
for y in range(-164,-56,3):
    print('%4d '%y+' '.join('%6.1f'%z(x,y) for x in xs))
