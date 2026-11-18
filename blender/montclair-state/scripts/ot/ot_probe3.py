import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
scn=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['OQ_CAM_eye_calcia_skirt_windows']
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=scn)]  # tr, br, bl, tl
o=cam.matrix_world.translation
def ray(px,py):
    u=px/1024; v=1-py/576
    tl,tr,br,bl=fr[3],fr[0],fr[1],fr[2]
    p=bl+(br-bl)*u+(tl-bl)*v
    return scn.ray_cast(dg,o,(p-o).normalized(),distance=500)
for px,py in [(30,330),(100,320),(160,300),(200,350),(100,290),(300,300),(60,370)]:
    h,loc,nor,i,ob,m=ray(px,py)
    if not h: print('PX',px,py,'miss'); continue
    up=scn.ray_cast(dg,loc+Vector((0,0,0.05)),Vector((0,0,1)),distance=30)
    print('PX',px,py,ob.name,[round(x,2) for x in loc],[round(x,2) for x in nor],[m.name for m in ob.data.materials][:3] if ob.type=='MESH' else '', 'UP', up[0] and (up[4].name,round(up[1].z,2),[m.name for m in up[4].data.materials][:3]))
