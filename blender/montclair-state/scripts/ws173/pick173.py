import bpy, math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def gz(x,y):
    h=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
    return h[1].z if h[0] else 115
c=Vector((-316.5,-258.3,0)); c.z=gz(c.x,c.y)+1.6
tg=Vector((-325.9,-263.3,0)); tg.z=gz(tg.x,tg.y)+0.2
fwd=(tg-c).normalized(); right=fwd.cross(Vector((0,0,1))).normalized(); up=right.cross(fwd)
W,H=768,432; f=30/36*W
for px,py in [(525,195),(410,245),(300,215),(600,200)]:
    d=(fwd*f+right*(px-W/2)+up*(H/2-py)).normalized()
    h=sc.ray_cast(dg,c,d)
    print('PICK',px,py,h[4].name if h[0] else None,tuple(round(v,2) for v in h[1]) if h[0] else '',flush=True)
