import json
from shapely.geometry import Polygon, box, MultiPolygon, mapping
from shapely.ops import unary_union
d=json.load(open('extract.json'))
def polys(fl):
  out=[]
  for f in fl:
    p=Polygon([(v[0],v[1]) for v in f['v']])
    if p.is_valid and p.area>1e-4: out.append(p)
    else: out.append(p.buffer(0))
  return out
walk=unary_union(polys(d['Footpaths_OSM']))
disc=unary_union(polys(d['COLE_add_forecourt_bu']))
U=unary_union([walk,disc]).buffer(0.05,join_style=2).buffer(-0.05,join_style=2)
U=U.buffer(-0.02).buffer(0.02)  # drop slivers
print('walk area',round(walk.area,1),'disc',round(disc.area,1),'union',round(U.area,1),'overlap',round(walk.intersection(disc).area,1), 'geoms', len(getattr(U,'geoms',[U])))
discz=disc.buffer(0.08)
sold=U.difference(U.buffer(-0.22)).intersection(discz)
band=U.buffer(-0.22).difference(U.buffer(-1.0)).intersection(discz)
band=band.buffer(-0.3,join_style=2).buffer(0.3,join_style=2).intersection(U.buffer(-0.22))
sold=sold.buffer(-0.06).buffer(0.06)
sold=sold.difference(sold.buffer(-0.05)).union(sold) if False else sold
conc=U.difference(sold).difference(band)
x0,y0,x1,y1=U.bounds
import math
pieces=[]
for mi,g in enumerate([conc,band,sold]):
  for ix in range(math.floor(x0),math.ceil(x1)):
    for iy in range(math.floor(y0),math.ceil(y1)):
      c=g.intersection(box(ix,iy,ix+1,iy+1))
      if c.is_empty: continue
      gs=getattr(c,'geoms',[c])
      for p in gs:
        if p.geom_type!='Polygon' or p.area<1e-4: continue
        pieces.append({'m':mi,'ext':list(p.exterior.coords)[:-1],'holes':[list(h.coords)[:-1] for h in p.interiors]})
json.dump({'pieces':pieces,'union':mapping(U),'deleted_faces':[f['i'] for f in d['Footpaths_OSM']]},open('pieces.json','w'))
print('pieces',len(pieces),'areas conc/band/sold',round(conc.area,1),round(band.area,1),round(sold.area,1))
