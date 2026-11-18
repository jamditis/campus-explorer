import bpy
from mathutils import Vector
from bpy_extras.view3d_utils import region_2d_to_vector_3d
sc=bpy.context.scene; cam=bpy.data.objects['QP_CAM_eye_richardson_from_SE']; dg=bpy.context.evaluated_depsgraph_get()
sc.render.resolution_x=1024; sc.render.resolution_y=576
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
tl,bl=fr[3],fr[2]; tr=fr[0]
def ray(px,py):
    u=px/1024; v=py/576
    p=fr[3]+(fr[0]-fr[3])*u+(fr[2]-fr[3])*v
    o=mw.translation; d=(mw@p-o).normalized()
    r=sc.ray_cast(dg,o,d)
    return r
for py in (470,480,488,493,498,503,510):
  for px in (350,600):
    r=ray(px,py); print('PICK',px,py,r[0], r[4].name if r[0] else None, tuple(round(c,2) for c in r[1]) if r[0] else None, r[3])
