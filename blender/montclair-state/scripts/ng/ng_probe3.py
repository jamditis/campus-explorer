import bpy, mathutils
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
# hide same as aerial? just probe visible-render objects
A=bpy.data.objects['NG_CAM_aerial_cutaway']
A.location=(-34,-36,178); d=mathutils.Vector((-2,2,138))-A.location; A.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); A.data.lens=26
dg.update()
for p in [(-11,11,137.7),(5,10,137.7),(12,-5,137.4),(20,-20,137.4),(15.2,10,140)]:
    v=world_to_camera_view(sc,A,mathutils.Vector(p)); print('AER',p,round(v.x,2),round(1-v.y,2))
B=bpy.data.objects['NG_CAM_eye_balcony_down']
M=B.matrix_world
for sx in (-0.3,0,0.3):
  for sy in (-0.3,0,0.3):
    dirv=(M.to_3x3()@mathutils.Vector((sx,sy,-1))).normalized()
    hit,loc,n,i,ob,_=sc.ray_cast(dg,M.translation,dirv)
    print('BAL',sx,sy,hit and ob.name, hit and tuple(round(c,2) for c in loc))
