cams171="camz('WS171_CAM_oblique_NormalAve_W_yard_trees_from_SSE_high',(-292,-322,0),(-314,-256),24,58.0,0.0)\ncamz('WS171_CAM_closeup_Lot3_S_end_curb_strip_from_SW',(-312.5,-243.5,0),(-301.5,-234.5),28,1.6,0.3)\ncamz('WS171_CAM_oblique_NormalAve_W_utility_line_from_SW_high',(-346,-289,0),(-310,-262),24,34.0,0.0)\ncamz('WS171_CAM_eye_NormalAve_W_S_walk_poles_from_E',(-276.5,-274.0,0),(-322,-262.5),26,1.7,6.0)\ncamz('WS171_CAM_eye_NormalAve_W_from_W_end_N_walk',(-344.0,-254.0,0),(-300,-266.5),26,1.7,7.0)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws165/render165.py').read()
src=src.replace('cams165="','cams165="'+cams171.replace('\n','\\n'),1)
exec(compile(src,'render165','exec'))
