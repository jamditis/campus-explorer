cams190="camz('WS190_CAM_oblique_Lot3_S_ramp_from_SW_high',(-328.0,-262.0,0),(-309.0,-240.0),24,20.0,0.0)\\\\ncamz('WS190_CAM_eye_Lot3_S_ramp_from_E_looking_W',(-300.0,-241.0,0),(-326.0,-232.0),26,1.7,0.5)\\\\ncamz('WS190_CAM_oblique_Lot3_S_ramp_from_SE_high',(-292.0,-258.0,0),(-309.0,-241.0),24,22.0,0.0)\\\\ncamz('WS190_CAM_eye_Lot3_S_ramp_from_S_looking_N',(-309.6,-252.5,0),(-308.0,-234.0),26,1.7,0.5)\\\\ncamz('WS190_CAM_closeup_Lot3_S_ramp_E_edge',(-301.5,-243.5,0),(-305.5,-239.0),30,2.0,0.0)\\\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws189/render189.py').read()
src=src.replace('cams189="','cams189="'+cams190,1)
exec(compile(src,'render189','exec'))
