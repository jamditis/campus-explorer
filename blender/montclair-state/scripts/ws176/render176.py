cams176="camz('WS176_CAM_oblique_WS110_S_curb_from_N_high',(-255.6,-250.6,0),(-232.7,-283.8),24,25.0,0.0)\ncamz('WS176_CAM_eye_WS110_S_walk_from_E_toward_junction',(-213.2,-288.4,0),(-281.1,-271.3),26,1.7,1.0)\ncamz('WS176_CAM_eye_NormalAve_S_curb_from_road_W_looking_E',(-289.9,-265.1,0),(-212.9,-287.4),26,1.5,0.3)\ncamz('WS176_CAM_closeup_junction_S_curb_straightened',(-274.5,-269.8,0),(-267.6,-275.0),30,1.6,0.1)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws174/render174.py').read()
src=src.replace("cams174=\"","cams174=\""+cams176.replace('\n','\\n'),1)
exec(compile(src,'render174','exec'))
