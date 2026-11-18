import bpy,sys
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws5'); import cams
cams.CAMS.update({'WS14_CAM_oblique_addition_east_from_SE':((-70,-95,152),(-95,-72,138),26)}); sc=bpy.context.scene; cams.ensure(sc)
bpy.context.view_layer.update()
cam=bpy.data.objects['WS14_CAM_oblique_addition_east_from_SE']; print('CAMLOC',cam.matrix_world.translation, cam.data.lens, cam.data.sensor_fit)
sc.render.resolution_x=1280; sc.render.resolution_y=720
fr=[cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
# frame order: TR, BR, BL, TL
tr,br,bl,tl=fr; o=cam.matrix_world.translation
dg=bpy.context.evaluated_depsgraph_get()
W,H=1024,576
for (px,py) in [(190,468),(160,462),(220,470),(473,340),(508,328),(147,190),(215,300),(265,300)]:
    u=px/W; v=py/H
    top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; p=top+(bot-top)*v
    d=(p-o).normalized()
    hit,loc,nor,idx,ob,m=sc.ray_cast(dg,o,d)
    mat=''
    if hit and ob.type=='MESH':
        try:
            me=ob.evaluated_get(dg).data; mi=me.polygons[idx].material_index; mat=me.materials[mi].name if me.materials else ''
        except Exception as e: mat=str(e)
    print('HIT',(px,py),hit and ob.name,[round(x,2) for x in loc],[round(x,2) for x in nor],idx,mat,flush=True)
