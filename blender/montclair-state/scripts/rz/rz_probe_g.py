import bpy, json, numpy as np
from mathutils import Vector
fp=json.load(open('data/qr/day8_prep/student_center_footprints_local_qr.json'))['ways']['313026743']['pts_local_m']
P=np.array(fp); c=P[:-1].mean(0)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
out=[]
for i in range(len(P)-1):
    for t in (0,0.5):
        p=P[i]*(1-t)+P[i+1]*t; v=p-c; p=p+v/np.linalg.norm(v)*1.0
        h,loc,n,idx,ob,m=sc.ray_cast(dg,Vector((p[0],p[1],200)),Vector((0,0,-1)))
        out.append((round(p[0],1),round(p[1],1),round(loc.z,2) if h else None, ob.name[:30] if h else None))
for r in out: print('G',r)
