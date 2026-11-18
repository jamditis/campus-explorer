cams194="camz('WS194_CAM_closeup_ramp_E_edge',(-301.5,-243.5,0),(-305.5,-239.0),30,2.0,0.0)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ncamz('WS194_CAM_eye_ramp_from_S_looking_N',(-309.6,-252.5,0),(-308.0,-234.0),26,1.7,0.5)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws193/render193.py').read()
src=src.replace('cams193="','cams193="'+cams194,1)
exec(compile(src,'render193','exec'))
