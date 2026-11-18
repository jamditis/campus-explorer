import xml.etree.ElementTree as ET
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937
t=Transformer.from_crs(4326,6527,always_xy=True)
r=ET.parse('data/msu_osm.xml').getroot()
N={}
for n in r.iter('node'):
    e,nn=t.transform(float(n.get('lon')),float(n.get('lat'))); N[n.get('id')]=((e-OE)*F,(nn-ON)*F)
W={w.get('id'):[N[nd.get('ref')] for nd in w.iter('nd') if nd.get('ref') in N] for w in r.iter('way')}
for rel in r.iter('relation'):
    tags={k.get('k'):k.get('v') for k in rel.iter('tag')}
    if 'building' not in tags and 'name' not in tags: continue
    pts=[p for m in rel.iter('member') if m.get('type')=='way' for p in W.get(m.get('ref'),[])]
    if not pts: continue
    cx=sum(p[0] for p in pts)/len(pts); cy=sum(p[1] for p in pts)/len(pts)
    if -300<cx<-50 and -350<cy<-150:
        print('REL',rel.get('id'),tags.get('name'),tags.get('building'),tags.get('building:levels'),round(cx,1),round(cy,1),'x',round(min(p[0] for p in pts),1),round(max(p[0] for p in pts),1),'y',round(min(p[1] for p in pts),1),round(max(p[1] for p in pts),1))
