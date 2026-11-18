import numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
pf=(-0.01446,-11.028)
res={}
for tag in ['2017','2023']:
    P=np.vstack([np.load('prep/ws175_scurb/las175%s_%s.npy'%(sf,tag)) for sf in ('','E2')]); P=P[P[:,3]==2]
    dd=P[:,:2]-A; ps=dd@N; pt=dd@T
    for tt in range(32,184,4):
        off=ps-np.polyval(pf,tt); k=(abs(pt-tt)<2)&(off>-1.5)&(off<2.5)
        if k.sum()<20: continue
        # asphalt level = median I at off 1.5..2.5 ; concrete level = median I at off -1.0..-0.2
        Ia=np.median(P[k&(off>1.5),4]); Ic=np.median(P[k&(off<-0.2),4]); thr=(Ia+Ic)/2
        bins=np.arange(-1.0,2.0,0.1); mi=[np.median(P[k&(off>=b)&(off<b+0.2),4]) if (k&(off>=b)&(off<b+0.2)).sum()>1 else np.nan for b in bins]
        # last bin (going north) where I > thr
        e=np.nan
        for b,v in zip(bins,mi):
            if not np.isnan(v) and v>thr: e=b+0.1
        res.setdefault(tt,{})[tag]=e
        print(tag,'t %3d Ia %5d Ic %5d edge off %+.2f'%(tt,Ia,Ic,e))
