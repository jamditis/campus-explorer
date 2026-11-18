import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb);z1=max(p.z for p in bb)
    if max(x1-x0,y1-y0)>250: continue
    if x1>60 and x0<200 and y1>150 and y0<260 and z1>145: print('B',o.name[:70],round(x0),round(x1),round(y0),round(y1),round(z1))
