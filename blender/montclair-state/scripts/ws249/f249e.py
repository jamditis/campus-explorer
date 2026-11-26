# ws249 pass 5 (CHAIN on ws249d): the ws249d W-slope test render showed a dark crack along the foot of the embankment:
# PK fill now sits on 2023 LiDAR but its western neighbour M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam
# (north 1 m DTM, ~0.2-0.6 m under LiDAR there) did not. Same snap (same node group + target) on M3b at index 0, so both
# meshes meet on the same LiDAR surface inside the target box (x -340..-282, y 92..216), feathered 4 m at the box edge.
import bpy
TAG='F249E'; MN='WS249_W_slope_LiDAR_terrain_snap'
o=bpy.data.objects['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
if MN not in o.modifiers:
    m=o.modifiers.new(MN,'NODES'); m.node_group=bpy.data.node_groups[MN]
    with bpy.context.temp_override(object=o): bpy.ops.object.modifier_move_to_index(modifier=MN,index=0)
print(TAG,o.name,[x.name for x in o.modifiers],flush=True)
