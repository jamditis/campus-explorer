# po: gutter runs along the outer edges of the pn/po tier eaves + downpipe xy (under the eave, 0.2 m off the wall). UNVERIFIED.
import json, numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
D=json.load(open('data/pq/polys.json')); E=json.load(open('data/pq/eaves.json'))
P={}
for t in D['tiers']: P.setdefault(t['k'],[]).append(Polygon(t['ext'],t['holes']))
P={k:unary_union(v) for k,v in P.items()}
G=[];DP=[]
for e in E:
    k=e['k']; z=e['z']; R=e['ext']; n=len(R)
    for i in range(n):
        a=np.array(R[i]); b=np.array(R[(i+1)%n]); L=np.linalg.norm(b-a)
        if L<0.8: continue
        m=(a+b)/2
        if P[k].distance(Point(m))<0.5: continue
        G.append({'a':a.tolist(),'b':b.tolist(),'z':z})
        if L<5: continue
        u=(b-a)/L; nrm=np.array([-u[1],u[0]])
        if P[k].distance(Point(m+nrm*0.45))>P[k].distance(Point(m-nrm*0.45)): nrm=-nrm   # point inward (toward the wall)
        ts=[L-0.9]+[t for t in np.arange(18,L-6,18)]
        for t in ts:
            q=a+u*t; p=q+nrm*0.45; d=P[k].distance(Point(p))
            if 0.08<d<0.4 and all(np.hypot(p[0]-x,p[1]-y)>3 for x,y,_,_,_ in DP): DP.append((float(p[0]),float(p[1]),z,float(q[0]),float(q[1])))
json.dump({'g':G,'dp':DP},open('data/pq/gutters.json','w')); print('GUTTER segs',len(G),'len',round(sum(np.hypot(g['b'][0]-g['a'][0],g['b'][1]-g['a'][1]) for g in G)),'downpipes',len(DP))
