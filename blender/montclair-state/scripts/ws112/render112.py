import bpy
src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
src=src.replace("('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km')","(['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][:1])",1)
add="""camz('WS112_CAM_oblique_branch_walks_from_SE',(-214,-282,0),(-256,-244),30,34.0,0.0)
camz('WS112_CAM_eye_W_branch_walk_from_W',(-275.5,-243.6,0),(-255,-247.2),28,2.2,1.0)
camz('WS112_CAM_eye_E_brick_link_from_N',(-234.6,-231.5,0),(-241.5,-250),28,1.7,0.8)
camz('WS112_CAM_closeup_E_brick_link_join',(-235.0,-249.5,0),(-240.3,-243.8),32,3.0,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render112','exec'))
