import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for x,y in [(-170,-15),(-185,-12),(-160,-12),(-175,-20),(-200,10),(-205,0),(-150,0),(-145,20),(-195,30)]:
    ok,loc,n,fi,ob,_=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
    if ok:
        oo=ob.original; mi=oo.data.polygons[fi].material_index if hasattr(oo.data,'polygons') and fi<len(oo.data.polygons) else 0
        print('NP',x,y,oo.name,round(loc.z,2),oo.material_slots[mi].material.name if oo.material_slots else '-')
