# Panzer gym + S block LiDAR massing: OSM 312847981 minus the E wing (verts 23..29), roof = 1 m class-6 medians, clipped exactly to the outline
import sys; sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
import json,numpy as np
from shapely.geometry import Polygon, box
from shapely import contains_xy
J=json.load(open('prep/ws158_PanzerE/panzer158.json')); o=J['outer']
if o[0]==o[-1]: o=o[:-1]
gp=[p for i,p in enumerate(o) if not (23<=i<=29)]
G=Polygon(gp).buffer(0); print('gym area',round(G.area),'verts',len(gp))
d=np.load('data/pts_panzer158.npz'); X,Y,Z,C=d['x'],d['y'],d['z'],d['c']
inn=G.buffer(-0.4); m=(C==6)&contains_xy(inn,X,Y); X,Y,Z=X[m],Y[m],Z[m]
x0,y0,x1,y1=G.bounds; x0=np.floor(x0)-1; y0=np.floor(y0)-1; nx=int(np.ceil(x1-x0))+2; ny=int(np.ceil(y1-y0))+2
ix=((X-x0)).astype(int); iy=((Y-y0)).astype(int)
cell=np.full((ny,nx),np.nan)
from collections import defaultdict
acc=defaultdict(list)
for i,j,z in zip(iy,ix,Z): acc[(i,j)].append(z)
for (i,j),v in acc.items(): cell[i,j]=np.median(v)
# nodes
N=np.full((ny+1,nx+1),np.nan)
for i in range(ny+1):
    for j in range(nx+1):
        v=cell[max(i-1,0):i+1,max(j-1,0):j+1]; v=v[~np.isnan(v)]
        if v.size: N[i,j]=v.mean()
for it in range(60):
    nan=np.isnan(N)
    if not nan.any(): break
    P=np.pad(N,1,constant_values=np.nan); S=np.nansum([P[:-2,1:-1],P[2:,1:-1],P[1:-1,:-2],P[1:-1,2:]],0); K=np.sum(~np.isnan([P[:-2,1:-1],P[2:,1:-1],P[1:-1,:-2],P[1:-1,2:]]),0)
    f=nan&(K>0); N[f]=S[f]/K[f]
from numpy.lib.stride_tricks import sliding_window_view as swv
for k in (5,5,3):
    Pd=np.pad(N,k//2,mode='edge'); N=np.median(swv(Pd,(k,k)),axis=(-1,-2))
print('smoothed nodes')
def hz(x,y):
    fx=x-x0; fy=y-y0; j=min(max(int(fx),0),nx-1); i=min(max(int(fy),0),ny-1); tx=fx-j; ty=fy-i
    return float(N[i,j]*(1-tx)*(1-ty)+N[i,j+1]*tx*(1-ty)+N[i+1,j]*(1-tx)*ty+N[i+1,j+1]*tx*ty)
faces=[]
for i in range(ny):
    for j in range(nx):
        c=box(x0+j,y0+i,x0+j+1,y0+i+1)
        if not G.intersects(c): continue
        q=G.intersection(c)
        for g in getattr(q,'geoms',[q]):
            if g.geom_type!='Polygon' or g.area<1e-4: continue
            pts=list(g.exterior.coords)[:-1]
            faces.append([[round(x,3),round(y,3),round(hz(x,y),3)] for x,y in pts])
walls=[]
ring=list(G.exterior.coords)
for (ax,ay),(bx,by) in zip(ring[:-1],ring[1:]):
    L=np.hypot(bx-ax,by-ay); n=max(1,int(np.ceil(L/1.0)))
    for k in range(n):
        t0,t1=k/n,(k+1)/n; p0=(ax+(bx-ax)*t0,ay+(by-ay)*t0); p1=(ax+(bx-ax)*t1,ay+(by-ay)*t1)
        walls.append([p0[0],p0[1],hz(*p0),p1[0],p1[1],hz(*p1)])
zs=[v[2] for f in faces for v in f]; print('roof faces',len(faces),'z',round(min(zs),2),round(np.median(zs),2),round(max(zs),2),'wall segs',len(walls))
json.dump({'faces':faces,'walls':walls},open('scripts/ws158/gym158.json','w'))
