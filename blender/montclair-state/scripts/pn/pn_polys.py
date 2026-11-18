# pn: building-aligned tier polygons + hip blocks for the clean Feliciano re-mass (UNVERIFIED approximation of LiDAR).
import numpy as np, json
from scipy import ndimage as nd
from shapely.geometry import box, LineString, Polygon, MultiPolygon
from shapely.ops import unary_union, polygonize
from shapely import affinity
d=np.load('data/pn/raster.npz'); Z=d['Z']; th=float(d['th']); cx,cy=float(d['cx']),float(d['cy']); u0,v0,R=float(d['u0']),float(d['v0']),float(d['R'])
c,s=np.cos(th),np.sin(th)
def w2uv(x,y): x-=cx;y-=cy; return (x*c+y*s, -x*s+y*c)
def uv2w(u,v): return (cx+u*c-v*s, cy+u*s+v*c)
W=json.load(open('data/pn/feli.json'))['walls']; segs=[]
for f in W:
    b=sorted(f,key=lambda q:q[2])[:2]; segs.append(LineString([w2uv(b[0][0],b[0][1]),w2uv(b[1][0],b[1][1])]))
fp=max(polygonize(unary_union(segs)),key=lambda p:p.area)
print('footprint area',round(fp.area,1),'roof cells area',np.isfinite(Z).sum()*R*R)
L=[143.0,146.5,150.0,153.3,156.6,161.3]
m=np.isfinite(Z); Zf=np.where(m,Z,0)
T=np.full(Z.shape,-1)
low=m&(Z<162.5)
T[low]=np.abs(Z[low][:,None]-np.array(L)[None]).argmin(1)
T[m&(Z>=162.5)]=len(L)-1   # hips sit on the 161 mass
# majority filter (5x5) on tiers
from scipy.stats import mode
Tp=np.pad(T,2,constant_values=-1); T2=T.copy()
for j,i in zip(*np.nonzero(m)):
    w=Tp[j:j+5,i:i+5].ravel(); w=w[w>=0]; T2[j,i]=np.bincount(w).argmax()
T=T2
def cells_poly(mask):
    ps=[box(u0+i*R,v0+j*R,u0+(i+1)*R,v0+(j+1)*R) for j,i in zip(*np.nonzero(mask))]
    return unary_union(ps)
out={'tiers':[],'hips':[]}
for k,Lk in enumerate(L):
    mk=T>=k
    mk=nd.binary_opening(mk,iterations=2) if k>0 else mk
    if mk.sum()<40: continue
    P=cells_poly(mk)
    if k==0: P=fp
    P=P.intersection(fp.buffer(-0.12-0.03*k,join_style=2)).buffer(0.0)
    P=P.simplify(0.3)
    geoms=[P] if isinstance(P,Polygon) else list(P.geoms)
    for g in geoms:
        if g.area<20: continue
        out['tiers'].append({'k':k,'z':Lk,'ext':[uv2w(*q) for q in list(g.exterior.coords)[:-1]],'holes':[[uv2w(*q) for q in list(h.coords)[:-1]] for h in g.interiors],'area':g.area})
# hips: components of cells >=162.5
H=m&(Z>=162.5); H=nd.binary_opening(H,iterations=2)
lab,n=nd.label(H)
for q in range(1,n+1):
    cm=lab==q
    if cm.sum()*R*R<25: continue
    jj,ii=np.nonzero(cm)
    ua,ub=u0+ii.min()*R,u0+(ii.max()+1)*R; va,vb=v0+jj.min()*R,v0+(jj.max()+1)*R
    zr=float(np.percentile(Z[cm],90))
    out['hips'].append({'u':[ua,ub],'v':[va,vb],'zr':zr,'area':float(cm.sum()*R*R)})
out['th']=th; out['cx']=cx; out['cy']=cy
json.dump(out,open('data/pn/polys.json','w'))
for t in out['tiers']: print('TIER',t['k'],t['z'],round(t['area'],1),len(t['ext']),len(t['holes']))
for h in out['hips']: print('HIP',[round(x,1) for x in h['u']+h['v']],round(h['zr'],2),round(h['area'],1))
