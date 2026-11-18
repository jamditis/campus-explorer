import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
from collections import Counter
hits=Counter(); zs={}
x=-236.0
while x<-226:
    y=-166.0
    while y<-150:
        o=Vector((x,y,160)); d=Vector((0,0,-1)); top=None
        for k in range(4):
            r,loc,n,i,ob,mw=sc.ray_cast(dg,o,d)
            if not r: break
            hits[(k,ob.name)]+=1; zs.setdefault(ob.name,[]).append(round(loc.z,2))
            o=loc+d*0.01
        y+=1.0
    x+=1.0
for (k,n),c in sorted(hits.items()): print('PROBE158',k,n,c,min(zs[n]),max(zs[n]))
