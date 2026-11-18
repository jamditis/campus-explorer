import bpy, collections
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cnt=collections.Counter(); ex={}
x=-236.0
while x<=-222:
    y=-234.0
    while y<=-218:
        hit,loc,nor,idx,ho,mt=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        if hit:
            n=ho.name; cnt[n]+=1; ex.setdefault(n,[]).append((round(x,1),round(y,1),round(loc.z,2)))
        y+=0.25
    x+=0.25
for n,c in cnt.most_common(): print('HIT',n,c,ex[n][:4])
