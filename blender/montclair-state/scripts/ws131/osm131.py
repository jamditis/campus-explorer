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
    if any(-202<x<-160 and -268<y<-215 for x,y in pts):
        print(w.get('id'),{k:v for k,v in tags.items() if k in('highway','service','name','amenity','surface','footway','parking','landuse','leisure','barrier','building','area','kerb')},[(round(x,1),round(y,1)) for x,y in pts if -215<x<-150 and -275<y<-205][:16])
