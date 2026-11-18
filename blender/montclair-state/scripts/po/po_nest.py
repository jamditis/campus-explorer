# po: clip each smoothed tier to the tier below (3 cm inset) so the nested prisms never poke out (UNVERIFIED).
import json,sys
from shapely.geometry import Polygon
from shapely.ops import unary_union
D=json.load(open(sys.argv[1])); P={}; Z={}
for t in D['tiers']: P.setdefault(t['k'],[]).append(Polygon(t['ext'],t['holes'])); Z[t['k']]=t['z']
U={k:unary_union(v) for k,v in P.items()}; ks=sorted(U); out=[]
for i,k in enumerate(ks):
    if i>0: U[k]=U[k].intersection(U[ks[i-1]].buffer(-0.03,join_style=2)).buffer(0).simplify(0.02)
    gs=[U[k]] if U[k].geom_type=='Polygon' else list(U[k].geoms)
    for g in gs:
        if g.geom_type!='Polygon' or g.area<20: continue
        out.append({'k':k,'z':Z[k],'ext':list(g.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in g.interiors],'area':g.area})
D['tiers']=out; json.dump(D,open(sys.argv[2],'w')); print('NESTED',[(t['k'],len(t['ext']),len(t['holes'])) for t in out])
