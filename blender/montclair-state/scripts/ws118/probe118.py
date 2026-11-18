import bpy
from mathutils import Vector
xr=lambda y: -213.3+(min(y,-184.0)+196.65)*(2.3/12.65)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-196,-194,-192,-190,-188,-186,-184,-183):
    out=[]
    for d in (0.1,0.4,0.8,1.2,1.8,2.5):
        x=xr(y)-0.30-d; h=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
        out.append('%.1f %s:%.2f'%(d,h[4].name[:18],h[1].z) if h[0] else '-')
    print('PR118 y',y,' | '.join(out))
