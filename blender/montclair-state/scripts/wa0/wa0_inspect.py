import bpy
O=bpy.data.objects
for n in ['WU_richardson_reid_LiDAR_patch_UNVERIFIED','QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED']:
    o=O[n]; me=o.data
    print('I',n,'v',len(me.vertices),'uv',[u.name for u in me.uv_layers],'attrs',[(a.name,a.domain,a.data_type) for a in me.attributes if not a.name.startswith('.')],'mods',[(m.type,m.name) for m in o.modifiers],'mw_id',o.matrix_world.is_identity)
m=O['WU_richardson_reid_LiDAR_patch_UNVERIFIED'].data.materials[0]
print('I MAT nodes',[ (nd.type,nd.name) for nd in m.node_tree.nodes][:30])
