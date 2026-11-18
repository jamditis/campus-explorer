import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import Counter
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def mesh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]; e.to_mesh_clear(); return V,P
def bnd(V,P):
    ec=Counter()
    for p in P:
        for i in range(len(p)): ec[tuple(sorted((p[i],p[(i+1)%len(p)])))]+=1
    return sorted({i for e,c in ec.items() if c==1 for i in e})
WT='WT_richardson_west_LiDAR_patch_UNVERIFIED'; WF='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'; RZ=[n for n in O.keys() if n.startswith('RZ2_')][0]
M={n:mesh(O[n]) for n in (WT,WF,RZ)}; B={n:BVHTree.FromPolygons(*M[n]) for n in M}
def z(n,x,y):
    h=B[n].ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] else None
for a,b,cond in ((WT,WF,lambda v:v.y>319.5 and 50<v.x<80),(WF,WT,lambda v:v.y<319 and 50<v.x<80),(RZ,WT,lambda v:300<v.y<325 and 45<v.x<60),(RZ,WF,lambda v:318<v.y<330 and 45<v.x<60)):
    V,P=M[a]; out=[]
    for i in bnd(V,P):
        v=V[i]
        if not cond(v): continue
        o=z(b,v.x,v.y)
        if o is None: continue
        out.append((round(v.x,1),round(v.y,1),round(v.z-o,3)))
    out.sort()
    print(a[:2],'edge over',b[:2],len(out),'exposed(>+0.5cm)',[t for t in out if t[2]>0.005])
