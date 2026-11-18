import bpy,numpy as np
from mathutils import Vector
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=O['WB_CAM_closeup_435_walk_north_edge_from_E']
from bpy_extras.object_utils import world_to_camera_view
# pixels of crack in 1024x576 image: approx (450,265),(560,275),(640,280),(690,295),(740,275)
mw=cam.matrix_world; fr=cam.data.view_frame(scene=sc)
tr,br,bl,tl=[mw@v for v in fr]
for px,py in [(455,266),(575,272),(640,282),(690,293),(745,276),(600,275)]:
    u=px/1024; v=py/576
    top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; p=top+(bot-top)*v
    d=(p-mw.translation).normalized(); o=mw.translation.copy(); hits=[]
    for _ in range(6):
        h=sc.ray_cast(dg,o,d)
        if not h[0]: break
        hits.append((h[4].name[:40],[round(c,2) for c in h[1]],round(h[2].z,2))); o=h[1]+d*0.005
    print('PX',px,py,hits[:4])
