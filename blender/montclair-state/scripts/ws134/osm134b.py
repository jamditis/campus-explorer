import xml.etree.ElementTree as ET, json
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937
t=Transformer.from_crs(4326,6527,always_xy=True)
r=ET.parse('data/msu_osm.xml').getroot()
N={}
for n in r.iter('node'):
    e,nn=t.transform(float(n.get('lon')),float(n.get('lat'))); N[n.get('id')]=((e-OE)*F,(nn-ON)*F)
out={}
for w in r.iter('way'):
    if w.get('id') in ('312845860','312845862','232846698','312845863','312845871','312845877','312845878','232846662'):
        out[w.get('id')]=[N[nd.get('ref')] for nd in w.iter('nd')]
json.dump(out,open('scripts/ws134/osm134.json','w'))
for k,v in out.items(): print(k,[(round(a,1),round(b,1)) for a,b in v])
