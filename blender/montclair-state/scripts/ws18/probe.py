import bpy,sys
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws5'); import cams
cams.CAMS.update({'WS10_CAM_eye_walk_from_sign_E':((-80.5,-57.6,136.5),(-50,-54,135.6),28)}); sc=bpy.context.scene; cams.ensure(sc)
bpy.context.view_layer.update()
cam=bpy.data.objects['WS10_CAM_eye_walk_from_sign_E']
sc.render.resolution_x=1280; sc.render.resolution_y=720
tr,br,bl,tl=[cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]; o=cam.matrix_world.translation
dg=bpy.context.evaluated_depsgraph_get()
W,H=1024,576
for px in range(568,632,12):
  for py in range(106,120,1):
    u=px/W; v=py/H
    top=tl+(tr-tl)*u; bot=bl+(br-bl)*u; p=top+(bot-top)*v
    d=(p-o).normalized()
    hit,loc,nor,idx,ob,m=sc.ray_cast(dg,o,d)
    mat='';back=''
    if hit and ob.type=='MESH':
        me=ob.evaluated_get(dg).data; poly=me.polygons[idx]
        mat=me.materials[poly.material_index].name if me.materials else ''
        wn=(ob.matrix_world.to_3x3()@poly.normal).normalized()
        back='BACK' if wn.dot(d)>0 else 'front'
    print('HIT',(px,py),hit and ob.name,[round(x,2) for x in loc],[round(x,2) for x in nor],idx,mat,back,flush=True)
