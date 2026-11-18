import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam_o=Vector((-13.6,105.5,143.0)); tgt=Vector((-15.7,117.1,146.8))
R=(tgt-cam_o).normalized().to_track_quat('-Z','Y').to_matrix(); fw=36/35/2
for px,py in [(160,100),(150,150),(170,70),(145,175),(180,120)]:
    u=(px/640-0.5)*2*fw; v=-(py/360-0.5)*2*fw*360/640
    d=(R@Vector((u,v,-1))).normalized()
    hit,loc,nor,idx,ob,mx=sc.ray_cast(dg,cam_o,d)
    print('R',px,py,ob.name if ob else None,idx,tuple(round(c,2) for c in loc),tuple(round(c,2) for c in nor), ob.parent.name if ob and ob.parent else '')
