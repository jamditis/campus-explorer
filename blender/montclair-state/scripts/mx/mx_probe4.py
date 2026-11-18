import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for z in (138.5,141,143,144.5,145.5):
    for t in (-1.0,-2.0,-4.04,-7.44,-9.0):
        hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,P(-18.1,t,z),-d)
        print("HRAY z %.1f t %.2f -> %s du %.2f"%(z,t,ob.name if hit else None,(-18.1-d.dot(loc)) if hit else 0))
