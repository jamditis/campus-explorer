cams188="camz('WS188_CAM_oblique_Sprague_endzone_from_SE_high',(-318.0,-234.0,0),(-340.0,-212.0),24,22.0,0.0)\ncamz('WS188_CAM_eye_Sprague_endzone_from_Lot36_looking_N',(-338.0,-227.0,0),(-338.0,-205.0),26,1.7,1.0)\ncamz('WS188_CAM_eye_Sprague_goal_line_from_E_looking_W',(-320.5,-211.0,0),(-352.0,-217.0),26,1.7,0.5)\ncamz('WS188_CAM_closeup_Sprague_endzone_letters_hashes',(-331.0,-223.0,0),(-339.0,-215.5),30,3.0,0.0)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws177/render177.py').read()
src=src.replace('cams177="','cams177="'+cams188.replace('\n','\\n'),1)
exec(compile(src,'render177','exec'))
