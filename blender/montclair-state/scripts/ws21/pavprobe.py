import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=Vector((33.9,121.8,138.6))
for tx,ty in [(30,116),(28,112),(25,114),(33,113),(22,110),(36,117),(30,108)]:
    d=(Vector((tx,ty,135))-o).normalized()
    hit,loc,n,i,ob,m=sc.ray_cast(dg,o,d)
    print('HIT',(tx,ty),ob.name if ob else None,[round(x,2) for x in loc] if hit else None, round(n.z,2) if hit else None, [s.material.name for s in ob.material_slots if s.material][:3] if hit else None)
