import bpy
from bpy_extras.view3d_utils import region_2d_to_vector_3d
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['UA_CAM_oblique_NormalAve_from_SW']
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl
mw=cam.matrix_world
for (px,py) in [(750,295),(700,280),(720,330),(700,380),(640,330),(660,260)]:
    u=px/1280; v=py/720
    tl,tr,bl=fr[3],fr[0],fr[2]
    p=tl+(tr-tl)*u+(bl-tl)*v
    o=mw.translation; d=(mw@p-o).normalized()
    hit,loc,n,i,ob,m=sc.ray_cast(dg,o,d)
    print('PICK',px,py,hit and ob.name, tuple(round(c,1) for c in loc) if hit else None, ob and ob.users_collection[0].name)
