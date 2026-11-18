import bpy, math
from mathutils import Vector
cam=bpy.data.objects['CAM_eye_cole_hall_northwest_br']
from bpy_extras.object_utils import world_to_camera_view as w2c
sc=bpy.context.scene
print('CAMROT',[round(math.degrees(a)) for a in cam.rotation_euler])
for o in sc.objects:
  if o.type not in('MESH','CURVE') or o.hide_render: continue
  ctr=o.matrix_world@ (sum((Vector(k) for k in o.bound_box),Vector())/8)
  if (ctr-cam.matrix_world.translation).length>40: continue
  p=w2c(sc,cam,ctr)
  if p.z>0 and 0.1<p.x<0.45 and 0.3<p.y<0.8:
    print('VIS',o.name,[round(v,1) for v in ctr],round(p.x,2),round(p.y,2),[round(v,1) for v in o.dimensions],[x.name for x in o.users_collection][:1])
