import sys; sys.path.insert(0,'/workspace/nj-scenes/pylib_proj_wq2')
import xml.etree.ElementTree as ET, json
from pyproj import Transformer
sd=json.load(open('data/scene_data.json'))
T=Transformer.from_crs('EPSG:4326','EPSG:6527',always_xy=True); F=1200/3937
r=ET.parse('data/msu_osm.xml').getroot(); nd={}
for n in r.iter('node'):
    e,nn=T.transform(float(n.get('lon')),float(n.get('lat'))); nd[n.get('id')]=((e-sd['E0_ftUS'])*F,(nn-sd['N0_ftUS'])*F,{t.get('k'):t.get('v') for t in n.iter('tag')})
B=lambda x,y:-262<x<-170 and -290<y<-140
for i,(x,y,t) in nd.items():
    if t and B(x,y): print('N',i,round(x,1),round(y,1),t)
out={}
for w in r.iter('way'):
    pts=[nd[q.get('ref')][:2] for q in w.iter('nd') if q.get('ref') in nd]
    if any(B(x,y) for x,y in pts):
        t={k.get('k'):k.get('v') for k in w.iter('tag')}; out[w.get('id')]=dict(t=t,p=pts)
        print('W',w.get('id'),t,[(round(x,1),round(y,1)) for x,y in pts][:10])
json.dump(out,open('scripts/ws102/osm102.json','w'))
