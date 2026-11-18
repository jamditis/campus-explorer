import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; V=o.data.vertices
for r in range(len(V)//6):
    v=[V[6*r+k].co for k in range(6)]
    if not (-226<v[0].x<-196 and v[0].y>-95) or r%2: continue
    d=(v[4]-v[1]); d.z=0; d.normalize(); out=[]
    for s in (0.02,0.06,0.1,0.15,0.2,0.3,0.45,0.6):
        p=v[4]+d*s; rr=sc.ray_cast(dg,Vector((p.x,p.y,400)),Vector((0,0,-1)))
        out.append((s,rr[4].name[:12] if rr[0] else None,round(rr[1].z-v[4].z,2) if rr[0] else None))
    print('P8',round(v[4].x,1),round(v[4].y,2),'v5',round(v[5].x,2),round(v[5].y,2),round(v[5].z-v[4].z,2),out)
