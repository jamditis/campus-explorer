import bpy
from mathutils import Vector
for n in ('T_PinOak_L1_0277','T_PinOak_L1_0274'):
  o=bpy.data.objects[n]
  print('T',n,o.type,o.data.name if o.data else None, o.data.users if o.data else None,[round(v,2) for v in o.location],[round(v,2) for v in o.scale],[m.type for m in o.modifiers], o.instance_type, o.instance_collection.name if o.instance_collection else None)
  if o.type=='MESH':
    mw=o.matrix_world; zs=[(mw@v.co).z for v in o.data.vertices]
    print('  zmin',round(min(zs),2),'zmax',round(max(zs),2),'nv',len(zs),[m.name for m in o.data.materials])
    low=[mw@v.co for v in o.data.vertices if (mw@v.co).z<o.location.z+2.3 and abs((mw@v.co).y+55)<2.2]
    print('  low over walk',len(low))
