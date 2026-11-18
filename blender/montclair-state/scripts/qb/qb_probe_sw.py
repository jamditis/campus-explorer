import bpy
sc=bpy.context.scene; cam=bpy.data.objects['QA_CAM_eye_feliciano_sw_slope']; dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world
print('CAM',tuple(round(c,2) for c in mw.translation))
for (u,v) in ((0.05,0.1),(0.15,0.12),(0.22,0.08),(0.3,0.12),(0.4,0.25),(0.6,0.3),(0.9,0.2),(0.5,0.05)):
    tl,bl,br=fr[3],fr[2],fr[1]; p=bl+(br-bl)*u+(tl-bl)*v
    d=(mw.to_3x3()@p).normalized(); ok,loc,n,i,o,m=sc.ray_cast(dg,mw.translation,d)
    extra=''
    if ok and o.name.startswith(('PZ_','PK_')):
        me=o.data; a=me.attributes.get('qb_fade')
        if a: extra='fade %.2f'%a.data[me.polygons[i].vertices[0]].value
    print('PIX %.2f %.2f'%(u,v), o.name if ok else None, tuple(round(c,1) for c in loc) if ok else '', o.material_slots[0].material.name if ok and o.material_slots else '', extra)
