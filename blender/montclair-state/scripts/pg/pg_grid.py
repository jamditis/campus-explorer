import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in range(166,184,1):
    row=[]
    for x in range(-222,-194,1):
        hit,loc,n,i,o,m=sc.ray_cast(dg,Vector((x+0.5,y+0.5,200)),Vector((0,0,-1)))
        row.append(f"{loc.z:5.1f}{(o.name[:2] if hit else '--')}" if hit else '  -  ')
    print('G',y,' '.join(row))
