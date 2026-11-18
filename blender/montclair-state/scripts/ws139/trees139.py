import numpy as np, json
from scipy import ndimage as nd
a=np.load('scripts/ws137p/las137p.npy'); d=np.load('scripts/ws137p/dtm137p_0p25m.npy')
X0,Y1=-185.,-240.
def dz(x,y):
    i=np.clip(((Y1-y)*4).astype(int),0,d.shape[0]-1); j=np.clip(((x-X0)*4).astype(int),0,d.shape[1]-1); return d[i,j]
v=a[a[:,3]==1]; h=v[:,2]-dz(v[:,0],v[:,1])
m=(h>3)&(v[:,1]<-262.5)&(v[:,1]>-302)&(v[:,0]>-172)&(v[:,0]<-86); v=v[m]; h=h[m]
print('pts',len(v))
G=np.zeros((40,86)); # 1 m grid y -302..-262, x -172..-86
gi=((-262-v[:,1])).astype(int); gj=(v[:,0]+172).astype(int)
for i,j,hh in zip(gi,gj,h): G[i,j]=max(G[i,j],hh)
Gs=nd.gaussian_filter(G,1.2)
mx=(Gs==nd.maximum_filter(Gs,size=7))&(G>5)
lab,n=nd.label(G>3)
trees=[]
for i,j in zip(*np.nonzero(mx)):
    x=-172+j+0.5; y=-262-i-0.5
    reg=lab[i,j]; area=(lab==reg).sum() if reg else 0
    # crown radius: points within 6 m above 3m
    r=np.hypot(v[:,0]-x,v[:,1]-y); sel=(r<7)&(h>3)
    rad=np.percentile(r[sel],90) if sel.sum()>5 else 2
    trees.append(dict(x=round(x,1),y=round(y,1),z=round(float(dz(np.array([x]),np.array([y]))[0]),2),h=round(float(G[i,j]),1),crown_r=round(float(rad),1),reg_area=int(area)))
for t in sorted(trees,key=lambda t:t['x']): print(t)
json.dump(trees,open('scripts/ws139/trees139.json','w'),indent=1)
