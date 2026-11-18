import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]+[o.name for o in bpy.data.objects if o.name.startswith(('WS113_terrain_fan_fill','WS110_ground_patch'))])",1)
add="""camz('WS114_CAM_oblique_S_end_and_S_edge_from_S',(-150,-318,0),(-175,-228),24,72.0,0.0)
camz('WS114_CAM_eye_brick_link_from_N',(-234.6,-233.2,0),(-240.5,-246.5),30,1.7,0.6)
camz('WS114_CAM_eye_brick_link_from_CollegeAve_W',(-241.2,-231.5,0),(-236.0,-242.0),30,1.7,0.3)
camz('WS114_CAM_test_S_edge_fill',(-60,-275,0),(-60,-238),28,25.0,0.0)
camz('WS114_CAM_closeup_brick_link_profile',(-231.5,-246.5,0),(-237.5,-239.5),32,3.2,0.0)
camz('WS113_CAM_eye_lawn_E_of_brick_link',(-238.2,-241.0,0),(-212,-233),28,1.7,1.0)
camz('WS113_CAM_eye_Chapin_S_lawn_from_E',(-196,-236,0),(-240,-244),30,1.7,1.0)
camz('WS113_CAM_closeup_brick_link_lawn_edge',(-231.5,-246.5,0),(-237.5,-239.5),32,3.2,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render113','exec'))
