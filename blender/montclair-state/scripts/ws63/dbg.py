import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('DBG mw',[list(r) for r in T.matrix_world])
dg=bpy.context.evaluated_depsgraph_get(); print('DBG polys',len(T.evaluated_get(dg).data.polygons))
q=T.modifiers['QM_terrain_band_to_DTM']; print('DBG QM',q.node_group.name,[n.bl_idname for n in q.node_group.nodes])
for k,v in q.items(): print('DBG QMin',k,v)
