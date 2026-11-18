import bpy, math
from mathutils import Vector
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
t=O.get('CCOM newsroom grid DMX terminators (nd)')
if t:
    vs=[t.matrix_world@v.co for v in t.data.vertices]
    for k in range(3):
        g=vs[k*len(vs)//3:(k+1)*len(vs)//3]; c=sum(g,Vector())/len(g); print('TERMPOS',[round(x,2) for x in c])
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0))
for z in (139.0,141.0,143.0):
  for off in (-2,0,2):
    p=Vector((-18.45,-13.9,z))+Vector((-d.y,d.x,0))*off - d*0.3
    hit,loc,nor,idx,ob,m=sc.ray_cast(dg,p,-d,distance=200)
    print('RAY',z,off,hit and round((loc-p).length,2), ob.name if hit else None)
