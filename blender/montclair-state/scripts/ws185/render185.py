cams185="camz('WS185_CAM_oblique_Lot36_Lot3_S_ramp_from_SW_high',(-342.0,-258.0,0),(-316.0,-232.0),24,30.0,0.0)\ncamz('WS185_CAM_eye_Lot36_from_W_looking_E_bank_toe',(-336.0,-231.0,0),(-312.0,-236.0),26,1.7,1.0)\ncamz('WS185_CAM_eye_Lot3_S_ramp_from_E_looking_W',(-300.0,-241.0,0),(-326.0,-232.0),26,1.7,0.5)\ncamz('WS185_CAM_closeup_Lot3_S_ramp_Lot36_SE',(-321.5,-233.0,0),(-311.0,-237.5),30,2.2,0.0)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws177/render177.py').read()
src=src.replace('cams177="','cams177="'+cams185.replace('\n','\\n'),1)
exec(compile(src,'render177','exec'))
