import bpy,numpy as np,pickle
from mathutils import Vector
x0,x1,y0,y1=-285,-225,-265,-225
out={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: continue
    if len(o.data.polygons)>400000: continue
    mw=o.matrix_world; V=np.array([tuple(mw@v.co) for v in o.data.vertices]) if len(o.data.vertices)<300000 else None
    if V is None: continue
    P=[]
    for f in o.data.polygons:
        vs=list(f.vertices); c=V[vs].mean(0)
        if x0<c[0]<x1 and y0<c[1]<y1 and f.normal.z>0.3: P.append((V[vs].tolist(),f.material_index))
    if P: out[o.name]=(P,[m.name for m in o.material_slots]); print('P112',o.name,len(P),round(min(p[0][0][2] for p in P),2),round(max(p[0][0][2] for p in P),2))
pickle.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws112/probe112.pkl','wb'))
