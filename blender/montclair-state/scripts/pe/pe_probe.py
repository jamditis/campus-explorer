import bpy
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for y in (100,130):
  for i in range(0,44):
    z=142+i*0.25
    hit,loc,n,fi,ob,m=sc.ray_cast(dg,(-200,y,z),(1,0,0))
    if hit:
        ev=ob.evaluated_get(dg); mi=ev.data.polygons[fi].material_index if fi<len(ev.data.polygons) else -1
        sl=ob.material_slots[mi].material.name if mi<len(ob.material_slots) and ob.material_slots[mi].material else None
        print('P',y,z,round(loc.x,2),ob.name[:40],mi,sl, tuple(round(c,2) for c in n))
