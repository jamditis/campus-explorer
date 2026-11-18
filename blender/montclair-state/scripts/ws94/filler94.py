import json,sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from shapely.geometry import Polygon,MultiPolygon
from shapely.ops import unary_union
import math
D=json.load(open('scripts/ws94/dump94.json'))
polys=[];pts=[]
for n,o in D.items():
    if n.startswith('WS77'): continue
    V=o['v']; pts+=V
    for f in o['f']:
        p=Polygon([(V[i][0],V[i][1]) for i in f])
        if p.is_valid and p.area>0: polys.append(p)
U=unary_union(polys)
isl=unary_union([Polygon([(o['v'][i][0],o['v'][i][1]) for i in f]) for n,o in D.items() if n.startswith('WS77') for f in o['f']]).buffer(0)
G=list(U.geoms) if hasattr(U,'geoms') else [U]
out=[]
for g in G:
    for r in g.interiors:
        h=Polygon(r)
        if h.area>20: continue  # the 81 m2 opening W is a real non-lot area, leave
        rest=h.difference(isl.buffer(-0.05)) if h.area>1 else h
        if rest.area<0.003: continue
        rest=rest.buffer(0.04,join_style=2).intersection(h.buffer(0.04,join_style=2))
        for q in (rest.geoms if hasattr(rest,'geoms') else [rest]):
            if q.area<0.003: continue
            q=q.simplify(0.01)
            out.append(list(q.exterior.coords)[:-1])
# z: IDW from nearest lot verts
import bisect
P=sorted(pts)
xs=[p[0] for p in P]
def zat(x,y):
    i=bisect.bisect_left(xs,x-1.0); j=bisect.bisect_right(xs,x+1.0)
    c=sorted(((p[0]-x)**2+(p[1]-y)**2,p[2]) for p in P[i:j])[:4]
    if not c: return None
    if c[0][0]<1e-8: return c[0][1]
    w=[1/d for d,_ in c]; return sum(wi*z for wi,(d,z) in zip(w,c))/sum(w)
F=[]
for ring in out:
    F.append([(x,y,zat(x,y)-0.006) for x,y in ring])
print("fillers",len(F),"area",round(sum(Polygon([(a,b) for a,b,c in r]).area for r in F),2))
json.dump(F,open('scripts/ws94/filler94.json','w'))
