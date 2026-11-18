import bpy
from mathutils import Vector
from collections import Counter
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; V=o.data.vertices; rows=len(V)//6
bad=Counter(); ex=[]
for r in range(rows-1):
    a=[V[6*r+k].co for k in range(6)]; b=[V[6*r+6+k].co for k in range(6)]
    if not (-215<a[0].x<-190 and a[0].y>-95): continue
    for u in (0,0.25,0.5,0.75):
        for t in [i/10 for i in range(1,11)]+[1.1,1.25]:
            p=(a[1].lerp(b[1],u)).lerp(a[4].lerp(b[4],u),t)
            rr=sc.ray_cast(dg,Vector((p.x,p.y,400)),Vector((0,0,-1)))
            if rr[0] and rr[4].name!=o.name:
                bad[(rr[4].name[:40],t>1)]+=1
                if len(ex)<25: ex.append((round(p.x,2),round(p.y,2),round(t,2),rr[4].name[:25],round(rr[1].z-p.z,3)))
print('P5',bad); print('P5 ex',ex)
