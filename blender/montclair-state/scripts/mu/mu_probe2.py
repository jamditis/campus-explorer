# Session mu: dump boundary-edge midpoints near the gable band (to diff mt vs pre-mt)
import bpy, bmesh, sys, json
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
U0,U1=3.197,10.397
out={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if o.name.startswith('CCOM entrance'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.z for v in bb)<145.5 or min(v.z for v in bb)>149.5: continue
    if max(v.dot(n) for v in bb)<21.0 or min(v.dot(n) for v in bb)>24.5: continue
    if min(v.dot(t) for v in bb)>U1+2 or max(v.dot(t) for v in bb)<U0-2: continue
    mw=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); L=[]
    for e in bm.edges:
        if not e.is_boundary: continue
        a=mw@e.verts[0].co; b=mw@e.verts[1].co; m=(a+b)/2
        if U0-2<m.dot(t)<U1+2 and 21.0<m.dot(n)<24.5 and 145.5<m.z<149.2:
            L.append([round(a.dot(t),3),round(a.dot(n),3),round(a.z,3),round(b.dot(t),3),round(b.dot(n),3),round(b.z,3)])
    bm.free()
    if L: out[o.name]={'e':L,'mats':[m.name if m else None for m in o.data.materials]}
json.dump(out,open(sys.argv[-1],'w'))
