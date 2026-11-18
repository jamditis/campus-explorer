import numpy as np, json, sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_scipy')
from scipy.spatial import cKDTree
V=np.array(json.load(open('scripts/ws100/cw100.json')))
z=np.load('data/pts_crop.npz'); x,y,h,c=z['x'],z['y'],z['z'],z['c']
m=(c==2)&(x>-260)&(x<-170)&(y>-175)&(y<-40); P=np.c_[x[m],y[m]]; H=h[m]; kd=cKDTree(P)
idx=kd.query_ball_point(V[:,:2],0.6)
g=np.array([np.median(H[i]) if len(i)>=3 else np.nan for i in idx])
dz=g+0.08-V[:,2]
ok=~np.isnan(dz); S=V[ok,:2]; D=np.clip(dz[ok],0,None)
print('cw verts',len(V),'withL',ok.sum(),'raw dz pos>0.2:',(dz[ok]>0.2).sum(), 'max %.2f'%np.nanmax(dz))
X0,X1,Y0,Y1,R=-260,-170,-175,-40,0.25
gx=np.arange(X0,X1+R,R); gy=np.arange(Y0,Y1+R,R); GX,GY=np.meshgrid(gx,gy); G=np.c_[GX.ravel(),GY.ravel()]
ks=cKDTree(S); sig=3.0
num=np.zeros(len(G)); den=np.zeros(len(G))
nb=ks.query_ball_point(G,3*sig)
for k,ii in enumerate(nb):
    if ii:
        w=np.exp(-((S[ii]-G[k])**2).sum(1)/(2*sig*sig)); num[k]=(w*D[ii]).sum(); den[k]=w.sum()
F=np.where(den>0,num/np.maximum(den,1e-9),0)
dd,_=cKDTree(V[:,:2]).query(G)
t=np.clip((dd-4)/(12-4),0,1); fall=0.5*(1+np.cos(np.pi*t))
F=(F*fall).reshape(GX.shape)
np.savez('scripts/ws100/field100.npz',F=F,X0=X0,Y0=Y0,R=R)
for yy in range(-160,-50,5):
    r=F[int((yy-Y0)/R)]; print('y%4d'%yy,' '.join('%.2f'%r[int((xx-X0)/R)] for xx in range(-244,-186,4)))
print('x',list(range(-244,-186,4)))
