# ti staging: roof-level polygons for Stone Hall + Blanton Hall from the 2017 1 m DSM inside the OSM footprints (numpy/shapely). Read-only on scene.
import numpy as np, json
from shapely.geometry import Polygon, box, MultiPolygon
from shapely.ops import unary_union
from shapely import contains_xy
from scipy import ndimage
G=np.load('north/data/grid_1m.npz'); X0,X1,Y0,Y1,R=[float(v) for v in G['extent']]; d=G['dsm']; t=G['dtm_filled']
W=json.load(open('data/td/east_osm.json'))['ways']
ys,xs=np.mgrid[0:d.shape[0],0:d.shape[1]]; CX,CY=xs*R+X0+R/2, ys*R+Y0+R/2
CFG={'313028565':('Stone Hall',141.5),'313029108':('Blanton Hall',152.6)}
out={}
for wid,(nm,thr) in CFG.items():
    P=Polygon(W[wid]['pts']).buffer(0); m=contains_xy(P,CX,CY); v=d[m]
    hi=m&(d>thr); hi=ndimage.binary_opening(hi,iterations=2); hi=ndimage.binary_closing(hi,iterations=2)&m
    lo_v=d[m&(d<=thr)]; hi_v=d[hi]
    lab,n=ndimage.label(hi); polys=[]
    for i in range(1,n+1):
        c=lab==i
        if c.sum()<40: continue
        u=unary_union([box(x-.5,y-.5,x+.5,y+.5) for x,y in zip(CX[c],CY[c])]).simplify(2.0).intersection(P.buffer(-0.4))
        for g in (u.geoms if hasattr(u,'geoms') else [u]):
            if g.geom_type=='Polygon' and g.area>40: polys.append([list(map(lambda q:round(q,2),p)) for p in g.exterior.coords[:-1]])
    ring=t[contains_xy(P.buffer(4),CX,CY)&~contains_xy(P.buffer(0.5),CX,CY)]
    rec=dict(name=nm,outer=[list(p) for p in P.exterior.coords[:-1]],lo_top=round(float(np.nanpercentile(lo_v,60)),2) if len(lo_v) else None,
             hi_top=round(float(np.nanpercentile(hi_v,60)),2) if len(hi_v) else None,hi_polys=polys,ground_min=round(float(np.nanmin(ring)),2),ground_med=round(float(np.nanmedian(ring)),2),
             frac_hi=round(float(hi.sum()/m.sum()),2))
    print(wid,{k:(v if k not in('outer','hi_polys') else len(v)) for k,v in rec.items()}, [len(p) for p in polys])
    out[wid]=rec
out['_src']='2017 NJ LiDAR 1 m DSM/DTM (north/data/grid_1m.npz) + OSM footprints (ODbL) via data/td/east_osm.json; levels split at a DSM threshold, opened/closed 2 cells, simplified 2.0 m'
json.dump(out,open('data/ti/east_levels.json','w'),indent=1)
