import bpy, numpy as np
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
A=np.array([-250.1,-46.7]);B=np.array([-237.3,3.8]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
L=Vector((-167.08,-83.42,132.50));T=Vector((-185.45,-59.70,134.20)); q=(T-L).normalized().to_track_quat('-Z','Y'); fx=36/26; fy=fx*720/1280
for py in range(452,496,6):
  for px in range(780,860,10):
    r=(q@Vector(((px/1280-0.5)*fx,(0.5-py/720)*fy,-1))).normalized()
    h,l,nn,i,o,m=sc.ray_cast(dg,L,r)
    if h:
      p=np.array([l.x,l.y])-A
      print('PX',px,py,o.name[:30],'z %.2f s %.2f u %.2f'%(l.z,p@n,p@d),flush=True)
