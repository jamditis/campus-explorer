import numpy as np
P=np.vstack([np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/las163.npy'),np.load('/workspace/nj-scenes/montclair-state/prep/ws172_s77/las172.npy')])
P=P[P[:,3]==2]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
d=P[:,:2]-A; s=d@N; t=d@T; z=P[:,2]; I=P[:,4]
bins=np.arange(-14,-7.49,0.25)
print('s-bins   '+' '.join('%5.1f'%b for b in bins[:-1]))
for tc in [-65,-62.5,-60,-47.5,-45,-32.5,-30,-25,-20,-15,-10,-5,-2.5]:
    m=abs(t-tc)<1.5
    rz=[];ri=[]
    for a,b in zip(bins[:-1],bins[1:]):
        k=m&(s>=a)&(s<b)
        rz.append(np.median(z[k]) if k.sum() else np.nan); ri.append(np.median(I[k]) if k.sum() else np.nan)
    rz=np.array(rz); base=np.nanmin(rz)
    print('t%6.1f dz '%tc+' '.join('%5.0f'%((v-base)*100) if v==v else '  nan' for v in rz))
    print('       I/1k'+' '.join('%5.1f'%(v/1000) if v==v else '  nan' for v in ri))
