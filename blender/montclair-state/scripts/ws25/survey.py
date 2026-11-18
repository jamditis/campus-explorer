import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if 'artridge' in o.name or 'PARTRIDGE' in o.name.upper():
        if o.type=='MESH':
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]
            mn=[min(v[i] for v in bb) for i in range(3)]; mx=[max(v[i] for v in bb) for i in range(3)]
            print('OBJ',o.name,len(o.data.polygons),[c.name for c in o.users_collection],[round(x,1) for x in mn],[round(x,1) for x in mx],[m.name if m else None for m in o.data.materials],[m.type for m in o.modifiers])
        else: print('OBJ',o.name,o.type)
