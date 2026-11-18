cams193="camz('WS193_CAM_closeup_ramp_W_curb_from_SE',(-307.6,-245.0,0),(-311.6,-237.6),30,1.6,0.0)\\\\\\\\\\\\\\\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws192/render192.py').read()
src=src.replace('cams192="','cams192="'+cams193,1)
exec(compile(src,'render192','exec'))
