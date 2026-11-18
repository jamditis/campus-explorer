import bpy,numpy as np,os
src=open('/workspace/nj-scenes/montclair-state/scripts/ws102/apply102.py').read(); exec(src[:src.index('mats={')])
SSf=np.arange(-1,S1+1.01,0.25); FR=[frame(s) for s in SSf]; PP=np.array([f[0] for f in FR]); NN=np.array([f[1] for f in FR])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.data; nt=len(tm.vertices)
c2=np.empty(nt*3); tm.vertices.foreach_get('co',c2); c2=c2.reshape(-1,3); MT=np.array(T.matrix_world); TW=c2@MT[:3,:3].T+MT[:3,3]
sel=np.where((TW[:,0]>-240)&(TW[:,0]<-200)&(TW[:,1]>-190)&(TW[:,1]<-152))[0]; n=0
for k in sel:
    q=TW[k,:2]; dd=np.hypot(*(PP-q).T); a=int(np.argmin(dd)); s=SSf[a]
    if s<0.3 or s>23.5: continue
    o=(q-PP[a])@NN[a]; e=eE(s); d_out=max(e-o,o-EW,0.0)
    if d_out<2.5:
        lim=zc(s)-(0.05 if d_out==0 else 0.02)
        if TW[k,2]>lim: TW[k,2]=lim; n+=1
Mi=np.linalg.inv(MT); tm.vertices.foreach_set('co',(TW@Mi[:3,:3].T+Mi[:3,3]).ravel()); tm.update(); print('S102 plaza-edge terrain capped',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('S102 SAVED')
