import bpy
F=bpy.data.objects['Footpaths_OSM']
print('FOOT mats',[s.material.name if s.material else None for s in F.material_slots], len(F.data.polygons))
import collections
c=collections.Counter(p.material_index for p in F.data.polygons); print(c)
for s in F.material_slots:
  m=s.material
  if m and m.use_nodes:
    print(' MAT',m.name,[n.bl_idname for n in m.node_tree.nodes][:30], 'users',m.users)
J=bpy.data.objects.get('Footpath control + expansion joints (3h)')
print('J',J and [s.material.name for s in J.material_slots])
for o in bpy.data.objects:
  n=o.name.lower()
  if any(k in n for k in ('cole','morehead','ccom','comm')) and o.type in ('MESH','EMPTY') and len(n)<60:
    print('OBJ',o.name,tuple(round(x,1) for x in o.location), o.type, [c.name for c in o.users_collection][:1], tuple(round(x,1) for x in o.dimensions))
for c in bpy.data.cameras: pass
print('CAMS',[o.name for o in bpy.data.objects if o.type=='CAMERA' and ('cole' in o.name.lower())])
print('MAT WS3',[m.name for m in bpy.data.materials if m.name.startswith('WS3')])
