import bpy
from mathutils import Vector
for o in bpy.data.objects:
    nm=o.name.upper()
    if ('LETTER' in nm or 'HAWK' in nm or 'RHC' in nm) and o.type in('MESH','FONT','CURVE'):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        mn=[round(min(v[i] for v in bb),2) for i in range(3)]; mx=[round(max(v[i] for v in bb),2) for i in range(3)]
        print('OBJ',o.name,o.type,mn,mx,[m.name for m in o.data.materials if m],o.hide_render,[c.name for c in o.users_collection])
