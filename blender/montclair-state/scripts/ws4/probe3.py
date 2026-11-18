import bpy
from mathutils import Vector
P=Vector((-72,-52.2)); 
for o in bpy.data.objects:
  if o.type in('MESH','EMPTY','CURVE') :
    w=o.matrix_world.translation
    if (Vector((w.x,w.y))-P).length<9 and 'Footpath' not in o.name and 'Terrain' not in o.name: print('NEAR',o.name,tuple(round(x,1) for x in w))

for o in bpy.data.objects:
  if o.type=='MESH' and ('tree' in o.name.lower() or 'lamp' in o.name.lower() or 'light' in o.name.lower()) and len(o.data.vertices)<2000000:
    mw=o.matrix_world; c=0
    for v in o.data.vertices:
      w=mw@v.co
      if abs(w.x+72)<3 and abs(w.y+52.5)<4: c+=1
    if c: print('MESHNEAR',o.name,c)
