import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]+[o.name for o in bpy.data.objects if o.name.startswith(('WS113_terrain_fan_fill','WS110_ground_patch'))])",1)
add="""camz('WS117_CAM_oblique_Chapin_W_entrance',(-236,-214,0),(-212,-194),28,22.0,0.0)
camz('WS117_CAM_eye_entrance_stair_from_plaza',(-225.5,-198.9,0),(-209,-198.8),30,1.7,1.0)
camz('WS117_CAM_eye_terrace_from_N_connector',(-217.0,-183.0,0),(-212,-199),28,1.7,0.8)
camz('WS117_CAM_closeup_stair_rail_cheek',(-219.5,-195.0,0),(-214.5,-199.5),32,2.2,0.5)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render117','exec'))
