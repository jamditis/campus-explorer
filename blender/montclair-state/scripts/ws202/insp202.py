import bpy, numpy as np, os
from mathutils import Vector
P=[(-305.3,-251.0),(-304.4,-235.8)]; out={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if not o.name.startswith(('WS165','WS170','WS191','WS193','WS194')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if not any(min(xs)-3<x<max(xs)+3 and min(ys)-3<y<max(ys)+3 for x,y in P): continue
    mw=o.matrix_world; V=np.array([tuple(mw@v.co) for v in o.data.vertices]); out[o.name]=V
    print('F202 OBJ',o.name,len(V),[m.type for m in o.modifiers],flush=True)
np.savez(os.environ['OUT'],**out)
