# ws183 read-only: which objects/material slots draw the faceted grey triangles S of the Lot 36 SE corner (eye from lot W)
import bpy, numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; cnt={}
for y in np.arange(-238,-232,0.25):
    for x in np.arange(-318,-306,0.25):
        hit,loc,n,i,o,m=sc.ray_cast(dg,Vector((x,y,140)),Vector((0,0,-1)))
        if not hit: continue
        oe=o.evaluated_get(dg); me=oe.data
        try: mat=me.materials[me.polygons[i].material_index].name if me.materials else '-'
        except Exception: mat='?'
        k=(o.name[:40],mat[:30],round(n.z,2)<0.995); cnt[k]=cnt.get(k,0)+1
for k,v in sorted(cnt.items(),key=lambda kv:-kv[1]): print('P183C',v,k,flush=True)
