cams169="camz('WS169_CAM_closeup_bank_S_end_from_SW',(-317.5,-239.0,0),(-306.0,-224.0),28,1.7,0.3)\ncamz('WS169_CAM_eye_light_standard_from_lane_S',(-309.0,-222.0,0),(-305.5,-204.8),24,1.7,8.0)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws165/render165.py').read()
src=src.replace('cams165="','cams165="'+cams169.replace('\n','\\n'),1)
exec(compile(src,'render165','exec'))
