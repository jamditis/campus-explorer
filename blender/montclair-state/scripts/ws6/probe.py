import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws5/probe_glass.py').read())
c=bpy.data.collections.get('WS4_Cole_walk_kit_20261109')
for o in c.all_objects: print('KIT',o.name,o.type,[round(x,2) for x in o.location],[round(x,2) for x in o.dimensions])
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']
print('TZ verts',len(TZ.data.vertices),'faces',len(TZ.data.polygons),'dims',[round(x,2) for x in TZ.dimensions],'loc',[round(x,2) for x in TZ.matrix_world.translation])
for m in TZ.material_slots:
  print('SLOT',m.material.name if m.material else None, m.material.users if m.material else 0)
for n in bpy.data.materials.keys():
  if 'tucco' in n or 'hite' in n or 'Cole' in n: print('MAT',n)
