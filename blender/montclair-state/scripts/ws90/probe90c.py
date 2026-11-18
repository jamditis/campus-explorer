import bpy,math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def gz(x,y):
    r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1))); return r[1].z if r[0] else 0
c=Vector((-214,-66.2,gz(-214,-66.2)+0.9)); t=Vector((-206,-73.5,gz(-206,-73.5)))
f=(t-c).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
k=math.tan(math.atan(18/30))
seen={}
for px in range(385,480,8):
  for py in range(90,115,4):
    d=(f+r*((px-352)/352*k)+u*((198-py)/352*k)).normalized()
    h=sc.ray_cast(dg,c,d)
    if h[0]: seen.setdefault(h[4].name,[]).append(tuple(round(v,1) for v in h[1]))
for n,v in seen.items(): print('P90C',n,len(v),v[:3])
