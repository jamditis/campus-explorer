cams160="camz('WS160_CAM_oblique_Panzer_gym_roof_from_SE',(-222,-246,0),(-268,-192),24,46.0,0.0)\ncamz('WS160_CAM_eye_Panzer_N_walk_spur_from_College_Ave',(-226.5,-160,0),(-236,-170.5),28,1.7,0.5)\n"
cams161="camz('WS161_CAM_oblique_Panzer_gym_SW_from_Lot3',(-353.4,-255.9,0),(-276.1,-202.1),26,38.0,0.0)\ncamz('WS161_CAM_eye_Panzer_W_facade_from_Lot3_aisle',(-306.7,-197.0,0),(-285.7,-177.3),26,1.7,5.0)\ncamz('WS161_CAM_eye_Panzer_S_block_from_SW',(-314.0,-249.7,0),(-284.7,-225.8),26,1.7,3.0)\ncamz('WS161_CAM_closeup_Panzer_W_door_clerestory',(-295.1,-178.1,0),(-285.3,-174.3),28,1.7,3.5)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws158/render158.py').read()
src=src.replace('add="""','add="""'+cams160+cams161,1)
exec(compile(src,'render158','exec'))
