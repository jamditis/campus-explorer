import bpy,os
from mathutils import Vector
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws72/lite_load.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws81/probe81a.py').read())
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
from collections import Counter
cnt=Counter(); samples={}
x=-234.0
while x<=-224:
    y=-130.0
    while y<=-110:
        ok,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        if ok:
            mat=None
            try: mat=ob.material_slots[ob.data.polygons[i].material_index].material.name
            except Exception: pass
            k=(ob.name,mat); cnt[k]+=1; samples.setdefault(k,[]).append((round(x,1),round(y,1),round(loc.z,2)))
        y+=0.25
    x+=0.25
for k,v in cnt.most_common(): print('TOPHIT',v,k,samples[k][:4],flush=True)
