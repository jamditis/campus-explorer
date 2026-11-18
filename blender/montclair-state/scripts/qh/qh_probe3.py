import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.hide_render: continue
    n=o.name.lower()
    if o.type in('POINTCLOUD','CURVES') or 'grass' in n or 'lamp' in n or 'bench' in n or o.type=='MESH' and any(m.type=='NODES' for m in o.modifiers) and ('scatter' in n or 'tuft' in n):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
        if y1>140 and x1>-220 and y0<262:
            print('G',o.name,o.type,[round(x0),round(x1),round(y0),round(y1),round(min(v.z for v in bb),1)],[m.name for m in o.modifiers][:4])
