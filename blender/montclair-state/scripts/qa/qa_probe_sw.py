import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['QA_CAM_eye_feliciano_sw_slope']; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl in cam space
mw=cam.matrix_world
for (u,v) in ((0.05,0.05),(0.12,0.15),(0.2,0.08),(0.3,0.25),(0.5,0.3),(0.7,0.3),(0.5,0.1),(0.9,0.2)):
    tl,bl,br=fr[3],fr[2],fr[1]
    p=bl+(br-bl)*u+(tl-bl)*v
    d=(mw.to_3x3()@p).normalized()
    ok,loc,n,i,o,m=sc.ray_cast(dg,mw.translation,d)
    print('PIX %.2f %.2f'%(u,v), o.name if ok else None, tuple(round(c,1) for c in loc) if ok else '')
