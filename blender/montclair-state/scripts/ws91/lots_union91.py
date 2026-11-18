# ws91b: lot edges straightened on the UNION outline (so coincident/stacked sheet edges move together; covered edges stay put)
import json,sys,math
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313'); sys.path.insert(0,'scripts/ws91')
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union,nearest_points
from straight91 import loops_of
D=json.load(open('scripts/ws91/dump91.json'))
LOTS=[n for n in D if n.startswith(('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill'))]
TOL=float(sys.argv[1]) if len(sys.argv)>1 else 0.3; CL=0.35
polys=[]
for n in LOTS:
    V=D[n]['v']
    for f in D[n]['f']:
        polys.append(Polygon([(V[i][0],V[i][1]) for i in f]).buffer(0.003))
U=unary_union(polys)
geoms=list(U.geoms) if hasattr(U,'geoms') else [U]
S=[g.simplify(TOL,preserve_topology=True) for g in geoms]
rings=[]
for g in S:
    if g.area>=2: rings.append(LineString(g.exterior.coords))
    pass  # ws91c: holes (island cut-outs) left untouched so the asphalt keeps meeting the WS77 island curb foot
from shapely.strtree import STRtree
tree=STRtree(rings); Ub=U.boundary
out={}; stat={}
for n in LOTS:
    V=D[n]['v']; d={}
    for L in loops_of(D[n]['f']):
        for i in L:
            p=Point(V[i][0],V[i][1])
            if Ub.distance(p)>0.02: continue   # covered by another sheet -> leave
            r=rings[tree.nearest(p)]
            if r.distance(p)>0.4: continue
            q=r.interpolate(r.project(p))
            dx,dy=q.x-p.x,q.y-p.y; m=math.hypot(dx,dy)
            if m>CL: dx,dy=dx*CL/m,dy*CL/m
            if m>0.002: d[i]=(dx,dy)
    out[n]=d; stat[n]=(len(d),round(max([math.hypot(*v) for v in d.values()] or [0]),3))
json.dump(out,open('scripts/ws91/lots_disp91.json','w')); print(stat, 'rings',len(rings),[len(r.coords) for r in rings][:10])
