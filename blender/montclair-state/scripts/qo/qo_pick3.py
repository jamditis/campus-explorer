import bpy
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['QK_CAM_eye_NE_road_ends_from_west']; fr=cam.data.view_frame(scene=sc); mw=cam.matrix_world; o=mw.translation
print('CAMLOC',tuple(round(c,1) for c in o))
for (px,py) in [(100,440),(110,447),(125,450),(150,452),(160,447),(440,388),(300,450)]:
  u=px/1024; v=1-py/576
  top=fr[3].lerp(fr[0],u); bot=fr[2].lerp(fr[1],u); p=bot.lerp(top,v); d=((mw@p)-o).normalized()
  h,loc,n,fi,ob,m=sc.ray_cast(dg,o,d)
  if h:
    e=ob.evaluated_get(dg); mn=e.material_slots[e.data.polygons[fi].material_index].name if e.material_slots else '?'
    print('PICK',px,py,ob.name,mn,tuple(round(c,1) for c in loc))
for mn in ('Ground_ortho_grass',):
  pass
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; print('SKIRT mats',[s.name for s in sk.material_slots],[m.name for m in sk.modifiers])
