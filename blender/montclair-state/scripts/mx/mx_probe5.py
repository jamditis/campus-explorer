import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
skip={'MS_CCOM_newsroom_studio_20261029mw','MS_CCOM_newsroom_studio_detail_20261030mx','MX_protos_hidden'}
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or any(c.name in skip for c in o.users_collection): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.z for p in bb)<137.5 or min(p.z for p in bb)>146.3: continue
    if max(d.dot(p) for p in bb)<-17.95 or min(d.dot(p) for p in bb)>1.7: continue
    if max(n.dot(p)-C0-T0 for p in bb)<-14.2 or min(n.dot(p)-C0-T0 for p in bb)>-0.4: continue
    oe=o.evaluated_get(dg); me=oe.to_mesh(); M=o.matrix_world; k=0
    for v in me.vertices:
        p=M@v.co; u=d.dot(p); t=n.dot(p)-C0-T0
        if -17.95<u<1.7 and -14.2<t<-0.4 and 137.5<p.z<146.3: k+=1
    oe.to_mesh_clear()
    if k: print("INTR",o.name,k,len(o.data.polygons),[c.name for c in o.users_collection])
