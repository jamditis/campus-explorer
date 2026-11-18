src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
add="""camz('WS67_CAM_oblique_CollegeAve_W_to_RHD',(-175,-150,175),(-250,-55),30,None,0.0)
camz('WS67_CAM_eye_CollegeAve_W_from_Kasser_steps',(-212,-70,0),(-268,-50),28,1.7,2.0)
camz('WS67_CAM_eye_CollegeAve_E_from_RHD_entrance',(-266,-56,0),(-214,-66),28,1.7,1.5)
camz('WS67_CAM_closeup_CollegeAve_gap_bridge',(-262,-61,0),(-246,-56),30,2.2,0.3)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render59+67','exec'))
