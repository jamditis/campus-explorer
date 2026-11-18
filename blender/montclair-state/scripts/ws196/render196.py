cams194="camz('WS196_CAM_oblique_access_lot_from_SE',(-222.0,-102.0,0),(-238.0,-76.0),26,18.0,0.0)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ncamz('WS196_CAM_eye_access_rows_from_W',(-257.0,-75.5,0),(-232.0,-77.5),26,1.7,0.3)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ncamz('WS196_CAM_eye_access_lot_from_NE_aisle',(-222.0,-80.5,0),(-250.0,-86.0),26,1.7,0.3)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ncamz('WS196_CAM_closeup_ISA_stalls',(-243.5,-77.0,0),(-236.5,-73.5),28,1.9,0.0)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws193/render193.py').read()
src=src.replace('cams193="','cams193="'+cams194,1)
exec(compile(src,'render193','exec'))
