import json,sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from shapely.geometry import Polygon
from shapely.ops import unary_union
D=json.load(open('scripts/ws94/dump94.json'))
polys=[]
for n,o in D.items():
    if n.startswith('WS77'): continue
    V=o['v']
    for f in o['f']:
        p=Polygon([(V[i][0],V[i][1]) for i in f])
        if p.is_valid and p.area>0: polys.append(p)
U=unary_union(polys)
G=list(U.geoms) if hasattr(U,'geoms') else [U]
print("parts",len(G),[round(g.area,1) for g in G])
isl=[]
for n,o in D.items():
    if n.startswith('WS77'):
        V=o['v']; isl=unary_union([Polygon([(V[i][0],V[i][1]) for i in f]) for f in o['f']])
H=[]
for g in G:
    for r in g.interiors:
        h=Polygon(r)
        cov=h.intersection(isl).area/h.area if h.area else 0
        H.append((h.area,cov,h.centroid.x,h.centroid.y,h.bounds))
H.sort(reverse=True)
print("holes",len(H))
for h in H[:40]: print([round(x,3) if isinstance(x,float) else [round(b,1) for b in x] for x in h])
json.dump([list(Polygon(r).exterior.coords) for g in G for r in g.interiors],open('scripts/ws94/holes94.json','w'))
