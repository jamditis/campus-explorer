import bpy
from mathutils import Vector
O=bpy.data.objects
for o in O:
    if o.type=='MESH' and ('newsroom' in o.name or 'studio' in o.name.lower()) and not o.hide_render:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        mn=[round(min(v[i] for v in bb),2) for i in range(3)]; mx=[round(max(v[i] for v in bb),2) for i in range(3)]
        print('OBJ',o.name,len(o.data.polygons),mn,mx,[s.material.name if s.material else None for s in o.material_slots][:3])
print('N',len(O))
