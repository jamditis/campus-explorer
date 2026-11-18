# WS110 N curb face vs 2017/2023 LiDAR intensity edge (data prep for the next UNIFY item); + = LiDAR edge further N (away from road) than model
import numpy as np
V=np.load('prep/ws174_scurb/ws110_curb_verts.npy')
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
d=V[:,:2]-A; s=d@N; t=d@T; m=(s>-5)&(s<3)&(t>26)&(t<185)
tb=np.arange(26,186,2); sf=[]
for a in tb:
    k=m&(t>=a)&(t<a+2); sf.append(s[k].min() if k.any() else np.nan)
sf=np.array(sf); ok=~np.isnan(sf); pf=np.polyfit(tb[ok]+1,sf[ok],1); print('N face fit s=%.5f*t%+.3f resid %.3f n %d'%(pf[0],pf[1],np.nanmax(abs(sf-np.polyval(pf,tb+1))),ok.sum()))
for tag in ['2017','2023']:
    P=np.vstack([np.load('prep/ws175_scurb/las175%s_%s.npy'%(sf_,tag)) for sf_ in ('','E2')]); P=P[P[:,3]==2]
    dd=P[:,:2]-A; ps=dd@N; pt=dd@T; out=[]
    for tt in range(34,184,4):
        off=ps-np.polyval(pf,tt); k=(abs(pt-tt)<2)&(off>-2.5)&(off<1.5)
        if k.sum()<20: continue
        Ia=np.median(P[k&(off<-1.5),4]); Ic=np.median(P[k&(off>0.2),4]); thr=(Ia+Ic)/2
        bins=np.arange(-2.0,1.0,0.1); e=np.nan
        med=[np.median(P[k&(off>=b)&(off<b+0.2),4]) if (k&(off>=b)&(off<b+0.2)).sum()>1 else np.nan for b in bins]
        for i in range(len(bins)-2):
            if med[i]>thr and med[i+1]>thr and med[i+2]>thr: e=bins[i]+0.1; break
        out.append(e); print(tag,'t %3d Ia %5d Ic %5d edge off %+.2f'%(tt,Ia,Ic,e))
    o=np.array(out); print(tag,'median',np.nanmedian(o))
