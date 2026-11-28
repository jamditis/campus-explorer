# ws269: 2023 LiDAR canopy check for the Lot 33 island tree (x -362..-305, y -60..-25): class-1 height over class-2 ground, 1 m max grid
import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937; X0,X1,Y0,Y1=-362.,-305.,-60.,-25.
P=[]
for fn in ['data/lpc_2023_J5D6.laz','north/data/USGS_LPC_NJ_NE6County_B23_J5D5.laz']:
    with laspy.open(fn) as rd:
        for ch in rd.chunk_iterator(2_000_000):
            x=(np.asarray(ch.x)-OE)*F; y=(np.asarray(ch.y)-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
            if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m]])
P=np.vstack(P); print('pts',len(P),'classes',np.unique(P[:,3],return_counts=True))
nx,ny=int(X1-X0),int(Y1-Y0); g=np.full((ny,nx),np.nan); t=np.full((ny,nx),-1e9)
ix=((P[:,0]-X0)).astype(int).clip(0,nx-1); iy=((P[:,1]-Y0)).astype(int).clip(0,ny-1)
G=P[:,3]==2; gz=np.median(P[G,2]) if G.any() else None
for c in (2,):
    m=P[:,3]==c; 
    for a,b,z in zip(iy[m],ix[m],P[m,2]): g[a,b]=z if np.isnan(g[a,b]) else min(g[a,b],z)
V=np.isin(P[:,3],[1,3,4,5])
np.maximum.at(t,(iy[V],ix[V]),P[V,2])
gf=np.where(np.isnan(g),np.nanmedian(g),g); h=np.where(t>-1e8,t-gf,0)
for yy in range(ny-1,-1,-2): print('%4d '%(Y0+yy)+''.join('#' if v>10 else ('+' if v>6 else ('.' if v>2.5 else ' ')) for v in h[yy]))
i=np.unravel_index(np.argmax(np.where((np.arange(nx)[None,:]+X0<-335),h,0)),h.shape); print('max W of -335: x',X0+i[1]+.5,'y',Y0+i[0]+.5,'h',round(h[i],1))
