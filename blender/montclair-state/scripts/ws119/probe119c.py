import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.name.startswith('WS117'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('BB',o.name[:50],[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])
o=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_landing')); mw=o.matrix_world
print('LV',sorted(set((round((mw@v.co).x,2),round((mw@v.co).y,2)) for v in o.data.vertices if (mw@v.co).z>124.7)))
