import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    lo=[min(v[i] for v in bb) for i in range(3)]; hi=[max(v[i] for v in bb) for i in range(3)]
    if lo[0]<-15 and hi[0]>-19 and lo[1]<-9.5 and hi[1]>-12 and lo[2]<137.6 and hi[2]>137.42 and hi[2]<138.0:
        print('RIS',o.name,[round(x,2) for x in lo],[round(x,2) for x in hi])
