import xml.etree.ElementTree as ET
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937
t=Transformer.from_crs(4326,6527,always_xy=True)
r=ET.parse('data/msu_osm.xml').getroot()
N={}
for n in r.iter('node'):
    e,nn=t.transform(float(n.get('lon')),float(n.get('lat'))); N[n.get('id')]=((e-OE)*F,(nn-ON)*F)
for w in r.iter('way'):
    tags={k.get('k'):k.get('v') for k in w.iter('tag')}
    pts=[N[nd.get('ref')] for nd in w.iter('nd') if nd.get('ref') in N]
    if not pts or not tags: continue
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    if max(xs)<-125 or min(xs)>-30 or max(ys)<-300 or min(ys)>-190: continue
    keep={k:v for k,v in tags.items() if k in('building','name','highway','service','amenity','parking','building:levels','height','surface','landuse','leisure','barrier','footway')}
    print('W',w.get('id'),keep,'x %.1f..%.1f y %.1f..%.1f n%d'%(min(xs),max(xs),min(ys),max(ys),len(pts)))
