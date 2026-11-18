cams174="camz('WS174_CAM_oblique_NormalAve_W_S_curb_from_N_high',(-312.0,-236.0,0),(-322.0,-266.0),24,30.0,0.0)\ncamz('WS174_CAM_eye_NormalAve_W_S_walk_from_E_taper',(-274.5,-273.9,0),(-324.4,-259.0),26,1.7,1.0)\ncamz('WS174_CAM_eye_NormalAve_W_S_curb_from_road_W',(-344.4,-252.2,0),(-290.7,-268.5),26,1.5,0.3)\ncamz('WS174_CAM_closeup_D2_mouth_new_curb_line',(-318.8,-257.3,0),(-324.9,-261.3),30,1.6,0.1)\ncamz('WS174_CAM_closeup_taper_E_end',(-267.3,-269.4,0),(-279.1,-271.8),28,1.6,0.1)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws173/render173.py').read()
src=src.replace("cams173=\"","cams173=\""+cams174.replace('\n','\\n'),1)
exec(compile(src,'render173','exec'))
