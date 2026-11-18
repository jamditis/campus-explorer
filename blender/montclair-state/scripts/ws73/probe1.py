import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
print('P names',sorted(o.name for o in sc.objects if any(k in o.name.lower() for k in ('curb','gutter','road','college','sidewalk','walk','berm','grass','lawn')))[:80])
for x in (-245,-235,-225,-215,-207,-203,-200,-197):
    prev=None; segs=[]
    y=-85.0
    while y<-45:
        r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        n=r[4].name if r[0] else None; z=round(r[1].z,2) if r[0] else None
        if n!=prev: segs.append((round(y,2),n,z)); prev=n
        y+=0.1
    print('P x',x,segs,flush=True)
