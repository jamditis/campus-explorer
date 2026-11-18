import bpy
from mathutils import Vector
o=bpy.data.objects['TX Partridge core: dark glazing behind frame (UNVERIFIED)']
mw=o.matrix_world
for p in o.data.polygons:
    vs=[mw@o.data.vertices[i].co for i in p.vertices]
    print('F',p.index,o.material_slots[p.material_index].name,round(p.normal.z,2),[(round(v.x,1),round(v.y,1),round(v.z,1)) for v in vs])
f=bpy.data.objects['TX Partridge precast frame: piers, spandrels, top band, plinth ']if 'TX Partridge precast frame: piers, spandrels, top band, plinth ' in bpy.data.objects else [x for x in bpy.data.objects if x.name.startswith('TX Partridge precast frame')][0]
print('FRAME',f.name)
import collections
c=collections.Counter(f.material_slots[p.material_index].name for p in f.data.polygons); print(c)
zs=collections.Counter(round((f.matrix_world@f.data.vertices[i].co).z,1) for p in f.data.polygons for i in p.vertices); print(sorted(zs.items())[-12:])
for m in bpy.data.materials:
    n=m.name.lower()
    if 'tile' in n and m.users>0: print('MAT',m.name,m.users)
for m in ['TX_Partridge_precast_concrete_UNVERIFIED','TX_Partridge_brown_brick_UNVERIFIED','TX_Partridge_bronze_mullion_UNVERIFIED','TX_Partridge_base_grime_UNVERIFIED']:
    mm=bpy.data.materials[m]; print('USERS',m,mm.users,[n.type for n in mm.node_tree.nodes])
