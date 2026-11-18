import bpy, numpy as np, json, re
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh
R='/workspace/nj-scenes/montclair-state'
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=ter.data; mw=ter.matrix_world
n=len(me.vertices); co=np.zeros(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
M=np.array(mw); co=co@M[:3,:3].T+M[:3,3]
ne=len(me.edges); ed=np.zeros(ne*2,dtype=np.int64); me.edges.foreach_get('vertices',ed); ed=ed.reshape(-1,2)
a,b=ed[:,0],ed[:,1]; L=np.linalg.norm(co[a,:2]-co[b,:2],axis=1)+1e-6; dz=np.abs(co[a,2]-co[b,2]); s=dz/L
print('terrain bbox',co.min(0),co.max(0),'verts',n)
# steep edges with significant drop (>0.6 m) — cliffs
st=(s>0.8)&(dz>0.6)
mid=(co[a[st]]+co[b[st]])/2
# cluster on 6 m grid
cells={}
for m,d in zip(mid,dz[st]):
    k=(int(m[0]//6),int(m[1]//6)); c=cells.setdefault(k,[0,0.0]); c[0]+=1; c[1]=max(c[1],d)
# building / landmark locations
marks={}
for o in bpy.data.objects:
    nm=o.name.lower()
    for key in ('cole','red hawk','redhawk','ccom','communication','morehead','life hall','partridge','kasser','annex','student center','university hall','dickson','sprague','calcia','russ','college hall','freeman'):
        if key in nm and o.type in('MESH','EMPTY'):
            bb=[o.matrix_world@Vector(c) for c in o.bound_box]; cx=sum(p.x for p in bb)/8; cy=sum(p.y for p in bb)/8
            marks.setdefault(key,[]).append((o.name,round(cx),round(cy)))
for k,v in marks.items(): print('MARK',k,v[:4])
# under buildings? skip cells covered by building footprints: use list
out=sorted([(k[0]*6+3,k[1]*6+3,c[0],round(c[1],2)) for k,c in cells.items()],key=lambda r:-r[3])
print('cliff cells',len(out))
json.dump({'cells':out,'marks':marks},open(R+'/data/ws29/scan.json','w'))
for r in out[:60]: print('CELL',r)
