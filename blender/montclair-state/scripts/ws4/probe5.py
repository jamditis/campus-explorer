import bpy
from mathutils import Vector
for o in bpy.data.objects:
  if o.type not in ('MESH','CURVE'): continue
  cs=[o.matrix_world@Vector(c) for c in o.bound_box]
  lo=[min(c[i] for c in cs) for i in range(3)]; hi=[max(c[i] for c in cs) for i in range(3)]
  d=[hi[i]-lo[i] for i in range(3)]
  if lo[0]<-110 and hi[0]>-150 and lo[1]<-30 and hi[1]>-75 and lo[2]>136 and lo[2]<143 and d[2]<1.5 and max(d[0],d[1])<30 and max(d[0],d[1])>2:
    print('T',o.name,[round(x,1) for x in lo],[round(x,1) for x in hi],o.hide_render)
