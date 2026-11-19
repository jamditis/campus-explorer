import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-56.3,-56.6,-57.0,-57.5):
  for x in (-250.2,-249.8,-249.5,-249.2,-248.9,-248.6):
    o=Vector((x,y,140)); s=[]
    for k in range(4):
        h,loc,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        s.append('%s@%.3f'%(ob.name[:38],loc.z)); o=loc-Vector((0,0,0.001))
    print('P221 %.1f %.1f '%(x,y)+' | '.join(s))
