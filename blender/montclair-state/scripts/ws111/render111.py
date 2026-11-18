import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS111_CAM_oblique_CollegeAve_mouth_aprons_pavilions_from_SE',(-212,-300,0),(-252,-256),30,32.0,0.0)
camz('WS111_CAM_eye_W_apron_pavilion_from_Normal_S',(-266,-273.5,0),(-256,-249),28,1.7,1.5)
camz('WS111_CAM_eye_E_walk_to_E_pavilion_from_N',(-238.8,-241.5,0),(-243.5,-263),28,1.7,1.0)
camz('WS111_CAM_closeup_W_curb_ramp_band',(-247.5,-262.5,0),(-254.2,-257.0),32,3.2,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render111','exec'))
