import bpy
for o in bpy.data.objects:
    if 'freeman' in o.name.lower():
        bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
        print('FO',repr(o.name),o.type,o.hide_render,len(o.data.polygons) if o.type=='MESH' else '', [round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)],o.users_collection[0].name, len(o.modifiers), [m.type for m in o.modifiers])
