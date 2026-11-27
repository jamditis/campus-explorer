# ws257 UNIFY #10: 2023 LiDAR (J5D5) class-2 ground DTM, 0.5 m, S of the WS110 patch's S edge (x -290..-170, y -330..-292); same
# method/frame as prep/ws172_s77/las172.py (cell mean, hole fill by growing median, 3x3 mean). Run with /workspace/opt/geo/bin/python.
import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-290.,-170.,-330.,-292.
P=[]
rd=laspy.open('north/data/USGS_LPC_NJ_NE6County_B23_J5D5.laz')
for ch in rd.chunk_iterator(2_000_000):
    ex,ey=np.asarray(ch.x),np.asarray(ch.y)
    x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m]].astype(np.float32))
P=np.vstack(P)
print("N",len(P),np.unique(P[:,3],return_counts=True),'x',P[:,0].min(),P[:,0].max(),'y',P[:,1].min(),P[:,1].max())
R=0.5; nx=int((X1-X0)/R); ny=int((Y1-Y0)/R)
g=P[P[:,3]==2]; i=((g[:,0]-X0)/R).astype(int); j=((g[:,1]-Y0)/R).astype(int)
S=np.zeros((ny,nx)); C=np.zeros((ny,nx)); np.add.at(S,(j,i),g[:,2]); np.add.at(C,(j,i),1)
Z=np.where(C>0,S/np.maximum(C,1),np.nan)
for it in range(40):
    nn=np.isnan(Z)
    if not nn.any(): break
    Zp=np.pad(Z,1,constant_values=np.nan); st=np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)])
    with np.errstate(all='ignore'): md=np.nanmedian(st,axis=0)
    Z=np.where(nn,md,Z)
Zp=np.pad(Z,1,mode='edge'); Zs=np.mean(np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)]),axis=0)
np.save('prep/ws257_u10/dtm257.npy',np.stack([Zs,C])); print('DTM',Zs.shape,'holes',int(np.isnan(Zs).sum()),'empty cells',int((C==0).sum()))
for x in (-280,-250,-230,-210,-190,-178):
    print('ROW x',x,[round(float(Zs[int((y-Y0)/R),int((x-X0)/R)]),2) for y in (-299,-302,-305,-310,-315,-320,-325)])
