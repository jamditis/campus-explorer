# ws259 W64: 1 m 2023 LiDAR ground grid (class 2; J5D5 for x < -268, J5D6 for x >= -268) over x -292..-232, y -246..-196 -> prep/ws259_w64/dtm259.npy (box only)
import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-292.,-232.,-246.,-196.; R=1.0; nx=int((X1-X0)/R); ny=int((Y1-Y0)/R)
S=np.zeros((ny,nx)); C=np.zeros((ny,nx))
for fn in ('north/data/USGS_LPC_NJ_NE6County_B23_J5D5.laz','data/lpc_2023_J5D6.laz'):
    for ch in laspy.open(fn).chunk_iterator(2_000_000):
        x=(np.asarray(ch.x)-OE)*F; y=(np.asarray(ch.y)-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)&(np.asarray(ch.classification)==2)
        if m.any():
            i=((x[m]-X0)/R).astype(int); j=((y[m]-Y0)/R).astype(int); np.add.at(S,(j,i),np.asarray(ch.z)[m]*0.3048006096); np.add.at(C,(j,i),1)
Z=np.where(C>0,S/np.maximum(C,1),np.nan)
for it in range(30):
    nn=np.isnan(Z)
    if not nn.any(): break
    Zp=np.pad(Z,1,constant_values=np.nan); st=np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)])
    with np.errstate(all='ignore'): md=np.nanmedian(st,axis=0)
    Z=np.where(nn,md,Z)
np.save('prep/ws259_w64/dtm259.npy',np.stack([Z,C])); print('DTM',Z.shape,'empty cells',int((C==0).sum()),'nan',int(np.isnan(Z).sum()))
for y in (-240,-230,-220,-210,-200): print('ROW y',y,[round(float(Z[int((y-Y0)/R),int((x-X0)/R)]),2) for x in range(-290,-232,6)])
