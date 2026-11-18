# system python + shapely: find black/white outline faces that lie outside a uniform buffer of the red letter (fill errors)
import json, numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
D=json.load(open('data/sd/letters.json'))['faces']
front=[f for f in D if f['n'][0]<-0.9]
U=lambda m: unary_union([Polygon(f['uv']).buffer(0) for f in front if f['m']==m])
R,B,Wt=U(2),U(1),U(0)
parts=sorted(R.geoms,key=lambda g:g.bounds[0])
out={}
for k,g in enumerate(parts):
    box=g.buffer(0.25)
    b=B.intersection(box); w=Wt.intersection(box)
    bw=0.031; ww=0.020
    eb=b.difference(g.buffer(bw*1.6,join_style=1)); ew=w.difference(g.buffer(bw+ww*1.6,join_style=1))
    print(k,round(g.bounds[0],2),'bw',round(bw,3),'ww',round(ww,3),'excess black m2',round(eb.area,4),'excess white m2',round(ew.area,4))
    out[k]=dict(bw=bw,ww=ww,u0=g.bounds[0],u1=g.bounds[2],eb=eb.area,ew=ew.area)
# per-face flags: faces of all orientations whose centroid (2D) lies in excess region of a letter
flag=[]
for k,g in enumerate(parts):
    o=out[k]
    if o['eb']<0.004 and o['ew']<0.004: continue
    gb=g.buffer(o['bw']*1.6,join_style=1); gw=g.buffer(o['bw']+o['ww']*1.6,join_style=1)
    for f in D:
        if f['m'] not in (0,1): continue
        P=Polygon(f['uv']) if abs(f['n'][0])>0.9 else None
        c=np.mean(np.array(f['uv']),axis=0)
        if not (o['u0']-0.3<c[0]<o['u1']+0.3): continue
        from shapely.geometry import Point
        lim = gb if f['m']==1 else gw
        if P is not None and P.area>1e-6:
            fr=P.difference(lim).area/P.area
            if fr>0.5: flag.append(f['i'])
        else:
            if not lim.contains(Point(c)): flag.append(f['i'])
print('FLAGGED',len(flag))
json.dump(dict(flag=flag,stats=out),open('data/sd/letters_flag.json','w'))
