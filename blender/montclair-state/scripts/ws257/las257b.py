# ws257 UNIFY #10: the 2023 J5D5 tile ends at x -268, so fill x -268..-170 from the 2017 B17 tiles (J5D5 / J5D6), after checking
# 2017 vs 2023 ground on the overlap (x -290..-268). Output prep/ws257_u10/dtm257.npy (same frame as las257.py: x -290..-170, y -330..-292, 0.5 m).
import laspy, numpy as np, os
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-290.,-170.,-330.,-292.; R=0.5; nx=int((X1-X0)/R); ny=int((Y1-Y0)/R)
def grab(fn):
    P=[]
    rd=laspy.open(fn)
    for ch in rd.chunk_iterator(2_000_000):
        ex,ey=np.asarray(ch.x),np.asarray(ch.y)
        x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)&(np.asarray(ch.classification)==2)
        if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096].astype(np.float32))
    return np.vstack(P) if P else np.zeros((0,3),np.float32)
def grid(g):
    i=((g[:,0]-X0)/R).astype(int); j=((g[:,1]-Y0)/R).astype(int)
    S=np.zeros((ny,nx)); C=np.zeros((ny,nx)); np.add.at(S,(j,i),g[:,2]); np.add.at(C,(j,i),1)
    return np.where(C>0,S/np.maximum(C,1),np.nan),C
D='north/data/'
g23=grab(D+'USGS_LPC_NJ_NE6County_B23_J5D5.laz'); Z23,C23=grid(g23)
g17=np.vstack([grab(D+f) for f in ('USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D5.laz','USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz')])
Z17,C17=grid(g17)
print('pts 2023',len(g23),'2017',len(g17),'2017 x %.1f..%.1f'%(g17[:,0].min(),g17[:,0].max()) if len(g17) else '')
both=~np.isnan(Z23)&~np.isnan(Z17); d=(Z17-Z23)[both]
print('overlap cells',both.sum(),'2017-2023 median %.3f p10 %.3f p90 %.3f'%tuple(np.percentile(d,[50,10,90])))
Z=np.where(~np.isnan(Z23),Z23,Z17-np.median(d)); C=C23+C17
for it in range(60):
    nn=np.isnan(Z)
    if not nn.any(): break
    Zp=np.pad(Z,1,constant_values=np.nan); st=np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)])
    with np.errstate(all='ignore'): md=np.nanmedian(st,axis=0)
    Z=np.where(nn,md,Z)
Zp=np.pad(Z,1,mode='edge'); Zs=np.mean(np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)]),axis=0)
np.save('prep/ws257_u10/dtm257.npy',np.stack([Zs,C])); print('DTM',Zs.shape,'holes',int(np.isnan(Zs).sum()),'empty cells',int((C==0).sum()))
for x in (-280,-250,-230,-210,-190,-178):
    print('ROW x',x,[round(float(Zs[int((y-Y0)/R),int((x-X0)/R)]),2) for y in (-299,-302,-305,-310,-315,-320,-325)])
