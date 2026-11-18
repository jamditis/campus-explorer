import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1]+[o.name for o in bpy.data.objects if o.name.startswith(('WS113_terrain_fan_fill','WS110_ground_patch'))])",1)
add="""camz('WS116_CAM_oblique_Chapin_W_plaza',(-252,-222,0),(-220,-193),28,26.0,0.0)
camz('WS116_CAM_eye_plaza_from_CollegeAve_W',(-234.5,-199.5,0),(-215,-196),30,1.7,0.8)
camz('WS116_CAM_eye_plaza_from_N_connector',(-216.2,-183.5,0),(-224,-202),30,1.7,0.6)
camz('WS116_CAM_closeup_walk_end_to_plaza',(-227.5,-208.0,0),(-222.5,-199.0),32,3.0,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render113','exec'))
