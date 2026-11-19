# ws223h (W45): the trench in the WS70 verge grass along the Kasser landing S edge comes from the WS72_KasserSW_walk_cut GN,
# whose target WS72_cut_helper_hidden is the OLD landing footprint (S edge ~0.25 m further S than the current slab, top
# ~125.72): grass in that band is pulled to 125.66, 13 cm under the slab edge. Only for WS70 (the helper is also used by
# Terrain_LiDAR_DTM_1m, WS60 and WS68, left as-is), the modifier now uses a copy of the node group aimed at a hidden copy of
# the CURRENT landing mesh, so the grass is cut (top - 6 cm) only under the real slab. Grass only; no paving touched.
import bpy
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']
H0=bpy.data.objects['WS72_cut_helper_hidden']
me=L.data.copy(); me.name='WS223_WS70_cut_helper_landing_ws223f'
H=bpy.data.objects.new('WS223_WS70_cut_helper_hidden',me); H.matrix_world=L.matrix_world.copy()
for c in H0.users_collection: c.objects.link(H)
H.hide_render=True; H.hide_viewport=H0.hide_viewport; H.display_type=H0.display_type; H.hide_set(H0.hide_get())
g0=bpy.data.node_groups['WS72_KasserSW_walk_cut']; g=g0.copy(); g.name='WS223_WS70_walk_cut_current_landing'
n=[n for n in g.nodes if n.bl_idname=='GeometryNodeObjectInfo'][0]; n.inputs[0].default_value=H
o=bpy.data.objects['WS70_gap_strip_grass_berms']; m=o.modifiers['WS72_KasserSW_walk_cut']; m.node_group=g
print('F223H helper',H.name,'verts',len(me.vertices),'collections',[c.name for c in H.users_collection],'WS70 mod ->',m.node_group.name,flush=True)
