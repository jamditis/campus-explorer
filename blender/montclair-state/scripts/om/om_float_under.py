# om: what lies under the floating walk cells (scene ray down from 5 cm under the slab), read-only
import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
fp=bpy.data.objects['Footpaths_OSM']
pts=[(44.0,190.1),(28.0,186.6),(3.6,196.1),(62.0,211.2),(43.9,172.0),(36.2,149.9),(38.0,145.0),(51.3,140.9),(-4.0,212.0)]
for x,y in pts:
    h,l,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    top=(ob.name,round(l.z,2)) if h else None
    hits=[]; o=Vector((x,y,400))
    for k in range(6):
        h,l,n,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        hits.append((ob.name[:34],round(l.z,2))); o=l-Vector((0,0,0.01))
    print('UNDER',(x,y),hits)
