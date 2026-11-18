import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0))
w=bpy.data.objects['School of Communication and Media walls']; M=w.matrix_world
us=set(); ts=[]
for v in w.data.vertices:
    p=M@v.co; t=n.dot(p)-20.36; u=d.dot(p)
    if -21<u<5 and -1.5<t<0.8 and 134<p.z<148: us.add((round(u,3),round(t,3)))
for x in sorted(us): print("UT",x)
for nm in ['CCOM_win_082_r0','CCOM_win_084_r0','CCOM_win_086_r0','CCOM_win_088_r0','CCOM_win_090_r0','CCOM_win_090_r0']:
    o=bpy.data.objects[nm]; p=o.matrix_world.translation; print("WIN",nm,round(d.dot(p),3),round(n.dot(p)-20.36,3),o.instance_collection.name, [ (c.name) for c in o.instance_collection.all_objects][:6])
    for c in o.instance_collection.all_objects:
        bb=[Vector(x) for x in c.bound_box]; print("  ",c.name,[round(min(b[i] for b in bb),2) for i in range(3)],[round(max(b[i] for b in bb),2) for i in range(3)], [s.material.name for s in c.material_slots if s.material])
    break
for nm in ['CCOM atrium glass (arched, 7x10 grid)','CCOM atrium mullion v0']:
    o=bpy.data.objects[nm]; print("MAT",nm,[s.material.name for s in o.material_slots])
print("ENG",bpy.context.scene.render.engine)
