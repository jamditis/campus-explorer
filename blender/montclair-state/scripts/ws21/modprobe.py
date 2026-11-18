import bpy
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in o.modifiers:
    ng=m.node_group
    print('MOD',m.name,m.show_render,ng.name if ng else None,[n.type for n in ng.nodes] if ng else None)
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg).to_mesh()
import bmesh; bm=bmesh.new(); bm.from_mesh(e)
M=o.matrix_world
b=[e2 for e2 in bm.edges if e2.is_boundary and all(-5<(M@v.co).x<60 and 95<(M@v.co).y<130 for v in e2.verts)]
print('EVAL faces',len(e.polygons),'boundary edges in court box',len(b))
