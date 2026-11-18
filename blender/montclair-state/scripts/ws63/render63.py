src=open('/workspace/nj-scenes/montclair-state/scripts/ws59/render59.py').read()
add="""camz('WS63_CAM_oblique_E_band',(55,5,165),(118,-70),30,None,0.0)
camz('WS63_CAM_eye_E_band_from_W',(84,-58,0),(128,-72),28,1.7,1.0)
camz('WS63_CAM_eye_E_band_from_SE',(152,-92,0),(105,-64),28,1.7,1.0)
camz('WS63_CAM_closeup_E_band_DTM_step',(92,-63,0),(102,-74),30,3.0,0.0)
"""
src=src.replace("base=bpy.data.objects.get('Sun')",add+"base=bpy.data.objects.get('Sun')",1)
exec(compile(src,'render59+63','exec'))
