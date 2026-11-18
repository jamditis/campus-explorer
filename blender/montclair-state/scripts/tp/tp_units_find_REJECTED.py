# tp: small DSM bumps 0.7-2.5 m above the modelled Bohn level roofs (cells >=1.2 m inside the level edge) -> roof unit list
import json,numpy as np
from shapely.geometry import Polygon,Point
from scipy import ndimage
d=np.load('data/tj/bohn_grid_1m.npz'); D=d[[f for f in d.files if f.endswith('__dsm')][0]]
X0,X1,Y0,Y1,_=d['extent']; ny,nx=D.shape
E=json.load(open('data/tl/bohn_levels_rect.json'))
polys=[(Polygon(p).buffer(0),t) for L in E['levels'] for p,t in zip(L['polys'],L['tops'])]
SH=json.load(open('data/tp/shafts.json')); SP=[Polygon(s['fp']).buffer(0.8) for s in SH]
M=np.full(D.shape,np.nan); OK=np.zeros(D.shape,bool)
for j in range(ny):
  for i in range(nx):
    pt=Point(X0+i+0.5,Y0+j+0.5); c=[(P,t) for P,t in polys if P.contains(pt)]
    if not c: continue
    P,t=max(c,key=lambda a:a[1]); M[j,i]=t
    OK[j,i]=P.buffer(-1.2).contains(pt) and not any(s.contains(pt) for s in SP)
ex=(D-M); m=(ex>0.7)&(ex<2.5)&OK
lab,n=ndimage.label(m); out=[]
for r in range(1,n+1):
  jj,ii=np.where(lab==r)
  if len(jj)>9: continue
  out.append(dict(x=float(X0+ii.mean()+0.5),y=float(Y0+jj.mean()+0.5),w=float(max(1.2,np.ptp(ii)+1)),l=float(max(1.2,np.ptp(jj)+1)),roof=float(np.median(M[jj,ii])),h=float(min(2.0,np.median(ex[jj,ii])))))
for o in out: print({k:round(v,1) for k,v in o.items()})
json.dump(out,open('data/tp/roof_units.json','w'))
