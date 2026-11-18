import bpy, numpy as np, os
B='/workspace/nj-scenes/montclair-state/scripts/ws101/'
l=np.load(B+'lidgrid101.npz'); LG=l['G']; LX,LY,LR=float(l['X0']),float(l['Y0']),float(l['R'])
def lid(xy):
    i=np.round((xy[:,0]-LX)/LR).astype(int); j=np.round((xy[:,1]-LY)/LR).astype(int); return LG[j,i]
o=bpy.data.objects['WS73_curb_back_lawn_verge_UNVERIFIED']; me=o.data; n=len(me.vertices)
co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
c=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; C=np.array([c.matrix_world@v.co for v in c.data.vertices])
sel=np.where((W[:,0]>-196.2)&(W[:,0]<-193.3)&(W[:,1]>-97)&(W[:,1]<-91.2))[0]; ch=[]
for k in sel:
    cc=C[np.abs(C[:,1]-W[k,1])<0.3]
    if not len(cc): continue
    b=W[k,0]-cc[:,0].max(); t=np.clip(b/0.8,0,1); w=t*t*(3-2*t)
    # fade in/out along y so the edit blends into untouched verge
    ty=min(np.clip((W[k,1]+97)/1.0,0,1),np.clip((-91.2-W[k,1])/1.0,0,1)); w*=ty
    L=lid(W[k:k+1,:2])[0]
    if not np.isfinite(L): continue
    dz=w*max(0.0,W[k,2]-(L+0.02))
    if dz>0.005: W[k,2]-=dz; ch.append(round(float(dz),2))
Mi=np.linalg.inv(M); me.vertices.foreach_set('co',(W@Mi[:3,:3].T+Mi[:3,3]).ravel()); me.update()
print('D101 verge verts lowered',len(ch),'max',max(ch) if ch else 0,ch[:20])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('D101 SAVED')
