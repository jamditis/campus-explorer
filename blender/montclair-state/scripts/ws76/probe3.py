import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for y in (-86,-90):
  r=[]
  for i in range(30):
    x=-248+i*0.15
    h=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
    r.append((round(x,2),h[4].name[:10] if h[4] else None, round(h[1].z,2)))
  print('P76r',y,[t for t in r if not t[1].startswith('WS75_spra')],flush=True)
