import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x,y in [(-208,-100),(-205,-98),(-203,-96),(-210,-104),(-201,-102),(-206,-92)]:
    o=Vector((x,y,300)); hits=[]
    for i in range(6):
        ok,loc,nrm,idx,ob,_=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not ok: break
        hits.append((ob.name,round(loc.z,3))); o=loc-Vector((0,0,0.001))
    print((x,y),hits)
