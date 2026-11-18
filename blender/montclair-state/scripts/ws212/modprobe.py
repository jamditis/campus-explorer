import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
N=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ort']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n in N or n.startswith('WS68_RHD_ground_northDTM')]
for o in b.objects:
    print('OBJ',o.name,len(o.data.vertices))
    for m in o.modifiers: print('  MOD',m.type,m.name,m.show_render, getattr(m,'node_group',None) and m.node_group.name)
