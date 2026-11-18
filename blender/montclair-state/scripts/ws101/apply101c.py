import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B='/workspace/nj-scenes/montclair-state/scripts/ws101/'
l=np.load(B+'lidgrid101.npz'); LG=l['G']; LX,LY,LR=float(l['X0']),float(l['Y0']),float(l['R'])
def lid(xy):
    i=np.round((xy[:,0]-LX)/LR).astype(int); j=np.round((xy[:,1]-LY)/LR).astype(int)
    ok=(i>=0)&(i<LG.shape[1])&(j>=0)&(j<LG.shape[0]); out=np.full(len(xy),np.nan); out[ok]=LG[j[ok],i[ok]]; return out
o=bpy.data.objects['UA_CollegeAve_spur_1557427669_UNVERIFIED']; me=o.data; n=len(me.vertices)
co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
key=[(round(a,2),round(b,2)) for a,b in W[:,:2]]; top={}
for k,z in zip(key,W[:,2]): top[k]=max(top.get(k,-1e9),z)
zt=np.array([top[k] for k in key])
# smooth LiDAR target along the spur: median over 1.5 m
L=lid(W[:,:2])
t=np.clip((W[:,1]+186)/(-161+186),0,1); w=t*t*(3-2*t)
# near the joint, also snap to the carriageway end height
cw=bpy.data.objects['WS27_CollegeAve_carriageway_2020ortho']; cco=np.array([cw.matrix_world@v.co for v in cw.data.vertices])
endz=np.median(cco[cco[:,1]<-159.5][:,2])
tgt=np.where(np.isfinite(L),L+0.08,zt)
jw=np.clip((W[:,1]+164)/3.0,0,1)  # last 3 m before the joint -> carriageway end height
tgt=tgt*(1-jw)+endz*jw
dz=(tgt-zt)*w; dz[W[:,1]>-157]=0
print('C101 spur verts moved',int((abs(dz)>0.01).sum()),'dz range %.2f..%.2f endz %.2f'%(dz.min(),dz.max(),endz))
W[:,2]+=dz; Mi=np.linalg.inv(M); me.vertices.foreach_set('co',(W@Mi[:3,:3].T+Mi[:3,3]).ravel()); me.update()
# terrain cap under spur + carriageway S end
vs=[];tris=[]
for nm in ('UA_CollegeAve_spur_1557427669_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho'):
    ob=bpy.data.objects[nm]; mw=ob.matrix_world; b=len(vs); vs+=[mw@v.co for v in ob.data.vertices]
    for p in ob.data.polygons: tris.append([b+i for i in p.vertices])
bvh=BVHTree.FromPolygons(vs,tris)
t_=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=t_.data; nt=len(tm.vertices)
c2=np.empty(nt*3); tm.vertices.foreach_get('co',c2); c2=c2.reshape(-1,3); MT=np.array(t_.matrix_world); TW=c2@MT[:3,:3].T+MT[:3,3]
s=np.where((TW[:,0]>-235)&(TW[:,0]<-205)&(TW[:,1]>-195)&(TW[:,1]<-150))[0]; cap=0
for k in s:
    h=bvh.ray_cast(Vector((TW[k,0],TW[k,1],TW[k,2]+5)),Vector((0,0,-1)),12)
    if h[0] is not None and TW[k,2]>h[0].z-0.05: TW[k,2]=h[0].z-0.05; cap+=1
Mi=np.linalg.inv(MT); tm.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); tm.update(); print('C101 terrain capped',cap)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('C101 SAVED')
