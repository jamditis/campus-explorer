import numpy as np
P=np.vstack([np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/las163.npy'),np.load('/workspace/nj-scenes/montclair-state/prep/ws172_s77/las172.npy')])
P=P[P[:,3]==2]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
d=P[:,:2]-A; s=d@N; t=d@T; z=P[:,2]; I=P[:,4]
DR=[(-77.0,-70.75),(-57,-52.75),(-42.5,-35)]
def stepfit(ss,zz,lo,hi,sign):
    best=None
    for sc in np.arange(lo,hi,0.05):
        # road side: linear in s; curb side offset h
        m=(ss<sc) if sign<0 else (ss>sc)
        if m.sum()<8 or (~m).sum()<8: continue
        X=np.c_[np.ones_like(ss),ss,m.astype(float)]
        c,res,*_=np.linalg.lstsq(X,zz,rcond=None); e=((X@c-zz)**2).sum()
        if best is None or e<best[0]: best=(e,sc,c[2])
    return best
out=[]
for tc in np.arange(-77.5,-1.0,2.5):
    indr=any(a-1<=tc<=b+1 for a,b in DR)
    m=(abs(t-tc)<1.25)
    # S curb: window s -13.5..-8.5 ; walk side s<sc higher
    ms=m&(s>-13.0)&(s<-8.5); bS=stepfit(s[ms],z[ms],-12.3,-9.3,-1)
    mn=m&(s>-2.5)&(s<2.5); bN=stepfit(s[mn],z[mn],-1.5,1.5,+1)
    # intensity: median int per 0.25 m bin s -13..-8
    line='t %6.1f %s S %s N %s'%(tc,'DRIVE' if indr else '     ',
      ('%6.2f h%.3f n%d'%(bS[1],bS[2],ms.sum())) if bS else 'na',
      ('%6.2f h%.3f n%d'%(bN[1],bN[2],mn.sum())) if bN else 'na')
    print(line)
