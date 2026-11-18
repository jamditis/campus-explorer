cams191="camz('WS191_CAM_oblique_NormalAveW_W_edge_from_SE_high',(-326.0,-272.0,0),(-349.0,-247.0),24,22.0,0.0)\\\\ncamz('WS191_CAM_eye_NormalAveW_looking_W_to_edge',(-333.0,-253.6,0),(-362.0,-251.5),26,1.7,0.5)\\\\ncamz('WS191_CAM_eye_Lot3_S_ramp_from_E_looking_W',(-300.0,-241.0,0),(-326.0,-232.0),26,1.7,0.5)\\\\ncamz('WS191_CAM_closeup_Lot3_S_gap_fill_from_SE',(-291.5,-243.5,0),(-297.5,-236.5),30,2.0,0.0)\\\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws189/render189.py').read()
src=src.replace('cams189="','cams189="'+cams191,1)
exec(compile(src,'render189','exec'))
