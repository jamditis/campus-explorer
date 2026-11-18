import bpy
from mathutils import Vector
for o in bpy.data.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb);z1=max(p.z for p in bb)
    if ('CELS' in o.name or 'Environmental' in o.name) or (x0>60 and x1<135 and y0>145 and y1<225 and o.type=='MESH' and not o.name.startswith('T_')):
        print('N',o.name[:70],o.type,o.hide_render,len(o.data.polygons) if o.type=='MESH' else 0,round(x0),round(x1),round(y0),round(y1),round(z1),[c.name for c in o.users_collection][:2])
