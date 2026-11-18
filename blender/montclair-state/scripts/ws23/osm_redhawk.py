import sys, json, xml.etree.ElementTree as ET
sys.path.insert(0,'/workspace/nj-scenes/blender_pylib_proj')
from pyproj import Transformer
FT=1200/3937; tr=Transformer.from_crs("EPSG:4326","EPSG:6527",always_xy=True)
c_e,c_n=tr.transform(-74.19720,40.86000); E0,N0=round(c_e,-1),round(c_n,-1)
def loc(lon,lat):
    e,n=tr.transform(lon,lat); return ((e-E0)*FT,(n-N0)*FT)
r=ET.parse('data/msu_osm.xml').getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.iter('node')}
out={}
for w in r.iter('way'):
    t={x.get('k'):x.get('v') for x in w.findall('tag')}
    nm=t.get('name','')
    if any(k in nm for k in ['Red Hawk','College Av','Normal Av','Carlisle']) or w.get('id') in ('232850521',):
        pts=[loc(*nodes[x.get('ref')]) for x in w.findall('nd') if x.get('ref') in nodes]
        out[w.get('id')]=dict(name=nm,tags=t,pts=[[round(a,1),round(b,1)] for a,b in pts])
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        print(w.get('id'),nm,t.get('highway',t.get('building','')),'x%.0f..%.0f y%.0f..%.0f'%(min(xs),max(xs),min(ys),max(ys)), t.get('sidewalk',''), t.get('lanes',''))
json.dump(out,open('data/ws23/osm_redhawk_ways.json','w'),indent=1)
