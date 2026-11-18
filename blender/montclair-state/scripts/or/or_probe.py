import bpy
for k in ['Computing','Environmental','Speech','Calcia']:
    for o in bpy.data.objects:
        if k in o.name: print(o.name, o.type, len(o.data.polygons) if o.type=='MESH' else '', [s.material.name if s.material else None for s in o.material_slots][:6], [m.type for m in o.modifiers])
