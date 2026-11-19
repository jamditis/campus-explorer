import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
# along the WS69 N curb back line (-252.349,-54.484)->(-249.345,-56.05), offsets n (m, + = north/away from road)
A=Vector((-252.349,-54.484)); B=Vector((-249.345,-56.05)); d=(B-A).normalized(); nrm=Vector((-d.y,d.x))
if nrm.y<0: nrm=-nrm
for t in (-1.0,-0.6,-0.3,0.0,0.3,0.6,0.9,1.2):
  row=[]
  for off in (-0.1,-0.03,0.0,0.03,0.06,0.1,0.15,0.25):
    p=A+d*t+nrm*off; o=Vector((p.x,p.y,127)); h,loc,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
    row.append('%s%.0f'%(ob.name[:4],(loc.z-125)*100) if h else '-')
  print('P221 t%.1f '%t+' '.join(row))
