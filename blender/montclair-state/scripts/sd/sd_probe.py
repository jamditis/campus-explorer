import bpy
for o in bpy.data.objects:
    n=o.name
    if any(k in n.lower() for k in ['mural','redhawk','red_hawk','letter']) or n.startswith('RZ') or 'StudentCenter' in n or 'Annex' in n:
        print('OBJ',n,o.type,[s.material.name if s.material else None for s in o.material_slots][:6], o.users_collection[0].name if o.users_collection else '', o.hide_render, len(o.data.polygons) if o.type=='MESH' else '')
for c in bpy.data.collections:
    if 'SB_' in c.name or 'SC_' in c.name or 'SA_' in c.name: print('COL',c.name,len(c.objects))
for m in bpy.data.materials:
    if m.name.startswith(('SC_','SB_')): print('MAT',m.name,m.users)
