import bpy
for o in bpy.data.objects:
    if o.type in('MESH','CAMERA') and ('feliciano' in o.name.lower()):
        bb=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box]
        print('BB',o.name[:60],'|',[round(min(v[i] for v in bb),1) for i in range(3)],[round(max(v[i] for v in bb),1) for i in range(3)],'|',[c.name for c in o.users_collection][:1],[s.link+':'+(s.material.name if s.material else '-') for s in o.material_slots][:4],[m.name for m in o.modifiers][:4], o.hide_render)
