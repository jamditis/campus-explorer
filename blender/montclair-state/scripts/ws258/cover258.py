# ws258: which Footpaths_OSM faces (base mesh XY) in the Chapin W plaza box sit under designed WS116-WS126 paving/beds/stairs (UNIFY #2 residue)
import json
from shapely.geometry import Polygon
from shapely.ops import unary_union
d=json.load(open('probe258a.json'))
BOX=(-232,-205,-208,-178)
DES=('WS116_','WS117_','WS119_','WS120_','WS124_','WS126_','WS115_','WS105_Chapin_E_bank_planting','WS127_','WS103_','WS102_')
des=[]
for o in d:
    if o['name'].startswith(DES) and not o['hide_render']:
        for p in o['polys']:
            g=Polygon([(v[0],v[1]) for v in p]).buffer(0)
            if g.area>1e-4: des.append(g)
U=unary_union(des)
fp=[o for o in d if o['name']=='Footpaths_OSM'][0]
res=[];tot=0;cov=0
for p in fp['polys']:
    cx=sum(v[0] for v in p)/len(p); cy=sum(v[1] for v in p)/len(p)
    if not(BOX[0]<cx<BOX[1] and BOX[2]<cy<BOX[3]): continue
    g=Polygon([(v[0],v[1]) for v in p]).buffer(0); a=g.area; c=g.intersection(U).area/a if a>0 else 1
    tot+=a; cov+=a*c
    res.append({'c':[round(cx,2),round(cy,2)],'area':round(a,3),'covered':round(c,3),'zmin':min(v[2] for v in p),'zmax':max(v[2] for v in p)})
print('faces',len(res),'area %.1f m2 covered %.1f%%'%(tot,100*cov/tot))
import collections
print('coverage histogram',collections.Counter(round(r['covered'],1) for r in res))
for r in res:
    if r['covered']<0.95: print('UNCOVERED',r)
json.dump(res,open('cover258.json','w'),indent=0)
