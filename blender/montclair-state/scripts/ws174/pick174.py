import bpy, math, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def gz(x,y):
    h=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
    return (h[1].z,h[4].name) if h[0] else (115,None)
C=eval(os.environ['C']); TG=eval(os.environ['TG']); L=float(os.environ['L'])
c=Vector((C[0],C[1],0)); z,n=gz(c.x,c.y); print('UNDERCAM',n,round(z,2)); c.z=z+C[2]
tg=Vector((TG[0],TG[1],0)); tg.z=gz(tg.x,tg.y)[0]+TG[2]
fwd=(tg-c).normalized(); right=fwd.cross(Vector((0,0,1))).normalized(); up=right.cross(fwd)
W,H=768,432; f=L/36*W
for px,py in eval(os.environ['PX']):
    d=(fwd*f+right*(px-W/2)+up*(H/2-py)).normalized()
    h=sc.ray_cast(dg,c,d)
    print('PICK',px,py,h[4].name if h[0] else None,tuple(round(v,2) for v in h[1]) if h[0] else '',flush=True)
