import bpy
exec(open('scripts/pq/pq_probe.py').read().split("probe('PK")[0])
pts=[(x,y) for x in range(380,440,10) for y in range(200,350,25)]
probe('PK_CAM_oblique_feliciano_from_NW',pts)
probe('PK_CAM_eye_feliciano_NW',[(x,y) for x in range(290,350,10) for y in range(10,90,20)])
