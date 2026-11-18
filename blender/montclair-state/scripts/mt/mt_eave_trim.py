# Session mt: remove the main-roof eave strip that ran across the face of the new entrance gable (photos show the white gable continuous from arch to apex).
import bpy, bmesh
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
U0,U1=3.197,10.397
skip=('CCOM entrance','CCOM tower','CCOM atrium')
tot=0
for o in list(bpy.data.objects):
    if o.type!='MESH' or o.name.startswith(skip) or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.z for v in bb)<146.5 or min(v.z for v in bb)>149: continue
    if max(v.dot(n) for v in bb)<21.6 or min(v.dot(t) for v in bb)>U1 or max(v.dot(t) for v in bb)<U0: continue
    if o.data.users>1: continue
    mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data)
    kill=[]
    for f in bm.faces:
        c=mw@f.calc_center_median()
        u=c.dot(t); w=c.dot(n)
        if U0+0.02<u<U1-0.02 and 21.75<w<23.7 and 145.8<c.z<148.7: kill.append(f)
    if kill:
        print('TRIM',o.name,len(kill),'of',len(bm.faces)); tot+=len(kill)
        bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); o.data.update()
    bm.free()
print('TOTAL',tot,'COUNT',len(bpy.data.objects))
bpy.ops.wm.save_mainfile(); print('SAVED')
