import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS102_CAM_oblique_CollegeAve_S_from_SE',(-182,-250,0),(-228,-195),30,42.0,0.0)
camz('WS102_CAM_eye_CollegeAve_S_from_S',(-242.6,-234,0),(-221,-170),28,1.6,1.0)
camz('WS102_CAM_eye_CollegeAve_S_from_N',(-214.5,-150,0),(-236,-212),28,1.6,0.5)
camz('WS102_CAM_closeup_plaza_bands_curb_start',(-230.8,-185.5,0),(-221,-171),30,1.6,0.0)
camz('WS103_CAM_closeup_W_sidewalk_from_S',(-238.46,-207.49,0),(-229.84,-182.96),30,1.6,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render103','exec'))
