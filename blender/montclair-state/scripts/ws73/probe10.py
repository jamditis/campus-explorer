import bpy
from mathutils import Vector
from collections import Counter
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; V=o.data.vertices
cnt=Counter(); ex=[]
for r in range(len(V)//6-1):
    a=V[6*r+0].co; b=V[6*r+6].co; a1=V[6*r+4].co
    if not (-222<a.x<-200 and a.y>-95): continue
    d=(a-a1); d.z=0; d.normalize()
    for u in (0,0.2,0.4,0.6,0.8):
        p0=a.lerp(b,u)
        for s in (0.02,0.1,0.2,0.3,0.45,0.6,0.8):
            p=p0+d*s; rr=sc.ray_cast(dg,Vector((p.x,p.y,400)),Vector((0,0,-1)))
            n=rr[4].name[:14] if rr[0] else None; cnt[n]+=1
            if n and not n.startswith(('WS27_CollegeAve_c',)) and len(ex)<30: ex.append((round(p.x,2),round(p.y,2),s,n,round(rr[1].z-p0.z,2)))
print('P9',cnt); print('P9 ex',ex)
