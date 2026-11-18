import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for z in (144.8,145.5,146.3,147.0):
  for y in (194,195,196,196.5,197,197.5,198,198.2):
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,Vector((-130,y,z)),Vector((1,0,0)))
    print('H z',z,'y',y,ob and ob.name,round(loc.x,2))
