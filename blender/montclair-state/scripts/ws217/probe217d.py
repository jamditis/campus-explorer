import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-47.4,-47.1,-46.9,-46.7,-46.5,-46.2,-45.8):
    row=[]
    for x in (-262.5,-261.0,-259.5,-258.0,-256.5,-255.8):
        r=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1)))
        row.append((x,r[4].name[:22] if r[0] else None,round(r[1].z,3) if r[0] else None))
    print('HIT y',y,row,flush=True)
raise SystemExit
