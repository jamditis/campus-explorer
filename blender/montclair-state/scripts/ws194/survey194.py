# ws194 wobble survey: plan-edge wobble score for long thin paving/curb/edge objects scene-wide.
import bpy, numpy as np, re
pat=re.compile(r'curb|kerb|walk|sidewalk|path|footway|edge|strip|drive|road|apron|ramp|verge|lawn|bed',re.I)
res=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not pat.search(o.name): continue
    me=o.data; n=len(me.vertices)
    if n<8 or n>60000: continue
    M=np.array(o.matrix_world)
    V=np.array([v.co[:] for v in me.vertices]); V=(M[:3,:3]@V.T).T+M[:3,3]
    P=V[:,:2]; c=P.mean(0); Q=P-c
    w,ev=np.linalg.eigh(np.cov(Q.T)); ax=ev[:,1]; s=Q@ax; t=Q@ev[:,0]
    L=s.max()-s.min(); Wd=t.max()-t.min()
    if L<4 or Wd/L>0.35: continue
    bins=np.arange(s.min(),s.max()+0.5,0.5); idx=np.digitize(s,bins)
    sc=[];hi=[];lo=[]
    for b in np.unique(idx):
        m=idx==b
        if m.sum()<1: continue
        sc.append(s[m].mean()); hi.append(t[m].max()); lo.append(t[m].min())
    sc=np.array(sc)
    if len(sc)<8: continue
    worst=0; rms=0
    for e in (np.array(hi),np.array(lo)):
        deg=3; p=np.polyfit(sc,e,deg); r=e-np.polyval(p,sc)
        # high-frequency: residual minus its own 3-bin moving average gives jitter
        worst=max(worst,np.abs(r).max()); rms=max(rms,np.sqrt((r**2).mean()))
    res.append((rms,worst,o.name,c[0],c[1],L,Wd))
res.sort(key=lambda a:-a[0])
for rms,worst,nm,x,y,L,Wd in res[:60]:
    print('SV rms %.3f max %.3f L %.1f W %.1f at (%.0f,%.0f) %s'%(rms,worst,L,Wd,x,y,nm),flush=True)
print('SV total',len(res))
