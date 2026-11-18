import bpy, math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
loc=Vector((-25.62,2.52,147.3)); tgt=Vector((-19.73,7.79,147.6)); f=35; W,H=768,432
fw=(tgt-loc).normalized(); r=fw.cross(Vector((0,0,1))).normalized(); up=r.cross(fw)
for px,py in ((325,290),(280,289),(370,288),(350,262),(300,265),(240,300)):
    x=(px/W-0.5)*36; y=(0.5-py/H)*36*H/W
    dr=(fw*f+r*x+up*y).normalized()
    h=sc.ray_cast(dg,loc,dr)
    print('HIT',px,py,h[0],h[4].name if h[0] else None,[round(c,3) for c in h[1]] if h[0] else None, h[3])
