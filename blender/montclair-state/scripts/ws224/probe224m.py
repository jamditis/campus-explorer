import bpy
o=[o for o in bpy.data.objects if o.name.startswith('WS70_gap_strip_grass')]
for x in o: print('P224',x.name,[s.material.name for s in x.material_slots if s.material],x.data.name, [c.name for c in x.users_collection], [m.type for m in x.modifiers])
W=[o for o in bpy.data.objects if o.name.startswith('WS71_Kasser_S_sidewalk')][0]; print('P224 WS71',W.name,[c.name for c in W.users_collection])
