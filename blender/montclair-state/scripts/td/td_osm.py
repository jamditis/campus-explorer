# td: OSM ways east of the Student Center along Quad Road (x 80..260, y 250..470), same affine fit as sf
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
            for r,p in zip(refs,pts): la,lo=nodes[r]; A.append([lo,la,1]); B.append(p)
A=np.array(A);B=np.array(B); M=np.linalg.lstsq(A,B,rcond=None)[0]
out={}
for wid,(refs,tags) in ways.items():
    if not all(r in nodes for r in refs) or not tags: continue
    P=np.array([[nodes[r][1],nodes[r][0],1] for r in refs])@M
    if ((P[:,0]>80)&(P[:,0]<260)&(P[:,1]>250)&(P[:,1]<470)).any():
        out[wid]={'tags':tags,'pts':np.round(P,2).tolist()}
        print(wid,{k:v for k,v in tags.items() if k in('highway','amenity','name','building','leisure','landuse','barrier','natural','surface','service','layer','tunnel')},len(refs),'x',round(P[:,0].min()),round(P[:,0].max()),'y',round(P[:,1].min()),round(P[:,1].max()))
json.dump({'source':'data/msu_osm.xml, affine fit (td, same as sf)','ways':out},open('data/td/east_osm.json','w'))
