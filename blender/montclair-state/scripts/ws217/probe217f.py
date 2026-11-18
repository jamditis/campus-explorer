import bpy, os
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in [(-253.375,-46.125),(-252.875,-45.625),(-252.125,-45.125),(-251.625,-46.375),(-253.5,-46.0)]:
    r=sc.ray_cast(dg,Vector((x,y,160)),Vector((0,0,-1)))
    r2=sc.ray_cast(dg,Vector((x,y,130)),Vector((0,0,-1)))
    print('HITF',x,y,r[4].name[:30] if r[0] else None,round(r[1].z,2),'| from130',r2[4].name[:30] if r2[0] else None,round(r2[1].z,2),flush=True)
raise SystemExit
