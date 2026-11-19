import bpy, sys, os
from mathutils import Vector
c=Vector((172.0,5.0,102.4)); tg=Vector((197.0,50.0,100.8))
f=(tg-c).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
dg=bpy.context.evaluated_depsgraph_get()
for px,py in [(400,165),(250,140),(600,195),(120,125)]:
    x=(px/704-0.5)*36/30; y=(0.5-py/396)*(36*396/704)/30
    d=(f+r*x+u*y).normalized()
    hit=bpy.context.scene.ray_cast(dg,c,d)
    print('P226M',px,py,hit[0],tuple(round(v,1) for v in hit[1]) if hit[0] else None,hit[4].name if hit[0] else None,flush=True)
sys.stdout.flush(); os._exit(0)
