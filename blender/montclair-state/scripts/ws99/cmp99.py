import numpy as np, json
from scipy.spatial import cKDTree
z=np.load('data/pts_crop.npz'); x,y,h,c=z['x'],z['y'],z['z'],z['c']
m=(x>-245)&(x<-170)&(y>-110)&(y<-30)&(c==2)
P=np.c_[x[m],y[m]]; H=h[m]; kd=cKDTree(P)
d=json.load(open('scripts/ws99/bend99.json'))
res={}
for n,vs in d.items():
    V=np.array(vs)
    if len(V)==0: continue
    idx=kd.query_ball_point(V[:,:2],0.6)
    g=np.array([np.median(H[i]) if len(i)>=2 else np.nan for i in idx])
    dz=V[:,2]-g
    ok=~np.isnan(dz)
    res[n]=(V,dz)
    print(n[:40],'n',len(V),'withLiDAR',ok.sum(),'dz median %.2f p10 %.2f p90 %.2f'%(np.nanmedian(dz),np.nanpercentile(dz,10),np.nanpercentile(dz,90)))
# along-road profile for carriageway: bin by x
V,dz=res['WS27_CollegeAve_carriageway_2020ortho']
for x0 in range(-240,-175,5):
    s=(V[:,0]>=x0)&(V[:,0]<x0+5)
    if s.sum(): print('CW x%4d..%4d y%.0f..%.0f n%3d dz med %+.2f'%(x0,x0+5,V[s,1].min(),V[s,1].max(),s.sum(),np.nanmedian(dz[s])))
V,dz=res['Terrain_LiDAR_DTM_1m']
for x0 in range(-225,-180,5):
  for y0 in range(-100,-40,10):
    s=(V[:,0]>=x0)&(V[:,0]<x0+5)&(V[:,1]>=y0)&(V[:,1]<y0+10)
    if s.sum()>5 and np.abs(np.nanmedian(dz[s]))>0.25: print('TER x%d y%d n%d dz %+.2f'%(x0,y0,s.sum(),np.nanmedian(dz[s])))
