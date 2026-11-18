import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS107_CAM_eye_Chapin_from_CollegeAve_S',(-226.5,-236,0),(-200,-185),24,1.7,6.0)
camz('WS108_CAM_eye_Chapin_from_CollegeAve_S_far',(-229,-262,0),(-200,-205),24,1.7,8.0)
camz('WS107_CAM_oblique_Chapin_W_bank_from_E',(-150,-200,0),(-200,-190),30,40.0,6.0)
camz('WS108_CAM_eye_W_bank_from_walk_N_v2_clear_of_PinOak0163',(-221.5,-162.5,0),(-235.79,-185.11),28,1.6,0.3)
camz('WS108_CAM_closeup_Chapin_eave_windows_from_road',(-232,-215,0),(-205,-192),40,9.0,10.0)
camz('WS108_CAM_closeup_Chapin_S_wing_eave_from_S',(-203,-247,0),(-197,-229),35,4.0,13.5)
camz('WS108_CAM_eye_Chapin_N_end_from_bend',(-205,-135,0),(-190,-185),28,1.7,7.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render108','exec'))
