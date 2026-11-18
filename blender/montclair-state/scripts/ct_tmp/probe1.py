import bpy, mathutils, math
from mathutils import Vector
sc=bpy.context.scene
L=Vector((-167.08,-83.42,132.50)); T=Vector((-185.45,-59.70,134.20))
d=(T-L).normalized()
q=d.to_track_quat('-Z','Y')
lens=26; sw=36.0; W,H=1280,720
dg=bpy.context.evaluated_depsgraph_get()
fx=sw/lens; fy=fx*H/W
seen={}
for py in range(430,520,10):
  for px in range(640,900,20):
    nx=(px/W-0.5)*fx; ny=(0.5-py/H)*fy
    r=(q@Vector((nx,ny,-1))).normalized()
    hit,loc,n,i,o,m=sc.ray_cast(dg,L,r)
    nm=o.name if o else None
    print('PX',px,py,nm[:50] if nm else None, tuple(round(c,2) for c in loc) if hit else None, flush=True)
# objects near gap
for o in bpy.data.objects:
  if o.type!='MESH' or o.hide_render: continue
  bb=[o.matrix_world@Vector(c) for c in o.bound_box]
  x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
  if x1>-200 and x0<-170 and y1>-75 and y0<-55 and (x1-x0)<80:
    print('OBJ',o.name[:60],round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(min(v.z for v in bb),2),round(max(v.z for v in bb),2))
