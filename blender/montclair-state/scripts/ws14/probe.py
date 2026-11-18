import bpy
for o in bpy.data.objects:
    n=o.name
    if 'cole' in n.lower() or 'COLE' in n:
        bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box] if o.type=='MESH' else []
        mn=[round(min(v[i] for v in bb),1) for i in range(3)] if bb else ''
        mx=[round(max(v[i] for v in bb),1) for i in range(3)] if bb else ''
        mats=[s.material.name for s in o.material_slots if s.material] if o.type=='MESH' else []
        print('OBJ',n,o.type,len(o.data.polygons) if o.type=='MESH' else '',mn,mx,mats[:6],[m.type for m in o.modifiers][:4], o.hide_render)
