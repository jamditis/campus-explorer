import bpy
from mathutils import Vector
P=Vector((-39.5,-56.5,144.4))
dg=bpy.context.evaluated_depsgraph_get()
for inst in dg.object_instances:
    ob=inst.object
    if ob.type not in('MESH','CURVE','POINTCLOUD','CURVES'): continue
    mw=inst.matrix_world
    bb=[mw@Vector(c) for c in ob.bound_box]
    lo=[min(p[i] for p in bb) for i in range(3)]; hi=[max(p[i] for p in bb) for i in range(3)]
    if all(lo[i]-0.3<=P[i]<=hi[i]+0.3 for i in range(3)) and (hi[0]-lo[0])<200:
        print('BBHIT',ob.name,'inst' if inst.is_instance else '', 'parent',inst.parent.name if inst.parent else '', [round(x,1) for x in lo],[round(x,1) for x in hi], ob.visible_camera if hasattr(ob,'visible_camera') else '')
