import bpy,sys,os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in ((10.32,-43.39),(9.0,-43.5),(7,-39),(2,-33),(12,-45)):
    z=170; out=[]
    for _ in range(12):
        h,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)))
        if not h: break
        if not ob.name.startswith('T_'): out.append('%s %.3f'%(ob.name[:28],loc.z))
        z=loc.z-0.01
        if len(out)>=3: break
    print('P224 (%.1f,%.1f) '%(x,y)+' | '.join(out))
sys.stdout.flush(); os._exit(0)
