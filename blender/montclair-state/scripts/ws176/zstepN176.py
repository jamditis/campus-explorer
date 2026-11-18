# UNIFY #83: WS110 N curb position from the LiDAR curb z-step (both years). Frame per prep/ws175_scurb/REFS.md
import numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
face=lambda t: -0.01462*t+0.292
for yr in ['2023','2017']:
    P=np.vstack([np.load('prep/ws175_scurb/las175_%s.npy'%yr),np.load('prep/ws175_scurb/las175E2_%s.npy'%yr)])
    try: P=np.vstack([P,np.load('prep/ws174_scurb/las174%s.npy'%('' if yr=='2023' else '_2017'))[:, :5]])
    except Exception as e: pass
    P=P[np.isin(P[:,3],[1,2])]
    d=P[:,:2]-A; s=d@N; t=d@T
    print('YEAR',yr,'pts',len(P))
    res=[]
    for tc in range(30,186,4):
        m=(abs(t-tc)<2.0)&(abs(s-face(tc))<2.5)
        if m.sum()<40: print(yr,'t %3d n %4d -'%(tc,m.sum())); continue
        ss=s[m]-face(tc); tt=t[m]-tc; zz=P[m,2]
        best=None
        for s0 in np.arange(-1.6,1.61,0.05):
            H=(ss>s0).astype(float)
            X=np.c_[np.ones_like(ss),tt,np.minimum(ss,s0),np.maximum(ss-s0,0),H]
            c,r,*_=np.linalg.lstsq(X,zz,rcond=None)
            rr=np.sqrt(np.mean((X@c-zz)**2))
            if best is None or rr<best[0]: best=(rr,s0,c[4])
        print(yr,'t %3d n %4d step_off %+.2f rise %+.3f rms %.3f'%(tc,m.sum(),best[1],best[2],best[0]))
        if 0.06<best[2]<0.25: res.append((tc,best[1]))
    r=np.array(res)
    if len(r):
        for a,b in [(30,66),(66,110),(110,150),(150,186)]:
            k=(r[:,0]>=a)&(r[:,0]<b); print(yr,'BIN t %d..%d median off %+.2f n %d'%(a,b,np.median(r[k,1]) if k.any() else np.nan,k.sum()))
        print(yr,'ALL median %+.2f n %d'%(np.median(r[:,1]),len(r)))
