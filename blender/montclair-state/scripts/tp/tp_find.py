# tp: find Bohn DSM cells that rise >1.5 m above the modelled TL level tops (unmodelled shafts/bulkheads)
import json,numpy as np
from shapely.geometry import Polygon,Point
from scipy import ndimage
d=np.load('data/tj/bohn_grid_1m.npz'); k=[f for f in d.files if f.endswith('__dsm')][0]; D=d[k]
X0,X1,Y0,Y1,_=d['extent']; ny,nx=D.shape
E=json.load(open('data/tl/bohn_levels_rect.json'))
polys=[(Polygon(p).buffer(0),t) for L in E['levels'] for p,t in zip(L['polys'],L['tops'])]
M=np.full(D.shape,np.nan)
for j in range(ny):
  for i in range(nx):
    pt=Point(X0+i+0.5,Y0+j+0.5); ts=[t for P,t in polys if P.contains(pt)]
    if ts: M[j,i]=max(ts)
ex=(D-M)>1.5
lab,n=ndimage.label(ex); out=[]
for r in range(1,n+1):
  jj,ii=np.where(lab==r)
  if len(jj)<4: continue
  xs=X0+ii+0.5; ys=Y0+jj+0.5
  out.append(dict(n=int(len(jj)),x0=float(xs.min()-.5),x1=float(xs.max()+.5),y0=float(ys.min()-.5),y1=float(ys.max()+.5),
     model_top=float(np.nanmedian(M[jj,ii])),dsm_med=float(np.median(D[jj,ii])),dsm_max=float(D[jj,ii].max()),cells=[[float(a),float(b)] for a,b in zip(xs,ys)]))
for o in out: print({k:(round(v,1) if isinstance(v,float) else v) for k,v in o.items() if k!='cells'})
json.dump(out,open('data/tp/bohn_excess.json','w'))
