import numpy as np
P=np.load('/workspace/nj-scenes/montclair-state/prep/ws174_scurb/las174_2017.npy'); P=P[P[:,3]==2]
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
d=P[:,:2]-A; s=d@N; t=d@T; z=P[:,2]; I=P[:,4]
bins=np.arange(-14,-7.49,0.5)
print('s-bins   '+' '.join('%5.1f'%b for b in bins[:-1]))
for tc in [-10,-5,0,5,10,15,20]:
    m=abs(t-tc)<2.5; rz=[];ri=[]
    for a,b in zip(bins[:-1],bins[1:]):
        k=m&(s>=a)&(s<b); rz.append(np.median(z[k]) if k.sum() else np.nan); ri.append(np.median(I[k]) if k.sum() else np.nan)
    rz=np.array(rz); base=np.nanmin(rz)
    print('t%6.1f dz '%tc+' '.join('%5.0f'%((v-base)*100) if v==v else '  nan' for v in rz))
    print('       I   '+' '.join('%5.0f'%v if v==v else '  nan' for v in ri))
