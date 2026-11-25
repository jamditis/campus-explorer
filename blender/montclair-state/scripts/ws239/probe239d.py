# ws239 read-only: main objects whose world bbox intersects the RHD SE entrance box (x -276..-248, y -50..-36, z 123..132)
import bpy, os
from mathutils import Vector
B=(-276,-248,-50,-36,123,132)
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','EMPTY') : continue
    if o.type=='EMPTY' and not o.instance_collection: continue
    cs=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(c.x for c in cs);x1=max(c.x for c in cs);y0=min(c.y for c in cs);y1=max(c.y for c in cs);z0=min(c.z for c in cs);z1=max(c.z for c in cs)
    if x1<B[0] or x0>B[1] or y1<B[2] or y0>B[3] or z1<B[4] or z0>B[5]: continue
    if (x1-x0)*(y1-y0)>20000: continue
    print('P239D',o.name[:60],o.type,'hr',o.hide_render,[round(v,1) for v in (x0,x1,y0,y1,z0,z1)],[c.name for c in o.users_collection][:1],flush=True)
os._exit(0)
