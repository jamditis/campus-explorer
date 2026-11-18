# system python + shapely 2.2: clean black (red+3.1 cm, round joins) and white (red+5.1 cm) outline regions for the
# letters whose outline fill errors closed the notches (N of COUNTRY = part 3, W of HAWK = part 8). Writes triangles.
import json, numpy as np, shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
D=json.load(open('data/sd/letters.json'))['faces']
front=[f for f in D if f['n'][0]<-0.9]; back=[f for f in D if f['n'][0]>0.9]
R=unary_union([Polygon(f['uv']).buffer(0) for f in front if f['m']==2])
parts=sorted(R.geoms,key=lambda g:g.bounds[0])
# per-layer depth planes x = a + b*u from vertex samples
def plane(fs,m):
    U=[];X=[]
    for f in fs:
        if f['m']!=m: continue
        for (u,z),x in zip(f['uv'],f['d']): U.append(u);X.append(x)
    b,a=np.polyfit(U,X,1); return float(a),float(b)
P={m:dict(front=plane(front,m),back=plane(back,m)) for m in (0,1)}
out=dict(planes=P,letters=[])
for k in (3,8):
    g=parts[k]
    lay={}
    for m,w in ((1,0.031),(0,0.051)):
        poly=g.buffer(w,join_style='round',quad_segs=6).simplify(0.002)
        tris=shapely.constrained_delaunay_triangles(poly)
        T=[list(t.exterior.coords)[:3] for t in tris.geoms]
        rings=[list(poly.exterior.coords)]+[list(r.coords) for r in poly.interiors]
        lay[m]=dict(tris=T,rings=rings,area=poly.area)
        print(k,m,'tris',len(T),'rings',len(rings),'area',round(poly.area,4))
    out['letters'].append(dict(k=k,u0=g.bounds[0]-0.12,u1=g.bounds[2]+0.12,layers=lay))
json.dump(out,open('data/sd/letters_rebuild.json','w')); print('planes',P)
