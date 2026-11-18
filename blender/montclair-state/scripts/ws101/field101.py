import numpy as np, sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_scipy')
from scipy.spatial import cKDTree
D=np.load('scripts/ws101/dump101.npz'); U=np.load('scripts/ws101/dumpua.npz')
cw=D['WS27_CollegeAve_carriageway_2020ortho']; cw=cw[cw[:,1]<-105]
ua=U['UA_CollegeAve_spur_1557427669_UNVERIFIED']; ua=ua[ua[:,1]>-205]
V=np.r_[cw,ua]
z=np.load('data/pts_crop.npz'); x,y,h,c=z['x'],z['y'],z['z'],z['c']
m=(c==2)&(x>-275)&(x<-170)&(y>-215)&(y<-95); P=np.c_[x[m],y[m]]; H=h[m]; kd=cKDTree(P)
idx=kd.query_ball_point(V[:,:2],0.6)
g=np.array([np.median(H[i]) if len(i)>=3 else np.nan for i in idx])
dz=g+0.08-V[:,2]; ok=~np.isnan(dz); S=V[ok,:2]; Dz=np.clip(dz[ok],0,None)
print('verts',len(V),'withL',ok.sum(),'max %.2f'%Dz.max())
X0,X1,Y0,Y1,R=-275,-170,-215,-95,0.25
gx=np.arange(X0,X1+R,R); gy=np.arange(Y0,Y1+R,R); GX,GY=np.meshgrid(gx,gy); G=np.c_[GX.ravel(),GY.ravel()]
ks=cKDTree(S); sig=3.0; num=np.zeros(len(G)); den=np.zeros(len(G))
dd,_=cKDTree(V[:,:2]).query(G); near=dd<12.5
for k in np.where(near)[0]:
    ii=ks.query_ball_point(G[k],4.2*sig)
    if ii:
        w=np.exp(-((S[ii]-G[k])**2).sum(1)/(2*sig*sig)); num[k]=(w*Dz[ii]).sum(); den[k]=w.sum()
F=np.where(den>0,num/np.maximum(den,1e-9),0)
t=np.clip((dd-4)/(12-4),0,1); F*=0.5*(1+np.cos(np.pi*t))
gyv=G[:,1]
tn=np.clip((gyv-(-120))/((-112)-(-120)),0,1); F*=0.5*(1+np.cos(np.pi*tn))   # N cut-off: full at -120, 0 at -112 (ws100 zone)
ts=np.clip((gyv-(-197))/((-187)-(-197)),0,1); F*=0.5*(1-np.cos(np.pi*ts))   # S onset: 0 at -197, full at -187
F=F.reshape(GX.shape)
np.savez('scripts/ws101/field101.npz',F=F,X0=X0,Y0=Y0,R=R)
xs=list(range(-250,-186,6))
for yy in range(-200,-104,6):
    r=F[int((yy-Y0)/R)]; print('y%4d'%yy,' '.join('%.2f'%r[int((xx-X0)/R)] for xx in xs))
print('x   ',xs)
# predicted road residual
def fld(xy):
    i=((xy[:,0]-X0)/R).round().astype(int); j=((xy[:,1]-Y0)/R).round().astype(int); return F[j,i]
for nm,A in (('cw',cw),('ua',ua)):
    gg=np.array([np.median(H[i]) if len(i)>=3 else np.nan for i in kd.query_ball_point(A[:,:2],0.6)])
    r=A[:,2]+fld(A[:,:2])-gg
    for y0 in range(-200,-100,10):
        s=(A[:,1]>=y0)&(A[:,1]<y0+10)&np.isfinite(r)
        if s.sum(): print(nm,y0,'after med %.2f [%.2f,%.2f]'%(np.median(r[s]),r[s].min(),r[s].max()))
