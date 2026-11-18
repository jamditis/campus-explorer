"""wc stitch: for x<66 WT ends at y=320.0 and WF starts at y=320.0 (abutting, no overlap). The wc raise lifted them by
different amounts there -> vertical slit visible as black crack lines in grazing views. Raise-only stitch: each edge vert
on that seam goes to max(own z, other sheet's edge z at same x)."""
import bpy,numpy as np,sys
from mathutils import Vector
from collections import Counter
O=bpy.data.objects
WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; WF=O['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
def edge(o,y0,y1,x0,x1):
    ec=Counter()
    for p in o.data.polygons:
        vs=list(p.vertices)
        for i in range(len(vs)): ec[tuple(sorted((vs[i],vs[(i+1)%len(vs)])))]+=1
    b={i for e,c in ec.items() if c==1 for i in e}; mw=o.matrix_world; out=[]
    for i in b:
        c=mw@o.data.vertices[i].co
        if y0<=c.y<=y1 and x0<=c.x<=x1: out.append((c.x,c.y,c.z,i))
    return sorted(out)
A=edge(WT,319.8,320.1,55.5,65.5); B=edge(WF,319.9,320.2,55.5,65.5)
print('WT edge',[(round(a[0],2),round(a[1],2),round(a[2],3)) for a in A])
print('WF edge',[(round(a[0],2),round(a[1],2),round(a[2],3)) for a in B])
def zat(E,x):
    xs=[e[0] for e in E]; zs=[e[2] for e in E]; return float(np.interp(x,xs,zs)) if xs else None
k=0; mx=0
newA=[(a[3],max(a[2],zat(B,a[0]))) for a in A]; newB=[(b[3],max(b[2],zat(A,b[0]))) for b in B]
for o,new,E in ((WT,newA,A),(WF,newB,B)):
    mi=o.matrix_world.inverted(); mw=o.matrix_world
    for (i,z),e in zip(new,E):
        if z>e[2]+1e-4:
            c=mw@o.data.vertices[i].co; mx=max(mx,z-c.z); c.z=z; o.data.vertices[i].co=mi@c; k+=1
    o.data.update()
print('STITCH',k,round(mx,3))
A2=edge(WT,319.8,320.1,55.5,65.5); B2=edge(WF,319.9,320.2,55.5,65.5)
print('resid',max(abs(a[2]-zat(B2,a[0])) for a in A2), max(abs(b[2]-zat(A2,b[0])) for b in B2))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
