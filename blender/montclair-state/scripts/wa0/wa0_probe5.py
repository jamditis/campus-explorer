import bpy
from collections import defaultdict
from mathutils import Vector
O=bpy.data.objects
X0,X1,Y0,Y1=108,117,278,285
WU=O['WU_richardson_reid_LiDAR_patch_UNVERIFIED']; mw=WU.matrix_world; vs=[mw@v.co for v in WU.data.vertices]
ec=defaultdict(int)
for p in WU.data.polygons:
    L=list(p.vertices)
    for a,b in zip(L,L[1:]+L[:1]): ec[(min(a,b),max(a,b))]+=1
oe=[(a,b) for (a,b),c in ec.items() if c==1 and X0<=vs[a].x<=X1 and Y0<=vs[a].y<=Y1]
print('WU open edges in box',len(oe))
for a,b in sorted(oe,key=lambda e:(vs[e[0]].y,vs[e[0]].x)):
    print(' E',tuple(round(c,3) for c in vs[a]),tuple(round(c,3) for c in vs[b]))
print('WU verts in box',sum(1 for v in vs if X0<=v.x<=X1 and Y0<=v.y<=Y1), 'mat',[m.name for m in WU.data.materials])
for o in O:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[c.x for c in bb]; ys=[c.y for c in bb]; zs=[c.z for c in bb]
    if max(xs)<X0+2 or min(xs)>X1-2 or max(ys)<Y0+1 or min(ys)>Y1-1: continue
    if (max(xs)-min(xs))>300: continue
    if 'grass' in o.name.lower() and 'clump' in o.name: continue
    print('OBJ',o.name,[round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(zs),2),round(max(zs),2)],len(o.data.polygons))
