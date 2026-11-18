# tp: shaft footprints from data/tp/bohn_excess.json (system python, shapely) -> data/tp/shafts.json
import json
from shapely.geometry import Polygon, MultiPoint, box
from shapely import affinity
D='/workspace/nj-scenes/montclair-state/'
EX=json.load(open(D+'data/tp/bohn_excess.json')); E=json.load(open(D+'data/tl/bohn_levels_rect.json'))
ANG=E['axis_deg']; GROUND=E['ground_med']
levels=[(Polygon(p).buffer(0),t,L['name']) for L in E['levels'] for p,t in zip(L['polys'],L['tops'])]
out=[]
for k,e in enumerate(EX):
    excess=e['dsm_med']-e['model_top']
    if not (1.8<=excess<=4.0 and e['n']>=10): continue
    mp=MultiPoint(e['cells']); c=mp.centroid
    x0,y0,x1,y1=affinity.rotate(mp,-ANG,origin=c).bounds
    r=affinity.rotate(box(x0-0.5,y0-0.5,x1+0.5,y1+0.5),ANG,origin=c)
    lv=[(P,t,n) for P,t,n in levels if abs(t-e['model_top'])<0.3 and P.intersects(r)]
    if not lv: continue
    P,t,lname=max(lv,key=lambda a:a[0].intersection(r).area)
    fp=r.intersection(P.buffer(0.12,join_style=2))
    if fp.geom_type!='Polygon' or fp.area<4: continue
    fp=fp.simplify(0.05)
    if not fp.exterior.is_ccw: fp=Polygon(list(fp.exterior.coords)[::-1])
    edge=fp.difference(P.buffer(-0.6,join_style=2)).area>0.5 and fp.area<=40   # big ones = roof plant penthouse, not a shaft to grade
    cap=fp.buffer(0.03,join_style=2)
    if not cap.exterior.is_ccw: cap=Polygon(list(cap.exterior.coords)[::-1])
    out.append(dict(k=k,level=lname,top=round(e['dsm_med'],2),bot=round((GROUND-1.0) if edge else (t-0.3),2),edge=bool(edge),area=round(fp.area,1),
        fp=[list(p) for p in list(fp.exterior.coords)[:-1]],cap=[list(p) for p in list(cap.exterior.coords)[:-1]]))
for o in out: print({k:v for k,v in o.items() if k not in('fp','cap')})
json.dump(out,open(D+'data/tp/shafts.json','w'))
