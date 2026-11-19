import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
import os
X0,X1,Y0,Y1,ST=[float(v) for v in os.environ.get('PG','-256,-244,-58,-49,1').split(',')]
y=Y1
while y>=Y0-1e-6:
    row=[]; x=X0
    while x<=X1+1e-6:
        r=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
        if r[0]:
            o=r[4]; mi=r[3]; ev=o.evaluated_get(dg); 
            try: mn=ev.data.polygons[mi].material_index; mat=ev.material_slots[mn].material.name if ev.material_slots and ev.material_slots[mn].material else '-'
            except Exception: mat='?'
            row.append('%.1f,%.1f %s@%.2f[%s]'%(x,y,o.name[:26],r[1].z,mat[:18]))
        x+=ST
    for c in row: print('HITE',c,flush=True)
    y-=ST
raise SystemExit
