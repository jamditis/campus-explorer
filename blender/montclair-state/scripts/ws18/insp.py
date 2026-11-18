import bpy
from mathutils import Vector
ob=bpy.data.objects['Eave drip / moss streaks on stucco (3g)']
me=ob.data; mw=ob.matrix_world
print('OBJ',ob.name,len(me.polygons),'mods',[m.type for m in ob.modifiers],'users',me.users, 'parent',ob.parent and ob.parent.name)
for i in range(262,290):
    if i>=len(me.polygons): break
    p=me.polygons[i]; vs=[mw@me.vertices[v].co for v in p.vertices]
    n=(mw.to_3x3()@p.normal).normalized()
    print(i,[ (round(v.x,2),round(v.y,2),round(v.z,2)) for v in vs],[round(x,2) for x in n])
# Morehead wall: ray from west at y -56, z 140 heading +x
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for z in (138,141,143,143.5,144):
  h=sc.ray_cast(dg,Vector((-60,-56.5,z)),Vector((1,0,0)))
  print('WALLRAY z',z,h[0] and h[4].name,[round(x,2) for x in h[1]])
