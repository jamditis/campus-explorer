cams177="camz('WS177_CAM_oblique_NormalAve_N_side_from_S_high',(-178.36,-315.07,0),(-171.70,-286.84),24,22.0,0.0)\ncamz('WS177_CAM_eye_NormalAve_N_walk_from_W_looking_E',(-204.63,-278.35,0),(-132.73,-295.84),26,1.7,1.0)\ncamz('WS177_CAM_eye_NormalAve_N_curb_from_road_E_looking_W',(-114.46,-305.49,0),(-191.35,-283.03),26,1.5,0.3)\ncamz('WS177_CAM_closeup_NormalAve_N_curb_verge_walk',(-172.97,-292.20,0),(-163.92,-288.68),30,1.6,0.0)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws176/render176.py').read()
src=src.replace("cams176=\"","cams176=\""+cams177.replace('\n','\\n'),1)
exec(compile(src,'render176','exec'))
