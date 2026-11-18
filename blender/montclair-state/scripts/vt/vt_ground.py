import bpy
from mathutils import Vector as V
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for x in [-86,-87.5,-89]:
  for dy in [0.3,1.0,1.8,2.6,3.5,5]:
    # wall y at x approx
    yw=-170.83+(x+84.96)/(-5.34)*1.25
    p=V((x+0.228*dy, yw+0.974*dy, 140))
    hit,loc,n,i,o,m=sc.ray_cast(dg,p,V((0,0,-1)))
    print('GR',x,dy,round(loc.z,2) if hit else None,o.name[:40] if hit else None)
