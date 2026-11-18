import bpy
for n in ['WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5','WS163_walk_back_lawn_lip_S_UNVERIFIED','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED','WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED','WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']:
    o=bpy.data.objects[n]; print('MOD',n,[(m.name,m.type,getattr(m,'node_group',None) and m.node_group.name) for m in o.modifiers],flush=True)
for o in bpy.data.objects:
    if o.type=='MESH' and any(m.type=='NODES' and m.node_group and ('scatter' in m.node_group.name.lower() or 'grass' in m.node_group.name.lower()) for m in o.modifiers):
        print('SCAT',o.name,[m.node_group.name for m in o.modifiers if m.type=='NODES'],flush=True)
