import bpy, collections
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cnt=collections.Counter(); ex={}
for xi in range(-205,-140,1):
  for yi in range(-22,-4,1):
    ok,loc,n,fi,ob,_=sc.ray_cast(dg,Vector((xi+0.5,yi+0.5,200)),Vector((0,0,-1)))
    if ok and ob.type=='MESH':
      m=ob.data.polygons[fi].material_index if fi<len(ob.data.polygons) else 0
      mn=ob.material_slots[m].material.name if ob.material_slots and ob.material_slots[m].material else '-'
      key=(ob.name,mn); cnt[key]+=1; ex.setdefault(key,[]).append((xi,yi,round(loc.z,2)))
for k,v in cnt.most_common(30): print('HIT',k,v,ex[k][:4])
