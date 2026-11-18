import bpy
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['QM_CAM_closeup_ccis_podium_edge_east']; fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world; o=mw.translation
for (px,py) in [(72,305),(78,312),(84,318),(90,322),(80,300),(70,315),(650,330),(690,330)]:
  u=px/768; v=1-py/432
  top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=bot.lerp(top,v); d=((mw@p)-o).normalized()
  h,loc,n,fi,ob,m=sc.ray_cast(dg,o,d)
  if h:
    e=ob.evaluated_get(dg); mn=e.material_slots[e.data.polygons[fi].material_index].name if e.material_slots else '?'
    print('PICK',px,py,ob.name,mn,tuple(round(c,2) for c in loc),tuple(round(c,2) for c in n))
