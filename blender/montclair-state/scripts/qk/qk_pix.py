import bpy, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects[os.environ['PCAM']]; fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl
M=cam.matrix_world; o=M.translation
for s in os.environ['PIX'].split(';'):
    u,v=map(float,s.split(','))  # u from left, v from top, 0..1
    tl,tr,bl=fr[3],fr[0],fr[2]
    p=tl+(tr-tl)*u+(bl-tl)*v; d=(M.to_3x3()@p).normalized()
    hit,loc,nor,idx,ob,_=sc.ray_cast(dg,o,d)
    print('PIX',s,hit,ob.name if ob else None,tuple(round(c,2) for c in loc),tuple(round(c,2) for c in nor))
