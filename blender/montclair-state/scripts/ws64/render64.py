src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
add="""camz('WS64_CAM_oblique_Kasser_north',(-170,70,195),(-224,16),30,None,0.0)
camz('WS64_CAM_eye_Kasser_north_from_E',(-198,28,0),(-232,8),28,1.7,1.0)
camz('WS64_CAM_eye_Kasser_north_from_NW',(-240,44,0),(-216,6),28,1.7,1.0)
camz('WS64_CAM_closeup_Kasser_north_pad',(-222,16,0),(-233,3),30,3.0,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render59+64','exec'))
