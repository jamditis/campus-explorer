import json,sys,bisect
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
D=json.load(open('scripts/ws96/dump96.json')); G96=json.load(open('scripts/ws96/gap96b.json'))
lot=[k for k in D if k.startswith(('WS75','WS76','WS79','WS80','WS94'))]
polys=[];pts=[]
for n in lot:
    V=D[n]['v']; pts+=V
    for f in D[n]['f']:
        p=Polygon([(V[i][0],V[i][1]) for i in f]).buffer(0)
        if p.area>0: polys.append(p)
for r in G96['fill']:
    p=Polygon([(a,b) for a,b,c in r]).buffer(0)
    if p.area>0: polys.append(p)
U=unary_union(polys)
isl=unary_union([Polygon([(D[n]['v'][i][0],D[n]['v'][i][1]) for i in f]).buffer(0) for n in D if n.startswith('WS77') for f in D[n]['f']])
W=box(-226,-102,-210,-74)
P=sorted(pts); xs=[p[0] for p in P]
def zat(x,y):
    i=bisect.bisect_left(xs,x-1.5); j=bisect.bisect_right(xs,x+1.5)
    c=sorted(((p[0]-x)**2+(p[1]-y)**2,p[2]) for p in P[i:j])[:4]
    if not c: return None
    if c[0][0]<1e-8: return c[0][1]
    w=[1/d for d,_ in c]; return sum(wi*z for wi,(d,z) in zip(w,c))/sum(w)
B=U.boundary
T=D['Terrain_LiDAR_DTM_1m']; low=dict((i,d) for i,d in G96['low'])
raise_=[]; skipped=0
for k,(x,y,z) in enumerate(T['v']):
    idx=T['idx'][k]; pt=Point(x,y)
    if idx in low or not W.contains(pt) or U.contains(pt) or isl.buffer(0.5).contains(pt): continue
    d=B.distance(pt)
    if d>1.6: continue
    q=B.interpolate(B.project(pt)); ze=zat(q.x,q.y)
    if ze is None: continue
    tgt=ze-0.012-0.12*d
    dz=tgt-z
    if dz<=0.005: continue
    if dz>0.40: skipped+=1; continue
    raise_.append((idx,round(dz,3)))
print("E97 raise",len(raise_),"max",max([d for _,d in raise_],default=0),"skipped>0.4",skipped)
json.dump({'raise':raise_},open('scripts/ws97/edge97.json','w'))
