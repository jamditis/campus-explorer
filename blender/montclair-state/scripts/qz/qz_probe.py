import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type=='MESH' and any(o.name.startswith(p) for p in ('QS','QW','QXP','QX_','OV')):
        mats=[s.material.name if s.material else None for s in o.material_slots]
        print('OBJ',o.name,len(o.data.polygons),mats,[c.name for c in o.users_collection])
sc=bpy.context.scene
for x in range(-75,-44,3):
  for y in range(268,292,3):
    hit,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
    if hit:
        mat=ob.material_slots[ob.data.polygons[i].material_index].material.name if ob.type=='MESH' and ob.material_slots and i<len(ob.data.polygons) else None
        print('RAY',x,y,round(loc.z,2),ob.name,mat,round(n.z,2))
for o in bpy.data.objects:
    if 'CAM' in o.name and o.name.startswith(('QY','QX')): print('CAM',o.name,tuple(round(v,1) for v in o.location))
