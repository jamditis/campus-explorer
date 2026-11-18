cams178="camz('WS178_CAM_closeup_Lot3_aisle_S_drive_lawn_edge',(-299.5,-246.0,0),(-308.0,-236.0),28,1.6,0.0)\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws177/render177.py').read()
src=src.replace('cams177="','cams177="'+cams178,1)
exec(compile(src,'render177','exec'))
