# ws179: 0.5 m class-2 DTM for the College Ave S-leg mouth window x -315..-240, y -295..-235 (2023 LiDAR), same recipe as las172.py
import numpy as np
X0,X1,Y0,Y1=-315.,-240.,-295.,-235.; R=0.5
P=np.load('/workspace/nj-scenes/montclair-state/prep/ws179_mulch/las179_2023.npy'); g=P[P[:,3]==2]
nx=int((X1-X0)/R); ny=int((Y1-Y0)/R)
i=np.clip(((g[:,0]-X0)/R).astype(int),0,nx-1); j=np.clip(((g[:,1]-Y0)/R).astype(int),0,ny-1)
S=np.zeros((ny,nx)); C=np.zeros((ny,nx)); np.add.at(S,(j,i),g[:,2]); np.add.at(C,(j,i),1)
Z=np.where(C>0,S/np.maximum(C,1),np.nan)
for it in range(40):
    nn=np.isnan(Z)
    if not nn.any(): break
    Zp=np.pad(Z,1,constant_values=np.nan); st=np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)])
    with np.errstate(all='ignore'): md=np.nanmedian(st,axis=0)
    Z=np.where(nn,md,Z)
Zp=np.pad(Z,1,mode='edge'); Zs=np.mean(np.stack([Zp[a:a+ny,b:b+nx] for a in range(3) for b in range(3)]),axis=0)
np.save('/workspace/nj-scenes/montclair-state/prep/ws179_mulch/dtm179.npy',np.stack([Zs,C]))
print('DTM179',Zs.shape,'origin',X0,Y0,'R',R,'holes',int(np.isnan(Zs).sum()),'empty',int((C==0).sum()))
# S-leg centreline profile (frame t~9.5)
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for s in range(-10,-27,-2):
    p=A+N*s+T*9.5; ii=int((p[0]-X0)/R); jj=int((p[1]-Y0)/R); print('  centre s %d xy (%.1f,%.1f) z %.2f'%(s,p[0],p[1],Zs[jj,ii]))
