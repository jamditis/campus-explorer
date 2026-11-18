# ws183 read-only: per-object z stack (BVH) at 0.1 m around the Lot 36 SE corner / bank toe (after fix181+fix182)
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1,ST=[float(v) for v in os.environ.get('PWIN','-322,-313,-234,-226,0.1').split(',')]
T={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    oe=o.evaluated_get(dg)
    try: me=oe.to_mesh()
    except Exception: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)>X1 or max(v.x for v in bb)<X0 or min(v.y for v in bb)>Y1 or max(v.y for v in bb)<Y0: oe.to_mesh_clear(); continue
    bm=bmesh.new(); bm.from_mesh(me); bm.transform(o.matrix_world); T[o.name]=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear()
names=sorted(T); code={n:'abcdefghijklmnopqrstuvwxyz'[i] for i,n in enumerate(names)}
print('P183LEGEND',code,flush=True)
L=[]
for y in np.arange(Y1,Y0-1e-6,-ST):
    r=''
    for x in np.arange(X0,X1+1e-6,ST):
        hs=[]
        for n,t in T.items():
            h=t.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))
            if h[0]: hs.append((h[0].z,n))
        hs.sort(reverse=True)
        r+=code[hs[0][1]] if hs else ' '
        if len(hs)>1 and hs[0][0]-hs[1][0]<0.004 and code[hs[0][1]]!=code[hs[1][1]]: L.append((round(x,2),round(y,2),hs[0][1][:24],hs[1][1][:24],round(hs[0][0],3),round(hs[1][0],3)))
    print('P183 %7.2f %s'%(y,r),flush=True)
print('P183 ZFIGHT n',len(L)); 
for l in L[:60]: print('P183ZF',l)
