import bpy,math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def ray(o,d):
    r=sc.ray_cast(dg,o,d.normalized()); return (r[4].name if r[0] else None, tuple(round(c,2) for c in r[1]) if r[0] else None)
gz=sc.ray_cast(dg,Vector((-266,-56,300)),Vector((0,0,-1)))
cam=Vector((-266,-56,gz[1].z+1.7)); print('P69 cam',tuple(cam),gz[4].name)
tgt=Vector((-214,-66,cam.z)); f=(tgt-cam).normalized(); r=f.cross(Vector((0,0,1))).normalized()
seen={}
for ah in range(-14,15):
  for av in range(-12,1):
    d=f*math.cos(math.radians(ah))+r*math.sin(math.radians(ah)); d.z=math.tan(math.radians(av*0.8))
    n,p=ray(cam,d)
    if n: seen.setdefault(n,[]).append((ah,av,p))
for n,l in sorted(seen.items(),key=lambda x:-len(x[1])): print('P69',n,len(l),l[:3])
