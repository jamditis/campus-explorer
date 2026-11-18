import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36
w=bpy.data.objects['School of Communication and Media walls']; M=w.matrix_world
fs=[]
for f in w.data.polygons:
    ps=[M@w.data.vertices[i].co for i in f.vertices]
    us=[d.dot(p) for p in ps]; ts=[n.dot(p)-C0 for p in ps]; zs=[p.z for p in ps]
    if max(abs(u+18.04) for u in us)<0.05 and min(ts)>-16 :
        fs.append((round(min(ts),2),round(max(ts),2),round(min(zs),2),round(max(zs),2)))
for x in sorted(fs): print("SF",x)
print("NSF",len(fs))
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render and o.name!=w.name:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        us=[d.dot(p) for p in bb]; ts=[n.dot(p)-C0 for p in bb]; zs=[p.z for p in bb]
        if min(us)<-18.0 and max(us)>-18.6 and max(ts)>-10 and min(ts)<-1 and max(zs)>140 and min(zs)<147 and (max(us)-min(us))<30:
            print("NEAR",o.name,"u %.2f..%.2f t %.2f..%.2f z %.2f..%.2f"%(min(us),max(us),min(ts),max(ts),min(zs),max(zs)))
inst=bpy.data.objects['CCOM_win_078_r0'].instance_collection
for o in inst.all_objects:
    bb=[Vector(c) for c in o.bound_box]; print("INST",o.name,[round(min(p[i] for p in bb),2) for i in range(3)],[round(max(p[i] for p in bb),2) for i in range(3)])
