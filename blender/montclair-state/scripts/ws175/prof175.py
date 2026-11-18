import numpy as np
V=np.load('prep/ws174_scurb/ws110_curb_verts.npy')
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
d=V[:,:2]-A; s=d@N; t=d@T; m=(s<-5)&(t<185)
# model S curb face line: fit s_face(t) = max s per 2 m bin (road side)
tb=np.arange(0,186,2); sf=[]
for a in tb:
    k=m&(t>=a)&(t<a+2); sf.append(s[k].max() if k.any() else np.nan)
sf=np.array(sf); ok=~np.isnan(sf); pf=np.polyfit(tb[ok]+1,sf[ok],1); print('face fit s=%.5f*t+%.3f resid %.3f'%(pf[0],pf[1],np.nanmax(abs(sf-np.polyval(pf,tb+1)))))
for tag in ['2017','2023']:
    P=np.load('prep/ws175_scurb/las175_%s.npy'%tag); P=P[P[:,3]==2]
    dd=P[:,:2]-A; ps=dd@N; pt=dd@T
    print('==',tag,len(P))
    for tt in range(30,124,4):
        sface=np.polyval(pf,tt); off=ps-sface   # + = north (road side)
        k=(abs(pt-tt)<1.5)&(off>-4)&(off<3)
        bins=np.arange(-4,3,0.25); zs=[];Is=[]
        for b in bins:
            q=k&(off>=b)&(off<b+0.25); zs.append(np.median(P[q,2]) if q.sum()>0 else np.nan); Is.append(np.median(P[q,4]) if q.sum()>0 else np.nan)
        zs=np.array(zs); Is=np.array(Is)
        # curb: largest rise going south (decreasing off) over 0.5 m
        best=None
        for i in range(2,len(bins)):
            if np.isnan(zs[i]) or np.isnan(zs[i-2]): continue
            r=zs[i-2]-zs[i]
            if best is None or r>best[0]: best=(r,bins[i]-0.25)
        print('t %3d face s %.2f curbstep %s | z %s | I %s'%(tt,sface,'%.2f m at off %+.2f'%best if best else '-',' '.join('%.2f'%(z-np.nanmin(zs)) if not np.isnan(z) else ' nan' for z in zs[::2]),' '.join('%d'%i if not np.isnan(i) else 'nan' for i in Is[::2])))
