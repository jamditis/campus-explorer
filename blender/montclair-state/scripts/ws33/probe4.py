import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
from collections import Counter
cnt=Counter(); ex={}
y=-50.0
while y<-25:
    x=-8.0
    while x<0:
        ok,loc,nor,idx,ob,mat=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
        if ok:
            n=ob.name
            cnt[n]+=1; ex.setdefault(n,[]).append((round(x,1),round(y,1),round(loc.z,2)))
        x+=0.5
    y+=0.5
for n,c in cnt.most_common(): print('TOP',n,c,ex[n][:5])
