import bpy, os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
c=Vector((-203.0,159.5,135.7))
for z in (136.5,137.5,138.5,140.5):
    t=Vector((-183.8,161.6,z)); d=(t-c); L=d.length; d.normalize()
    r=sc.ray_cast(dg,c,d,distance=L+2)
    print('R252 z',z,'dist %.2f'%L,'hit',r[0],r[4].name if r[0] else None,tuple(round(a,2) for a in r[1]) if r[0] else None,flush=True)
os._exit(0)
