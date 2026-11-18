import laspy, numpy as np, os
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-380.,-340.,-250.,-215.
P=[]
for fn in ['data/lpc_2023_J5D6.laz','north/data/USGS_LPC_NJ_NE6County_B23_J5D5.laz']:
    rd=laspy.open(fn)
    h=rd.header
    if h.maxs[0]<OE+X0/F or h.mins[0]>OE+X1/F or h.maxs[1]<ON+Y0/F or h.mins[1]>ON+Y1/F: print('skip',fn); continue
    for ch in rd.chunk_iterator(1_000_000):
        x=(np.asarray(ch.x)-OE)*F; y=(np.asarray(ch.y)-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
        if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]].astype(np.float32))
P=np.vstack(P); np.save('prep/ws181_lot36/las181_W.npy',P); print('N',len(P))
g=P[P[:,3]==2]
for y in np.arange(-226.5,-243,-1):
    s=''
    for x in np.arange(-379.5,-345,1.5):
        m=(abs(g[:,0]-x)<0.75)&(abs(g[:,1]-y)<0.5)
        v=np.median(g[m,4]) if m.sum() else -1
        s+= '.' if v<0 else ('a' if v<3000 else ('m' if v<5500 else 'g'))
    print('%.1f'%y,s)
