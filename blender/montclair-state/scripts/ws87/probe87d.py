import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x in range(-270,-205,6):
  for y in (-72,-69,-66):
    ok,loc,n,i,o,_=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
    if ok:
      ms=o.data.materials if o.type=='MESH' else []
      mi=o.data.polygons[i].material_index if o.type=='MESH' and i<len(o.data.polygons) else -1
      print('P87',x,y,round(loc.z,2),o.name[:50],ms[mi].name if 0<=mi<len(ms) and ms[mi] else mi)
