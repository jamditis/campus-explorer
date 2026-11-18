import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS105_CAM_oblique_W_bank_from_E',(-196.96,-181.67,0),(-232.61,-174.57),30,24.0,0.0)
camz('WS105_CAM_eye_W_bank_from_walk_N',(-220.68,-154.42,0),(-235.79,-185.11),28,1.6,0.3)
camz('WS105_CAM_eye_W_bank_from_lower_walkway_S',(-241.74,-193.62,0),(-227.24,-162.73),28,1.6,0.8)
camz('WS105_CAM_closeup_stair_B_from_walk',(-229.51,-182.02,0),(-232.17,-176.31),28,1.6,-0.6)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render105','exec'))
