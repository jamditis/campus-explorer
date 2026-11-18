cams189="camz('WS189_CAM_closeup_Sprague_goalpost_from_SE',(-342.5,-216.5,0),(-349.4,-211.0),28,1.7,2.6)\\ncamz('WS189_CAM_oblique_Sprague_goalpost_Lot36_from_SE_high',(-318.0,-234.0,0),(-340.0,-212.0),24,22.0,0.0)\\n"
src=open('/workspace/nj-scenes/montclair-state/scripts/ws188/render188.py').read()
src=src.replace('cams188="','cams188="'+cams189,1)
exec(compile(src,'render188','exec'))
