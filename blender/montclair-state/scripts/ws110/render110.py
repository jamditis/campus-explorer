import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS110_CAM_oblique_CollegeAve_S_end_NormalAve_from_SE',(-200,-310,0),(-250,-252),28,38.0,0.0)
camz('WS110_CAM_eye_CollegeAve_mouth_from_Normal_S',(-252.5,-277,0),(-240,-228),28,1.75,2.0)
camz('WS110_CAM_eye_NormalAve_from_CollegeAve_S',(-240.5,-233,0),(-258,-276),26,1.6,1.5)
camz('WS110_CAM_eye_bend_slot_check_from_S',(-196.5,-126,0),(-193,-80),30,1.6,1.0)
camz('WS110_CAM_closeup_E_curb_return',(-236,-257,0),(-246,-267.5),30,3.5,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render110','exec'))
