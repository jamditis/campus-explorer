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
    if any(-252<x<-212 and -258<y<-228 for x,y in pts):
        print(w.get('id'),{k:v for k,v in tags.items() if k in('highway','service','name','amenity','surface','footway','parking','landuse','leisure','barrier','building','area','kerb')},[(round(x,1),round(y,1)) for x,y in pts if -260<x<-205 and -265<y<-220][:14])
