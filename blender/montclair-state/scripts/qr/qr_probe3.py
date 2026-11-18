import bpy
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
sc.render.resolution_x=1024; sc.render.resolution_y=576
for cn,pxs in (('QP_CAM_eye_richardson_from_SE',((60,520),(120,490),(180,475),(30,560))),('QQ_CAM_closeup_richardson_SW_entrance',((100,500),(250,470),(600,500),(900,540)))):
    cam=bpy.data.objects[cn]; sc.camera=cam
    fr=cam.data.view_frame(scene=sc); M=cam.matrix_world; tr,br,bl,tl=[M@v for v in fr]; o=M.translation
    for (px,py) in pxs:
        p=tl+(tr-tl)*(px/1024)+(bl-tl)*(py/576)
        ok,loc,n,i,ob,m=sc.ray_cast(dg,o,(p-o).normalized()); ms=''
        if ok and ob.type=='MESH':
            me=ob.evaluated_get(dg).data
            if i<len(me.polygons) and me.materials: ms=me.materials[me.polygons[i].material_index].name
        print('HIT',cn[-12:],(px,py),ok and [round(c,1) for c in loc],ob.name if ok else None,ms)
