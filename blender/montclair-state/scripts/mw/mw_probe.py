import bpy
from mathutils import Vector
for o in bpy.data.objects:
    n=o.name
    if any(k in n.lower() for k in ['newsroom','ccom','school of comm','scm','news']):
        if o.type=='MESH' or o.type=='FONT':
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]
            mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
            print("OBJ|%s|%s|%s|hide=%s|col=%s|%s|%s|nf=%d"%(n,o.type,o.data.name if o.data else '',o.hide_render,[c.name for c in o.users_collection],[round(x,2) for x in mn],[round(x,2) for x in mx], len(o.data.polygons) if o.type=='MESH' else 0))
