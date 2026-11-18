import bpy
from mathutils import Vector
for c in bpy.data.collections:
    if c.name.startswith('COLE') or 'Cole' in c.name:
        print('COL', c.name, [(o.name, o.type, len(o.data.polygons) if o.type=='MESH' else 0, o.hide_render, o.hide_viewport) for o in c.objects])
for o in bpy.data.objects:
    if ('Cole' in o.name or o.name.startswith('COLE')) and not any(c.name.startswith('COLE') for c in o.users_collection):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('OBJ', o.name, [c.name for c in o.users_collection], o.type, round(min(v.x for v in bb),1), round(max(v.x for v in bb),1), round(min(v.y for v in bb),1), round(max(v.y for v in bb),1), o.hide_render)
