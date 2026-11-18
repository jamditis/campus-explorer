import json, math
from shapely.geometry import Point, Polygon, box, mapping
from shapely.ops import unary_union
from shapely import affinity
C=(-107.0,-50.5); R=9.5; ANG=-13.5  # gable axis rotation (deg) from TZ footprint + ortho gable band
a=math.radians(ANG); u=(math.cos(a),math.sin(a)); v=(-math.sin(a),math.cos(a))
F0=(-105.2,-62.3)  # gable face centre (TZ top edge midpoint)
d=(C[0]-F0[0])*v[0]+(C[1]-F0[1])*v[1]
def L(pu,pv): return (C[0]+pu*u[0]+pv*v[0], C[1]+pu*u[1]+pv*v[1])
circle=Point(C).buffer(R,resolution=64)
apron=Polygon([L(-R,0),L(R,0),L(R,-(d+1.2)),L(-R,-(d+1.2))])
U=unary_union([circle,apron])
# brick border ring: around the whole outline except where it runs inside the building
ring=U.difference(U.buffer(-0.6,join_style=2))
bld=Polygon([L(-R-2,-(d-0.3)),L(R+2,-(d-0.3)),L(R+2,-(d+5)),L(-R-2,-(d+5))])
ring=ring.difference(bld)
# quatrefoil inlay outline (4 lobes + centre square), aligned with the gable axis
lo=2.3; lr=1.95
Q=unary_union([Point(L(lo,0)).buffer(lr,64),Point(L(-lo,0)).buffer(lr,64),Point(L(0,lo)).buffer(lr,64),Point(L(0,-lo)).buffer(lr,64),
  Polygon([L(-lo,-lo),L(lo,-lo),L(lo,lo),L(-lo,lo)])])
qline=Q.difference(Q.buffer(-0.28))
dark=U.difference(ring).difference(qline)
x0,y0,x1,y1=U.bounds; pieces=[]
for mi,g in enumerate([dark,ring,qline]):
  for ix in range(math.floor(x0),math.ceil(x1)):
    for iy in range(math.floor(y0),math.ceil(y1)):
      c=g.intersection(box(ix,iy,ix+1,iy+1))
      if c.is_empty: continue
      for p in getattr(c,'geoms',[c]):
        if p.geom_type!='Polygon' or p.area<1e-4: continue
        pieces.append({'m':mi,'ext':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in p.interiors]})
json.dump({'pieces':pieces,'union':mapping(U),'C':C,'R':R,'ang':ANG,'u':u,'v':v,'d':d},open('pieces.json','w'))
print('d',round(d,2),'pieces',len(pieces),'areas',round(dark.area,1),round(ring.area,1),round(qline.area,1),'bounds',[round(b,1) for b in U.bounds])
