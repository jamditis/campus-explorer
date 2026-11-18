import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]+[o.name for o in bpy.data.objects if o.name.startswith(('WS113_terrain_fan_fill','WS110_ground_patch'))])",1)
add="""camz('WS113_CAM_oblique_fan_fill_from_SW',(-268,-268,0),(-212,-214),28,48.0,0.0)
camz('WS113_CAM_eye_lawn_E_of_brick_link',(-238.2,-241.0,0),(-212,-233),28,1.7,1.0)
camz('WS113_CAM_eye_Chapin_S_lawn_from_E',(-196,-236,0),(-240,-244),30,1.7,1.0)
camz('WS113_CAM_closeup_brick_link_lawn_edge',(-231.5,-246.5,0),(-237.5,-239.5),32,3.2,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render113','exec'))
