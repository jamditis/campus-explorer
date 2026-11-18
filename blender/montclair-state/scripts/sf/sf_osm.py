# sf: extract Lot 38 / Quad Road / parking aisles from data/msu_osm.xml into local m via an affine fit on ways present in scene_data.json
import json, numpy as np, xml.etree.ElementTree as ET
t=ET.parse('data/msu_osm.xml').getroot()
nodes={n.get('id'):(float(n.get('lat')),float(n.get('lon'))) for n in t.iter('node')}
ways={w.get('id'):([nd.get('ref') for nd in w.iter('nd')],{tg.get('k'):tg.get('v') for tg in w.iter('tag')}) for w in t.iter('way')}
sd={e['id']:e for e in json.load(open('data/scene_data.json'))['features']}
A=[];B=[]
for wid in ['313026743','313027434','313027428','313027436','313027423','313027429']:
    if wid in ways and wid in sd:
        refs=ways[wid][0]; pts=sd[wid]['pts']
        if len(refs)==len(pts):
            for r,p in zip(refs,pts):
                la,lo=nodes[r]; A.append([lo,la,1]); B.append(p)
A=np.array(A);B=np.array(B); M,res,_,_=np.linalg.lstsq(A,B,rcond=None)
err=np.abs(A@M-B).max(); print('fit pts',len(A),'max err m',round(err,3))
out={}
for wid,(refs,tags) in ways.items():
    if not all(r in nodes for r in refs): continue
    P=np.array([[nodes[r][1],nodes[r][0],1] for r in refs])@M
    if ((P[:,0]>-60)&(P[:,0]<110)&(P[:,1]>320)&(P[:,1]<420)).any() and (tags.get('highway') in('service','footway','pedestrian') or tags.get('amenity')=='parking' or tags.get('leisure') or tags.get('landuse') or tags.get('barrier')):
        out[wid]={'tags':tags,'pts':np.round(P,2).tolist()}
        print(wid,{k:v for k,v in tags.items() if k in('highway','amenity','name','service','leisure','landuse','barrier')},len(refs),[tuple(x) for x in np.round(P,1).tolist()][:12])
json.dump({'source':'data/msu_osm.xml, affine lat/lon->local fit (sf)','fit_max_err_m':float(err),'ways':out},open('data/sf/north_lot_osm.json','w'))
