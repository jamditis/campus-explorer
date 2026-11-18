import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['PO_CAM_closeup_feliciano_gutter_downpipe']; sc.camera=cam
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
tr,br,bl,tl=[mw@v for v in fr]
for px,py in [(200,230),(190,215),(115,195),(560,250),(600,255),(130,300),(470,120)]:
    u=px/640; v=py/360
    p=tl+(tr-tl)*u+(bl-tl)*v; o=mw.translation; d=(p-o).normalized()
    r=sc.ray_cast(dg,o,d)
    print('PX',px,py,r[4].name if r[0] else None,r[3],[round(x,2) for x in r[1]], [round(x,2) for x in r[2]])
