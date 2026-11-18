import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-92.,-60.,-256.,-194.
rd=laspy.open('data/lpc_2023_J5D6.laz'); P=[]
for ch in rd.chunk_iterator(3_000_000):
    x=(np.asarray(ch.x)-OE)*F; y=(np.asarray(ch.y)-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]])
P=np.vstack(P); np.save('scripts/ws140/las140.npy',P); print('N',len(P),np.unique(P[:,3],return_counts=True))
g=P[P[:,3]==2]
# 1m grid: ground z, max nonground height above ground, mean intensity of ground
for y in range(-196,-256,-2):
    row=[]
    for x in range(-90,-62,2):
        m=(g[:,0]>=x)&(g[:,0]<x+2)&(g[:,1]>=y-2)&(g[:,1]<y)
        a=P[(P[:,0]>=x)&(P[:,0]<x+2)&(P[:,1]>=y-2)&(P[:,1]<y)]
        gz=np.median(g[m,2]) if m.sum() else np.nan
        cl=np.bincount(a[:,3].astype(int),minlength=7) if len(a) else np.zeros(7)
        hmax=(a[:,2].max()-gz) if len(a) and m.sum() else np.nan
        it=np.median(g[m,4]) if m.sum() else np.nan
        tag='B' if cl[6]>len(a)*0.5 else ('T' if hmax>3 else ('s' if hmax>0.4 else '.'))
        row.append(f"{gz:6.2f}{tag}{int(it) if it==it else 0:>5}")
    print(y,' '.join(row))
