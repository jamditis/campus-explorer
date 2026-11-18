import json,sys
from shapely.geometry import Polygon
from shapely.ops import unary_union
for f in sys.argv[1:]:
    D=json.load(open(f)); P={}
    for t in D['tiers']: P.setdefault(t['k'],[]).append(Polygon(t['ext'],t['holes']))
    tot=sum(len(t['ext'])+sum(len(h) for h in t['holes']) for t in D['tiers'])
    U={k:unary_union(v) for k,v in P.items()}
    pokes=[round(U[k+1].difference(U[k]).area,2) for k in sorted(U) if k+1 in U]
    print(f,'verts',tot,'tiers',len(D['tiers']),'areas',[round(U[k].area) for k in sorted(U)],'poke-out m2',pokes)
