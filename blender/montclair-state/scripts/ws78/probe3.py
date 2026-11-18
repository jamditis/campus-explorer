import bpy
from mathutils import Vector
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
# bbox-intersection list without loading meshes heavily: load all objects? too heavy -> link library (linked data is lighter) 
with bpy.data.libraries.load(src,link=True) as (fr,to): to.objects=list(fr.objects)
n=0
for o in to.objects:
    if not o or o.type not in ('MESH','CURVE','EMPTY'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb)
    if x1>-249 and x0<-200 and y1>-140 and y0<-84 and (x1-x0)<400:
        print('WS78B',o.name,o.type,round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(min(p.z for p in bb),2),'hid',o.hide_render,[m.type for m in getattr(o,'modifiers',[])][:4],flush=True)
