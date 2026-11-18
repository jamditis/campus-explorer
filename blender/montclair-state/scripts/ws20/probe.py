import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    n=o.name
    if o.type=='MESH' and any(k in n for k in ('Life Hall','CCOM','Communication','drip','Drip')) :
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        mn=[round(min(v[i] for v in bb),1) for i in range(3)]; mx=[round(max(v[i] for v in bb),1) for i in range(3)]
        print('BB',n,mn,mx,len(o.data.polygons))
