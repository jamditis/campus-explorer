cams173="camz('WS173_CAM_oblique_NormalAve_W_driveways_from_N_high',(-314.2,-237.8,0),(-327.0,-265.6),24,30.0,0.0)\ncamz('WS173_CAM_eye_driveway_D3_from_N_walk_E',(-297.7,-254.5,0),(-311.4,-269.3),26,1.7,1.0)\ncamz('WS173_CAM_eye_NormalAve_W_S_walk_driveways_from_E',(-298.9,-268.4,0),(-349.5,-256.5),26,1.7,1.0)\ncamz('WS173_CAM_closeup_driveway_D2_mouth_curb_cut',(-316.5,-258.3,0),(-325.9,-263.3),30,1.6,0.2)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws172/render172.py').read()
src=src.replace('cams171="','cams171="'+cams173.replace('\n','\\n'),1)
exec(compile(src,'render172','exec'))
