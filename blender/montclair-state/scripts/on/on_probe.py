import bpy, mathutils
sc=bpy.context.scene; cam=bpy.data.objects['OH_CAM_eye_schmitt_SSW_end']
sc.render.resolution_x=1024; sc.render.resolution_y=576
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl
tr,br,bl,tl=fr
M=cam.matrix_world; o=M.translation
for px,py in [(118,100),(110,85),(125,115),(105,95),(130,90),(118,125),(30,80),(20,300)]:
    u=px/1024; v=py/576
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    d=(M.to_3x3()@p).normalized()
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,o,d)
    print('PX',px,py,hit, ob.name if ob else None, tuple(round(c,2) for c in loc), tuple(round(c,2) for c in nor), (ob.parent.name if ob and ob.parent else ''))
