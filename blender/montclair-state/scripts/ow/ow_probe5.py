import bpy
from bpy_extras.view3d_utils import region_2d_to_vector_3d
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['OR_CAM_eye_CELS_skirt_windows_base_course']; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); W,H=1024,576
for px,py in [(880,400),(920,420),(960,440),(990,460),(900,470),(950,400),(1010,420),(850,380)]:
    u=px/W; v=1-py/H
    tr,br,bl,tl=fr; p=bl+(br-bl)*u+(tl-bl)*v
    d=(cam.matrix_world.to_3x3()@p).normalized(); o=cam.matrix_world.translation
    ok,loc,n,i,ob,mx=sc.ray_cast(dg,o,d)
    print('HIT',px,py,ob.name if ok else None,tuple(round(c,2) for c in loc) if ok else '', round(n.z,3) if ok else '')
