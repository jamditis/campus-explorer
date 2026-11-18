import bpy, numpy as np
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(M) as (a,b): b.objects=['fd_rhd_ramp_barrier_curb']
o=b.objects[0]; mw=o.matrix_world
P=np.array([tuple(mw@v.co) for v in o.data.vertices]); print('R206 verts',len(P),'mods',[m.type for m in o.modifiers])
m=(abs(P[:,0]+310.4)<5)&(abs(P[:,1]+11.2)<5); Q=P[m]; print('R206 near',len(Q),'z %.2f..%.2f'%(Q[:,2].min(),Q[:,2].max()) if len(Q) else '')
if len(Q)>3:
    c=Q[:,:2].mean(0); u,s,vt=np.linalg.svd(Q[:,:2]-c); d=(Q[:,:2]-c)@vt[1]
    print('R206 dir',vt[0],'perp spread',np.round(np.percentile(d,[0,10,50,90,100]),3))
    # cluster rows by perpendicular offset
    for z in sorted(set(np.round(Q[:,2],1)))[:8]:
        k=np.round(Q[:,2],1)==z; print('R206 z',z,len(Q[k]),np.round(np.sort(d[k]),3)[:20])
