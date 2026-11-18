import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(-20,113),(-21,114.5),(-19,114.8),(-20,115.8),(-18.5,115.3)]:
    o=Vector((x,y,160)); hits=[]
    for k in range(4):
        h,l,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        hits.append((ob.name[:30],round(l.z,2))); o=l-Vector((0,0,0.01))
    print('DOWN',x,y,hits)
w=bpy.data.objects['Schmitt Hall walls']; print('MATS',[s.material.name if s.material else None for s in w.material_slots])
