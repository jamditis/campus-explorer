import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in o.modifiers: print(m.name, m.show_render, m.node_group.name if m.type=='NODES' and m.node_group else '')
for m in o.modifiers: m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); TB=BVHTree.FromBMesh(bm)
def z(x,y):
    h=TB.ray_cast(Vector((x,y,175)),Vector((0,0,-1))); return h[0].z if h[0] else float('nan')
xs=list(range(-246,-180,6))
for y in range(-164,-118,3):
    print('%4d '%y+' '.join('%6.1f'%z(x,y) for x in xs))
