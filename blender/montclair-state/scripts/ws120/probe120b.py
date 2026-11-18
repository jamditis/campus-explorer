import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
    if mx[0]<-217.5 or mn[0]>-211 or mx[1]<-206 or mn[1]>-201.0 or mn[2]>127: continue
    print('Q',o.name[:70],[round(v,2) for v in mn],[round(v,2) for v in mx], len(o.data.polygons))
