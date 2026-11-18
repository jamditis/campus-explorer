import bpy
for o in bpy.data.objects:
    if ('Calcia' in o.name or 'calcia' in o.name) and o.type=='MESH': print('NM',o.name,[s.material.name for s in o.material_slots if s.material][:2],[u.name for u in o.data.uv_layers])
