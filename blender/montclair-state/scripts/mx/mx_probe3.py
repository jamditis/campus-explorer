import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for u in (-18.1,-18.3,-18.8,-19.5,-21):
    for t in (-0.5,-1.5,-2.99,-4.04,-5.09,-6.39,-7.44,-8.49,-9.3,-11):
        hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,P(u,t,170),Vector((0,0,-1)))
        print("RAY u %.1f t %.2f -> %s %.2f"%(u,t,ob.name if hit else None,loc.z if hit else 0))
