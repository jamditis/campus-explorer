import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS105_CAM_oblique_W_bank_from_E',(-196.96,-181.67,0),(-232.61,-174.57),30,24.0,0.0)
camz('WS105_CAM_eye_W_bank_from_walk_N',(-220.68,-154.42,0),(-235.79,-185.11),28,1.6,0.3)
camz('WS105_CAM_eye_W_bank_from_lower_walkway_S',(-241.74,-193.62,0),(-227.24,-162.73),28,1.6,0.8)
camz('WS107_CAM_closeup_stair_B_from_walk',(-228.2,-185.0,0),(-232.4,-176.6),28,3.0,-0.8)
camz('WS107_CAM_eye_Chapin_from_CollegeAve_S',(-226.5,-236,0),(-200,-185),24,1.7,6.0)
camz('WS107_CAM_oblique_Chapin_W_bank_from_E',(-150,-200,0),(-200,-190),30,40.0,6.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render105','exec'))
