import sys, json, numpy as np
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from scipy.spatial import Delaunay
d=json.load(open('scripts/ws99/bedctx99.json'))
occ=[]
for n,F in d.items():
    if n.startswith(('Footpaths','WS98','WS77','WS75','WS80','WS79','WS76','WS27')):
        for f in F:
            p=Polygon([(q[0],q[1]) for q in f])
            if p.is_valid and p.area>1e-5: occ.append(p)
O=unary_union(occ).buffer(0.02)
gen=Polygon([(-216.4,-88.45),(-206.9,-88.45),(-206.3,-89.5),(-206.3,-92.0),(-212.6,-95.5),(-212.6,-90.2),(-216.4,-90.2)])
bed=gen.difference(O)
if bed.geom_type=='MultiPolygon': bed=max(bed.geoms,key=lambda g:g.area)
bed=bed.buffer(-0.25,join_style=1).buffer(0.25,join_style=1).simplify(0.04)
bed=bed.buffer(0.15,join_style=1).buffer(-0.15,join_style=1).simplify(0.03)
ext=list(bed.exterior.coords)[:-1]
B=[]
for i in range(len(ext)):
    a=np.array(ext[i]); b=np.array(ext[(i+1)%len(ext)]); L=np.linalg.norm(b-a); k=max(1,int(L/0.25))
    for t in range(k): B.append(a+(b-a)*t/k)
B=np.array(B); inner=bed.buffer(-0.12)
gx,gy=np.meshgrid(np.arange(bed.bounds[0],bed.bounds[2],0.3),np.arange(bed.bounds[1],bed.bounds[3],0.3))
I=[(x,y) for x,y in zip(gx.ravel(),gy.ravel()) if inner.contains(Point(x,y))]
P=np.vstack([B,np.array(I)])
tri=Delaunay(P); T=[list(map(int,t)) for t in tri.simplices if bed.buffer(0.01).contains(Point(P[t].mean(0)))]
sh=[(-216.0,-88.95,1.4),(-215.2,-89.0,1.6),(-214.2,-89.0,1.6),(-211.7,-88.9,1.2),(-209.35,-89.0,1.7),(-207.3,-89.2,1.5),(-210.7,-91.8,1.3),(-211.95,-92.1,1.4),(-209.3,-91.6,1.6)]
ok=[s for s in sh if bed.buffer(-0.2).contains(Point(s[0],s[1]))]
print('area %.2f verts %d tris %d shrubs %d/%d'%(bed.area,len(P),len(T),len(ok),len(sh)), [s for s in sh if s not in ok])
json.dump({'poly':[list(map(float,p)) for p in ext],'P':P.tolist(),'T':T,'shrubs':ok},open('scripts/ws99/bed99.json','w'))
