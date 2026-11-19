import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-56.3,-56.5,-56.8,-57.2):
  row=[]
  for k in range(26):
    x=-249.55+k*0.02
    o=Vector((x,y,127.0)); h,loc,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
    row.append('%s%.0f'%(ob.name[:4] if h else '-', (loc.z-125)*100 if h else 0))
  print('P221 y%.1f '%y+' '.join(row))
