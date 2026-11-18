src=open('/workspace/nj-scenes/montclair-state/scripts/ws158/render158.py').read()
src=src.replace('add="""','add="""camz(\'WS160_CAM_oblique_Panzer_gym_roof_from_SE\',(-222,-246,0),(-268,-192),24,46.0,0.0)\ncamz(\'WS160_CAM_eye_Panzer_N_walk_spur_from_College_Ave\',(-226.5,-160,0),(-236,-170.5),28,1.7,0.5)\n',1)
exec(compile(src,'render158','exec'))
