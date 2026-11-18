import bpy, numpy as np, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B='/workspace/nj-scenes/montclair-state/scripts/ws101/'
l=np.load(B+'lidgrid101f.npz'); LG=l['G']; LX,LY,LR=float(l['X0']),float(l['Y0']),float(l['R'])
def lid(xy):
    i=np.round((xy[:,0]-LX)/LR).astype(int); j=np.round((xy[:,1]-LY)/LR).astype(int)
    ok=(i>=0)&(i<LG.shape[1])&(j>=0)&(j<LG.shape[0]); out=np.full(len(xy),np.nan); out[ok]=LG[j[ok],i[ok]]; return out
X0,X1,Y0,Y1,FE=-209.0,-172.0,-172.0,-128.0,3.0
def wbox(xy):
    d=np.minimum.reduce([xy[:,0]-X0,X1-xy[:,0],xy[:,1]-Y0,Y1-xy[:,1]]); t=np.clip(d/FE,0,1); return t*t*(3-2*t)
SAVE=os.environ.get('SAVE')=='1'
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; n=len(me.vertices)
co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(t.matrix_world); W=co@M[:3,:3].T+M[:3,3]
s=np.where((W[:,0]>X0)&(W[:,0]<X1)&(W[:,1]>Y0)&(W[:,1]<Y1))[0]
lz=lid(W[s,:2]); dz=np.where(np.isfinite(lz),np.clip(lz-W[s,2],0,None),0)*wbox(W[s,:2])
print('B101 terrain verts',len(s),'raised',int((dz>0.01).sum()),'max %.2f med(raised) %.2f'%(dz.max(),np.median(dz[dz>0.01]) if (dz>0.01).any() else 0))
W[s,2]+=dz
PAVE=['WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','UA_CollegeAve_spur_1557427669_UNVERIFIED']
vs=[];tris=[]
for nm in PAVE:
    o=bpy.data.objects.get(nm); mw=o.matrix_world; b=len(vs); vs+=[mw@v.co for v in o.data.vertices]
    for p in o.data.polygons: tris.append([b+i for i in p.vertices])
bvh=BVHTree.FromPolygons(vs,tris); capped=0
for k in s:
    best=None; center=False
    for off in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
        h=bvh.ray_cast(Vector((W[k,0]+off[0],W[k,1]+off[1],W[k,2]+5)),Vector((0,0,-1)),12)
        if h[0] is not None:
            center|=off==(0,0); best=h[0].z if best is None else min(best,h[0].z)
    if best is not None and W[k,2]>best-0.05:
        pu=W[k,2]-(best-0.05)
        if not center and pu>0.2: continue
        W[k,2]=best-0.05; capped+=1
Mi=np.linalg.inv(M); me.vertices.foreach_set('co',(W@Mi[:3,:3].T+Mi[:3,3]).ravel()); me.update()
print('B101 capped under paving',capped)
mv=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.parent or o.name.startswith('Terrain'): continue
    c=np.array(o.matrix_world.translation)
    if not(X0<c[0]<X1 and Y0<c[1]<Y1): continue
    bb=[o.matrix_world@Vector(q) for q in o.bound_box]
    if max(v.x for v in bb)-min(v.x for v in bb)>15 and o.data.users==1: continue
    z=lid(c[None,:2])[0]
    if not np.isfinite(z): continue
    d=float(np.clip(z-c[2],0,None)*wbox(c[None,:2])[0])
    if 0.02<d<3: o.matrix_world.translation.z+=d; mv.append((o.name[:40],round(d,2)))
print('B101 moved',mv)
if SAVE: bpy.ops.wm.save_mainfile(); print('B101 SAVED')
