import numpy as np
from scipy.ndimage import gaussian_filter1d
f=np.load('feat137p.npz'); Z,Isd,xs,ys=f['Z'],f['Isd'],f['xs'],f['ys']
Zr=np.load('dtm137p_0p25m.npy')
thr=float(__import__("sys").argv[1])
print('Isd thr',thr)
out=[]
for x in np.arange(-172,-88,1.0):
    j=np.argmin(abs(xs-x)); col=gaussian_filter1d(Isd[:,j],2)
    iy=[i for i in range(len(ys)) if -292<ys[i]<(-262 if x<-161 else -267)]
    # first y going S where texture becomes rough and stays rough for 1.5 m
    ys_edge=None
    for k,i in enumerate(iy):
        if all(col[i:i+6]>thr): ys_edge=ys[i]; break
    # curb step: max drop in raw Z over 0.75 m within ±2 m of the texture edge
    step=None
    if ys_edge is not None:
        zz=Zr[:,j]; best=(0,None)
        for i in iy:
            if abs(ys[i]-ys_edge)<2.5 and i+3<len(ys) and not np.isnan(zz[i]) and not np.isnan(zz[i+3]):
                d=zz[i]-zz[i+3]
                if abs(d)>abs(best[0]): best=(d,ys[i]-0.375)
        step=best
    # paving z just N of the edge
    zp=np.nanmedian(Zr[(ys>ys_edge)&(ys<ys_edge+3),j]) if ys_edge is not None else np.nan
    out.append((x,ys_edge,zp,step))
    print(f"x {x:6.1f}  S-edge(texture) y {ys_edge}  pave z {zp:.2f}  maxstep {None if step is None else (round(step[0],3),step[1])}")
