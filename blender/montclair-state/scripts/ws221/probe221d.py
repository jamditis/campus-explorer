import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-55.0,-54.6,-54.2,-53.8,-53.4):
  row=[]
  for x in (-248.85,-248.75,-248.65,-248.55,-248.4):
    o=Vector((x,y,127.0)); s=[]
    for k in range(2):
        h,loc,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        s.append('%s@%.0f'%(ob.name[:14],(loc.z-125)*100)); o=loc-Vector((0,0,0.001))
    row.append('/'.join(s))
  print('P221 y%.1f '%y+'  '.join(row))
