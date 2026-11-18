# tk: Bohn Hall level outlines from the 2017 1 m DSM (data/tj/bohn_grid_1m.npz) clipped to OSM 232853538. Read-only -> data/tk/bohn_levels.json
import numpy as np, json
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union
from shapely import contains_xy
d=np.load('data/tj/bohn_grid_1m.npz'); k=[f for f in d.files if f.endswith('__dsm')][0]; dsm=d[k]; dtm=d[k.replace('dsm','dtm')]
X0,X1,Y0,Y1,_=d['extent']; ny,nx=dsm.shape
P=Polygon(json.load(open('data/td/east_osm.json'))['ways']['232853538']['pts']).buffer(0)
TH=[('L1',138.0),('L2',145.0),('L3',155.0),('L4',163.0),('PH',168.0)]
out={'outer':[list(c) for c in P.exterior.coords[:-1]],'levels':[]}
inner=contains_xy(P.buffer(-0.6),*np.meshgrid(np.arange(nx)+X0+.5,np.arange(ny)+Y0+.5))
v=dsm[inner&np.isfinite(dsm)]; out['base_top']=float(np.percentile(v[v<138],75)) if (v<138).any() else 136.0
prev=P
for nm,t in TH:
    cells=[box(X0+i,Y0+j,X0+i+1,Y0+j+1) for j in range(ny) for i in range(nx) if np.isfinite(dsm[j,i]) and dsm[j,i]>=t]
    if not cells: continue
    g=unary_union(cells).buffer(1.2,join_style=2).buffer(-2.2,join_style=2).buffer(1.0,join_style=2).simplify(0.7).intersection(prev.buffer(-0.15,join_style=2)).buffer(-0.5,join_style=2).buffer(0.5,join_style=2).simplify(0.3)
    polys=[p for p in getattr(g,'geoms',[g]) if p.geom_type=='Polygon' and p.area>12]
    if not polys: continue
    vals=[]
    for p in polys:
        mm=contains_xy(p.buffer(-0.5),*np.meshgrid(np.arange(nx)+X0+.5,np.arange(ny)+Y0+.5))&np.isfinite(dsm)
        nt=dict(TH[1:]+[('x',999)]).get(nm,999); nt=[b for a,b in TH if b>t]; nt=nt[0] if nt else 999; vv=dsm[mm]; vv=vv[(vv>=t)&(vv<nt)]; vals.append(float(np.percentile(vv,70)) if len(vv) else t+1)
    out['levels'].append({'name':nm,'th':t,'polys':[[list(c) for c in p.exterior.coords[:-1]] for p in polys],'tops':vals,'areas':[round(p.area,1) for p in polys]})
    print(nm,t,[round(p.area) for p in polys],[round(x,2) for x in vals])
    prev=unary_union(polys)
out['ground_med']=float(np.nanmedian(dtm[contains_xy(P.buffer(5),*np.meshgrid(np.arange(nx)+X0+.5,np.arange(ny)+Y0+.5))&~inner]))
print('base_top',out['base_top'],'ground',out['ground_med'])
json.dump(out,open('data/tk/bohn_levels.json','w'))
