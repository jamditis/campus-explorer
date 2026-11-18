import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['WS3_CAM_eye_cole_plaza_from_SW']
sc.render.resolution_x=1280; sc.render.resolution_y=720
dg=bpy.context.evaluated_depsgraph_get()
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr, br, bl, tl
o=cam.matrix_world.translation
def ray(px,py):
  u=px/1024; v=py/576
  top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=top.lerp(bot,v)
  ok,loc,n,i,ob,m=sc.ray_cast(dg,o,(p-o).normalized())
  return ok and (ob.name,i,tuple(round(c,2) for c in loc))
for px,py in [(700,480),(720,470),(690,500),(740,475),(600,520),(560,480),(860,520),(650,455)]: print('RAY',px,py,ray(px,py))
