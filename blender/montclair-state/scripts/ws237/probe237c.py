# read-only CHAIN: all surfaces (evaluated) stacked at given XY points (vertical ray, repeated)
import bpy, mathutils, os
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for p in os.environ['PXY'].split():
    x,y=map(float,p.split(':')); z=400.0; out=[]
    for i in range(8):
        h=sc.ray_cast(dg,mathutils.Vector((x,y,z)),mathutils.Vector((0,0,-1)))
        if not h[0]: break
        out.append('%s@%.2f'%(h[4].name[:22],h[1].z)); z=h[1].z-0.005
    print('P237C',x,y,' | '.join(out),flush=True)
os._exit(0)
