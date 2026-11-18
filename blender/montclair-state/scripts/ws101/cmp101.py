import numpy as np, sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_scipy')
from scipy.spatial import cKDTree
z=np.load('data/pts_crop.npz'); x,y,h,c=z['x'],z['y'],z['z'],z['c']
m=(c==2)&(x>-265)&(x<-180)&(y>-180)&(y<-95); P=np.c_[x[m],y[m]]; H=h[m]; kd=cKDTree(P)
D=np.load('scripts/ws101/dump101.npz')
def lid(V,r=0.7):
    idx=kd.query_ball_point(V[:,:2],r); return np.array([np.median(H[i]) if len(i)>=3 else np.nan for i in idx])
np.save('scripts/ws101/lidP.npy',np.c_[P,H])
for k in D.files:
    V=D[k]; 
    if k.startswith('Terrain'): V=V[(V[:,1]<-112)]
    L=lid(V); d=V[:,2]-L
    print('==',k,len(V),'med %.2f min %.2f max %.2f'%(np.nanmedian(d),np.nanmin(d),np.nanmax(d)))
    for y0 in range(-170,-100,10):
        s=(V[:,1]>=y0)&(V[:,1]<y0+10)&np.isfinite(d)
        if s.sum(): print('   y%d..%d n%d x %.0f..%.0f  d med %.2f [%.2f,%.2f]'%(y0,y0+10,s.sum(),V[s,0].min(),V[s,0].max(),np.median(d[s]),d[s].min(),d[s].max()))
