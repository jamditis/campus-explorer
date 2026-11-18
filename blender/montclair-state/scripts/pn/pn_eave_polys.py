import json, numpy as np
from shapely.geometry import Polygon, MultiPolygon
D=json.load(open('data/pn/polys.json')); th=D['th']; cx,cy=D['cx'],D['cy']; c,s=np.cos(th),np.sin(th)
from shapely.ops import unary_union
P={}
for t in D['tiers']: P.setdefault(t['k'],[]).append(Polygon(t['ext'],t['holes']))
P={k:unary_union(v) for k,v in P.items()}; Z={t['k']:t['z'] for t in D['tiers']}
OV=0.65; out=[]
for k in (3,4,5):
    ring=P[k].buffer(OV,join_style=2).difference(P[k].buffer(-0.08,join_style=2))
    if k+1 in P: ring=ring.difference(P[k+1].buffer(OV+0.2,join_style=2))
    ring=ring.buffer(-0.02).buffer(0.02)
    gs=[ring] if isinstance(ring,Polygon) else list(ring.geoms)
    for g in gs:
        if g.area<1.0 or g.is_empty: continue
        g=g.simplify(0.05)
        out.append({'k':k,'z':Z[k],'ext':list(g.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in g.interiors]})
json.dump(out,open('data/pn/eaves.json','w')); print('EAVES',len(out),[ (o['k'],len(o['ext']),len(o['holes'])) for o in out][:20])
