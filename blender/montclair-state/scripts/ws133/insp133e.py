import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in [(-128,-276),(-120,-280),(-112,-270),(-110,-262),(-136,-272),(-140,-268),(-114,-255),(-125,-266),(-100,-280)]:
    r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
    print('HIT %.0f %.0f'%(x,y), r[0], r[4].name if r[4] else None, '%.2f'%r[1].z if r[0] else '')
