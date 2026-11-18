import bpy
from mathutils import Vector
c=bpy.data.objects['Curbs_granite_OSM']
dg=bpy.context.evaluated_depsgraph_get(); e=c.evaluated_get(dg); me=e.to_mesh(); m=c.matrix_world
for (y0,x0,x1) in ((-45.2,-3,0),(-45.2,-9,-6),(-25,-3,0)):
  pts=sorted({(round((m@v.co).x,3),round((m@v.co).z,3)) for v in me.vertices if abs((m@v.co).y-y0)<0.4 and x0<(m@v.co).x<x1})
  print(y0,len(pts),pts[:40])
