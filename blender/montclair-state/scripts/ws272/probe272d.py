import bpy, os, sys
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(b.x for b in bb);x1=max(b.x for b in bb);y0=min(b.y for b in bb);y1=max(b.y for b in bb)
    if x1-x0>200: continue
    if x1>-285 and x0<-240 and y1>-150 and y0<-120:
        print('P272D',o.name[:80],[round(v,1) for v in (x0,x1,y0,y1,min(b.z for b in bb),max(b.z for b in bb))],flush=True)
sys.stdout.flush(); os._exit(0)
