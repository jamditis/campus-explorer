import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
out=Vector((0.92,-0.4,0)).normalized(); c=Vector((10.6,141.1,0))
for z in (138.9,139.1,139.3,139.5,140.0):
    for off in (-0.6,0,0.6):
        al=Vector((-out.y,out.x,0))
        o=c+out*4+al*off; o.z=z
        h=sc.ray_cast(dg,o,-out)
        print('R',z,off,h[0], h[4].name if h[4] else None, round((h[1]-o).length,2) if h[0] else None)
