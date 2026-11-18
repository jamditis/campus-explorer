import bpy
for o in bpy.data.objects:
    n=o.name.lower()
    if ('stair' in n or 'rail' in n or 'tread' in n or 'nosing' in n) and ('ccom' in n or n.startswith(('ng','nh','ni','nj','nk','nl','nm','nn','no','np','ns','nu'))):
        bb=[o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box] if o.type=='MESH' else []
        mn=[round(min(v[i] for v in bb),2) for i in range(3)] if bb else ''; mx=[round(max(v[i] for v in bb),2) for i in range(3)] if bb else ''
        print('P',o.name,o.type,o.hide_render,len(o.data.vertices) if o.type=='MESH' else '',mn,mx,[s.material.name if s.material else None for s in o.material_slots][:3])
