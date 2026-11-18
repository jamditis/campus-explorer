import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km',[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0])",1)
add="""camz('WS67_CAM_oblique_CollegeAve_W_to_RHD',(-175,-150,175),(-250,-55),30,None,0.0)
camz('WS67_CAM_eye_CollegeAve_E_from_RHD_entrance',(-266,-56,0),(-214,-66),28,1.7,1.5)
camz('WS68_CAM_closeup_crosswalk_RHD_SE',(-259.5,-71,0),(-255.5,-50),30,1.7,0.0)
camz('WS69_CAM_closeup_gap_strip_curbs',(-242,-63,0),(-251,-55),30,1.7,0.0)
camz('WS68_CAM_eye_RHD_cogen_lawn_from_S',(-285,-128,0),(-290,-40),26,1.7,4.0)
"""
assert "TT=[bvh(n) for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km',[o" in src
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render59+68+69','exec'))
