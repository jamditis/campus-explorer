import bpy, os
from mathutils import Vector
# W38 probe: top object per 0.25 m cell around the walk E end / WS72 Kasser landing / stair door (terrain GN on in subset runs)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in [-48.0+0.25*i for i in range(15)]:
    row=[]
    for x in [-257.0+0.5*j for j in range(11)]:
        r=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1)))
        row.append((r[4].name[:6] if r[0] else '-')+'@'+(str(round(r[1].z,2)) if r[0] else ''))
    print('HITE y',round(y,2),' '.join(row),flush=True)
if os.environ.get('PROBE_EXIT')=='1': raise SystemExit
