import json,sys,bisect
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
D=json.load(open('scripts/ws96/dump96.json'))
lot=[k for k in D if k.startswith(('WS75','WS76','WS79','WS80','WS94'))]
polys=[];pts=[]
for n in lot:
    V=D[n]['v']; pts+=V
    for f in D[n]['f']:
        p=Polygon([(V[i][0],V[i][1]) for i in f]).buffer(0)
        if p.area>0: polys.append(p)
U=unary_union(polys)
isl=unary_union([Polygon([(D[n]['v'][i][0],D[n]['v'][i][1]) for i in f]).buffer(0) for n in D if n.startswith('WS77') for f in D[n]['f']])
W=box(-226,-102,-210,-74)   # E-end window
Uc=U.buffer(0.6,join_style=1).buffer(-0.6,join_style=1)   # closing: fills notches/gaps <1.2 m
Us=Uc.simplify(0.15)            # straighten wobble
gap=Us.difference(U).difference(isl.buffer(0.02)).intersection(W)
G=[g for g in (gap.geoms if hasattr(gap,'geoms') else [gap]) if g.area>0.002]
P=sorted(pts); xs=[p[0] for p in P]
def zat(x,y):
    i=bisect.bisect_left(xs,x-1.5); j=bisect.bisect_right(xs,x+1.5)
    c=sorted(((p[0]-x)**2+(p[1]-y)**2,p[2]) for p in P[i:j])[:4]
    if c[0][0]<1e-8: return c[0][1]
    w=[1/d for d,_ in c]; return sum(wi*z for wi,(d,z) in zip(w,c))/sum(w)
out=[]
for g in G:
    g=g.buffer(0.03,join_style=2).intersection(Us)  # tuck 3 cm under sheet edges
    for q in (g.geoms if hasattr(g,'geoms') else [g]):
        if q.geom_type!='Polygon' or q.area<0.002: continue
        q=q.simplify(0.01)
        out.append([(x,y,zat(x,y)-0.006) for x,y in list(q.exterior.coords)[:-1]])
print("G96 gaps",len(out),"area",round(sum(Polygon([(a,b) for a,b,c in r]).area for r in out),2))
# terrain verts poking through: inside Us shrunk 0.15 m, terrain z > lot z - 0.03
T=D['Terrain_LiDAR_DTM_1m']; inner=Us.buffer(-0.15).intersection(W.buffer(1))
low=[]
for k,(x,y,z) in enumerate(T['v']):
    if inner.contains(Point(x,y)):
        zl=zat(x,y)
        if z>zl-0.03: low.append((T['idx'][k],round(zl-0.04-z,3)))
print("G96 terrain lower",len(low),"max",min([d for _,d in low],default=0))
json.dump({'fill':out,'low':low},open('scripts/ws96/gap96.json','w'))
