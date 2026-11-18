import bpy, math, collections
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
for nm in ['Downspouts (3f)','Gutters half-round (3f, Life/CCOM UNVERIFIED)']:
    o=bpy.data.objects[nm]; M=o.matrix_world; cl=collections.Counter(); zr={}
    for f in o.data.polygons:
        p=M@f.center; u=d.dot(p); t=n.dot(p)-C0-T0
        if u>-18.05 and -14.5<t<-0.02 and 136<p.z<148.2:
            k=(round(u),round(t,1)); cl[k]+=1; zr.setdefault(k,[999,0]); zr[k][0]=min(zr[k][0],p.z); zr[k][1]=max(zr[k][1],p.z)
    for k,v in sorted(cl.items()): print("CL",nm[:10],k,v,[round(x,2) for x in zr[k]])
