import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['PO_CAM_closeup_feliciano_gutter_downpipe']
dg=bpy.context.evaluated_depsgraph_get(); fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
tr,br,bl,tl=[mw@v for v in fr]
for px,py in [(790,395),(800,420),(600,360),(130,195),(125,205)]:
    u=px/1024; v=py/576; p=tl+(tr-tl)*u+(bl-tl)*v; o=mw.translation.copy(); d=(p-o).normalized()
    for k in range(3):
        r=sc.ray_cast(dg,o,d)
        if not r[0]: print('PX',px,py,k,None); break
        print('PX',px,py,k,r[4].name,[round(x,2) for x in r[1]],[round(x,2) for x in r[2]]); o=r[1]+d*0.02
