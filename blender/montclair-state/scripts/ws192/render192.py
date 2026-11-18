cams192="camz('WS192_CAM_oblique_Lot3_S_end_from_SW_high',(-324.0,-263.0,0),(-299.0,-234.0),24,24.0,0.0)\\\\\\\\ncamz('WS192_CAM_closeup_strip_E_end_from_SE',(-295.2,-240.2,0),(-299.3,-235.6),30,1.6,0.0)\\\\\\\\ncamz('WS192_CAM_oblique_Lot3_S_end_from_SE_high',(-280.0,-260.0,0),(-304.0,-234.0),24,20.0,0.0)\\\\\\\\ncamz('WS192_CAM_eye_Lot3_S_strip_from_W_looking_E',(-313.0,-239.0,0),(-292.0,-236.0),26,1.7,0.5)\\\\\\\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws191/render191.py').read()
src=src.replace('cams191="','cams191="'+cams192,1)
exec(compile(src,'render191','exec'))
