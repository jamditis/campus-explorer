# tl: rectilinear Bohn Hall level outlines. Same 2017 1 m DSM thresholds as tk, but sampled on a grid aligned to the OSM
# footprint axes (70.5/160.5 deg), so every level edge is parallel to the OSM walls (tk's raster buffers gave faceted diagonals).
import numpy as np, json, math
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
from shapely import contains_xy
d=np.load('data/tj/bohn_grid_1m.npz'); k=[f for f in d.files if f.endswith('__dsm')][0]; dsm=d[k]
X0,X1,Y0,Y1,_=d['extent']; ny,nx=dsm.shape
E=json.load(open('data/tk/bohn_levels.json'))
P=Polygon(E['outer']).buffer(0); C=P.centroid; ANG=70.5
Pr=affinity.rotate(P,-ANG,origin=C)
def samp(x,y):
    i=np.floor(x-X0).astype(int); j=np.floor(y-Y0).astype(int); ok=(i>=0)&(i<nx)&(j>=0)&(j<ny)
    v=np.full(x.shape,np.nan); v[ok]=dsm[j[ok],i[ok]]; return v
s=0.5; bx0,by0,bx1,by1=Pr.bounds
us=np.arange(bx0,bx1,s)+s/2; vs=np.arange(by0,by1,s)+s/2; U,V=np.meshgrid(us,vs)
ca,sa=math.cos(math.radians(ANG)),math.sin(math.radians(ANG))
Xw=C.x+(U-C.x)*ca-(V-C.y)*sa; Yw=C.y+(U-C.x)*sa+(V-C.y)*ca
Z=samp(Xw,Yw)
TH=[('L1',138.0),('L2',145.0),('L3',155.0),('L4',163.0),('PH',168.0)]
out={'outer':E['outer'],'levels':[],'base_top':E['base_top'],'ground_med':E['ground_med'],'axis_deg':ANG}
prev=Pr
def ortho(p,tol=1.0,minlen=1.6):
    # snap a (rotated-frame) polygon to axis-parallel edges: simplify, classify edges H/V, merge runs, drop short jogs, intersect
    c=list(p.simplify(tol).exterior.coords)[:-1]
    for it in range(6):
        n=len(c); E=[]
        for i in range(n):
            a=c[i]; b=c[(i+1)%n]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
            if L<1e-6: continue
            h=abs(dx)>=abs(dy); E.append([h,(a[1]+b[1])/2 if h else (a[0]+b[0])/2,L])
        M=[]
        for e in E:
            if M and M[-1][0]==e[0]: w=M[-1][2]+e[2]; M[-1][1]=(M[-1][1]*M[-1][2]+e[1]*e[2])/w; M[-1][2]=w
            else: M.append(e)
        if len(M)>1 and M[0][0]==M[-1][0]: e=M.pop(); w=M[0][2]+e[2]; M[0][1]=(M[0][1]*M[0][2]+e[1]*e[2])/w; M[0][2]=w
        nc=[]
        for i in range(len(M)):
            a=M[i]; b=M[(i+1)%len(M)]
            if a[0]==b[0]: continue
            nc.append((b[1],a[1]) if a[0] else (a[1],b[1]))
        # drop shortest jog below minlen
        n=len(nc); Ls=[math.hypot(nc[(i+1)%n][0]-nc[i][0],nc[(i+1)%n][1]-nc[i][1]) for i in range(n)]
        c=nc
        if n>4 and min(Ls)<minlen:
            i=Ls.index(min(Ls)); c=[v for k,v in enumerate(nc) if k!=(i+1)%n]
        else: break
    q=Polygon(c).buffer(0)
    return q if q.area>0 else None
for n,(nm,t) in enumerate(TH):
    m=np.isfinite(Z)&(Z>=t)
    cells=[box(us[i]-s/2,vs[j]-s/2,us[i]+s/2,vs[j]+s/2) for j,i in zip(*np.nonzero(m))]
    if not cells: continue
    g=unary_union(cells).buffer(1.5,join_style=2).buffer(-3.0,join_style=2).buffer(1.5,join_style=2)
    g=g.intersection(prev.buffer(-0.15,join_style=2)).buffer(-0.6,join_style=2).buffer(0.6,join_style=2).simplify(0.05)
    polys=[ortho(p) for p in getattr(g,'geoms',[g]) if p.geom_type=='Polygon' and p.area>12]
    polys=[p.intersection(prev.buffer(-0.15,join_style=2)) for p in polys if p is not None]
    polys=[q for p in polys for q in getattr(p,'geoms',[p]) if q.geom_type=='Polygon' and q.area>12]
    if not polys: continue
    nt=[b for a,b in TH if b>t]; nt=nt[0] if nt else 999
    vals=[]
    for p in polys:
        mm=contains_xy(p.buffer(-0.5),U,V)&np.isfinite(Z); vv=Z[mm]; vv=vv[(vv>=t)&(vv<nt)]; vals.append(float(np.percentile(vv,70)) if len(vv) else t+1)
    W=[affinity.rotate(p,ANG,origin=C) for p in polys]
    out['levels'].append({'name':nm,'th':t,'polys':[[list(c) for c in p.exterior.coords[:-1]] for p in W],'tops':vals,'areas':[round(p.area,1) for p in W],'nverts':[len(p.exterior.coords)-1 for p in W]})
    print(nm,t,[round(p.area) for p in W],[len(p.exterior.coords)-1 for p in W],[round(x,2) for x in vals])
    prev=unary_union(polys)
json.dump(out,open('data/tl/bohn_levels_rect.json','w'))
from PIL import Image, ImageDraw
im=Image.new('RGB',(900,450),'white'); dr=ImageDraw.Draw(im); ox=[p[0] for p in E['outer']]; oy=[p[1] for p in E['outer']]
mx,my=min(ox)-3,min(oy)-3; sc=420/max(max(ox)-mx,max(oy)-my)
def T(p,off): return (off+(p[0]-mx)*sc, 440-(p[1]-my)*sc)
cols=['red','orange','green','blue','purple']
for off,LL in ((0,E['levels']),(450,out['levels'])):
    dr.polygon([T(p,off) for p in E['outer']],outline='black')
    for k,L in enumerate(LL):
        for p in L['polys']: dr.polygon([T(q,off) for q in p],outline=cols[k%5])
im.save('data/tl/levels_cmp.png')
