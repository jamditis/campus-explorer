import bpy, sys
from mathutils import Vector
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws5'); import cams
sc=bpy.context.scene
cams.CAMS.update({'WS16_CAM_closeup_addition_eave_from_E':((-80,-68,146.5),(-93.5,-75,143.2),32)}); cams.ensure(sc)
bpy.context.view_layer.update()
cam=bpy.data.objects['WS16_CAM_closeup_addition_eave_from_E']
print('CAMLOC',cam.matrix_world.translation[:])
sc.render.resolution_x=1024; sc.render.resolution_y=576; sc.render.resolution_percentage=100
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl
tr,br,bl,tl=[cam.matrix_world@v for v in fr]
o=cam.matrix_world.translation
dg=bpy.context.evaluated_depsgraph_get()
for (px,py,lab) in [(650,281,'whiteline'),(400,226,'whiteline2'),(700,330,'teeth'),(500,300,'teeth2'),(100,245,'mainfascia'),(250,238,'corner')]:
    u=px/1024; v=py/576
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    d=(p-o).normalized()
    hit,loc,n,idx,ob,_=sc.ray_cast(dg,o,d)
    print('HIT',lab,ob.name if ob else None,[round(x,2) for x in loc],idx, ob.material_slots[ob.data.polygons[idx].material_index].material.name if ob and idx<len(ob.data.polygons) else '')
