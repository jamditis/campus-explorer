import bpy
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.z for v in bb)<146.4 or min(v.z for v in bb)>148.6: continue
    if max(v.dot(n) for v in bb)<21.0 or min(v.dot(n) for v in bb)>23.5: continue
    if min(v.dot(t) for v in bb)>3.3 or max(v.dot(t) for v in bb)<2.36: continue
    mw=o.matrix_world; c=0; zs=[]; us=[]
    for p in o.data.polygons:
        q=mw@p.center
        if 2.37<q.dot(t)<3.19 and 21.0<q.dot(n)<23.4 and 146.4<q.z<148.6: c+=1; zs.append(q.z); us.append(q.dot(t))
    if c: print('IN',repr(o.name),c,'z',round(min(zs),3),round(max(zs),3),'u',round(min(us),3),round(max(us),3),o.users_collection[0].name)
