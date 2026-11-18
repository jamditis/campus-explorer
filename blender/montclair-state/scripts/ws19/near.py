import bpy
from mathutils import Vector
P=Vector((-43.0,-68.6,144.0))
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    mn=Vector([min(v[i] for v in bb) for i in range(3)]); mx=Vector([max(v[i] for v in bb) for i in range(3)])
    if all(mn[i]-2<=P[i]<=mx[i]+2 for i in range(3)) and (mx-mn).length<200:
        print('N',o.name,[round(x,2) for x in mn],[round(x,2) for x in mx],len(o.data.polygons))
