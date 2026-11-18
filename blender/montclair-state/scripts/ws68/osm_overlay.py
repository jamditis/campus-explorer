import sys, xml.etree.ElementTree as ET
sys.path.insert(0,'/workspace/nj-scenes/blender_pylib_proj')
from pyproj import Transformer
from PIL import Image, ImageDraw
FT=1200/3937; tr=Transformer.from_crs("EPSG:4326","EPSG:6527",always_xy=True)
c_e,c_n=tr.transform(-74.19720,40.86000); E0,N0=round(c_e,-1),round(c_n,-1)
def loc(lon,lat):
    e,n=tr.transform(lon,lat); return ((e-E0)*FT,(n-N0)*FT)
cx,cy,S=-290,-40,200
def px(p): return ((p[0]-cx)/S*1000+500, 500-(p[1]-cy)/S*1000)
r=ET.parse('data/msu_osm.xml').getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.iter('node')}
im=Image.open(sys.argv[1]).convert('RGB'); d=ImageDraw.Draw(im)
for w in r.iter('way'):
    t={x.get('k'):x.get('v') for x in w.findall('tag')}
    pts=[loc(*nodes[x.get('ref')]) for x in w.findall('nd') if x.get('ref') in nodes]
    if len(pts)<2: continue
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    if max(xs)<-400 or min(xs)>-180 or max(ys)<-150 or min(ys)>70: continue
    col=None
    if 'highway' in t: col=(255,0,0) if t['highway'] not in('footway','path','steps','service','pedestrian') else ((255,160,0) if t['highway']=='service' else (0,200,255))
    elif 'building' in t: col=(255,0,255)
    elif t.get('amenity')=='parking': col=(255,255,0)
    if col: d.line([px(p) for p in pts],fill=col,width=3); print(w.get('id'),{k:v for k,v in t.items() if k in('name','highway','building','amenity','service','parking','layer','bridge')},'x%.0f..%.0f y%.0f..%.0f'%(min(xs),max(xs),min(ys),max(ys)))
for X in range(-380,-190,20): d.text(px((X,-138)),str(X),fill=(255,255,255))
for Y in range(-130,60,20): d.text(px((-388,Y)),str(Y),fill=(255,255,255))
im.save(sys.argv[2])
