import xml.etree.ElementTree as ET, json
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937
tr=Transformer.from_crs(4326,6527,always_xy=True)
r=ET.parse('data/msu_osm.xml').getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.iter('node')}
ways={w.get('id'):w for w in r.iter('way')}
def xy(nid):
    e,n=tr.transform(*nodes[nid]); return ((e-OE)*F,(n-ON)*F)
out={}
for w in r.iter('way'):
    if w.get('id')=='315835594':
        out['tags']={t.get('k'):t.get('v') for t in w.iter('tag')}
        out['ring']=[xy(nd.get('ref')) for nd in w.iter('nd') if nd.get('ref') in nodes]
for rel in r.iter('relation'):
    for m in rel.iter('member'):
        if m.get('ref')=='315835594': out.setdefault('rels',[]).append(rel.get('id'))
# also any other wood/scrub ways near ravine
near=[]
for w in r.iter('way'):
    t={x.get('k'):x.get('v') for x in w.iter('tag')}
    if t.get('natural') in ('wood','scrub') or t.get('landuse')=='forest':
        pts=[xy(nd.get('ref')) for nd in w.iter('nd') if nd.get('ref') in nodes]
        if pts and any(150<p[0]<320 and 250<p[1]<360 for p in pts): near.append((w.get('id'),t,len(pts)))
out['near']=near
r2=out.get('ring',[])
if r2:
    xs=[p[0] for p in r2]; ys=[p[1] for p in r2]; out['bbox']=[min(xs),max(xs),min(ys),max(ys)]
json.dump(out,open('data/wk/wood.json','w'))
print(out.get('tags'),out.get('bbox'),len(r2),out.get('rels'),near)
