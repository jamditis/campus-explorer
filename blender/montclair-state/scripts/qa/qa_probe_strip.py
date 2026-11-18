import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['QA_CAM_eye_dickson_south_end']; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl in cam space
mw=cam.matrix_world
for (u,v) in ((0.509,0.52),(0.509,0.30),(0.509,0.08),(0.513,0.45),(0.757,0.42),(0.76,0.2)):
    tl,bl,br=fr[3],fr[2],fr[1]
    p=bl+(br-bl)*u+(tl-bl)*v
    d=(mw.to_3x3()@p).normalized()
    ok,loc,n,i,o,m=sc.ray_cast(dg,mw.translation,d)
    print('PIX %.3f %.2f'%(u,v), o.name if ok else None, tuple(round(c,2) for c in loc) if ok else '', [s.material.name for s in o.material_slots][:3] if ok else '', m if ok else '')
