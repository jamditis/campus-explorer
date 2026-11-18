import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km',[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0])",1)
add="""camz('WS90_CAM_eye_left_curb_bend_from_S',(-197.6,-104,0),(-203,-72),28,1.6,0.4)
camz('WS101_CAM_oblique_Sleg_from_SE',(-178,-196,152),(-216,-138),30,None,0.0)
camz('WS101_CAM_eye_Sleg_from_S',(-217.5,-178,0),(-207,-112),28,1.6,0.6)
camz('WS101_CAM_eye_Sleg_from_N',(-203.5,-110,0),(-219,-168),28,1.6,0.3)
camz('WS101_CAM_closeup_Sleg_W_curb_lane',(-226,-141,0),(-214,-129),30,1.6,0.0)
camz('WS101_CAM_closeup_Sleg_E_posts_bed',(-199,-153,0),(-205.5,-136),30,1.6,0.3)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render101','exec'))
