# ws273 f273b (merge208 CHAIN on ws273a): rename the #4b GN so subset renders keep it (subrend234's terrain regex needs 'terrain').
import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=T.modifiers['WS273_lot_pocket_S_lawn_material']
m.name='WS273_lot_pocket_S_terrain_lawn_material'; m.node_group.name='WS273_lot_pocket_S_terrain_lawn_material'
m.show_viewport=True; m.show_render=True
print('F273B',[x.name for x in T.modifiers][-2:],m.show_viewport,m.show_render,flush=True)
_OFF[:]=[(on,'WS273_lot_pocket_S_terrain_lawn_material' if (on=='Terrain_LiDAR_DTM_1m' and mn=='WS273_lot_pocket_S_lawn_material') else mn) for on,mn in _OFF]
