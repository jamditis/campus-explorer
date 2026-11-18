# ws47 parallel: sparse street-tree points for the ~0.5 km neighbourhood band (Joe Nov 9 9:54).
# Source: OSM via Overpass (ODbL). Output: data/ws47/band_trees.json in Blender metres (EPSG:6527 ftUS - origin)*m_per_ftUS.
import json, sys, random, urllib.request, urllib.parse, math
sys.path[:0]=['/workspace/nj-scenes/pylib_shapely313','/workspace/nj-scenes/pylib_proj_wq2']
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
import pyproj
B=json.load(open('north/data/boundary.json')); E0,N0=B['origin_ftUS']; k=B['m_per_ftUS']
poly=Polygon(B['polygon_blender_m'])
T=pyproj.Transformer.from_crs(4326,6527,always_xy=True)
def P(lon,lat):
    e,n=T.transform(lon,lat); return ((e-E0)*k,(n-N0)*k)
cx,cy=poly.centroid.x,poly.centroid.y
# bbox: polygon expanded by 750 m, back to lat/lon
Ti=pyproj.Transformer.from_crs(6527,4326,always_xy=True)
x0,y0,x1,y1=poly.buffer(750).bounds
lo0,la0=Ti.transform(x0/k+E0,y0/k+N0); lo1,la1=Ti.transform(x1/k+E0,y1/k+N0)
q=f'[out:json][timeout:90];(way["highway"~"^(residential|tertiary|secondary|primary|unclassified|living_street)$"]({la0},{lo0},{la1},{lo1});way["building"]({la0},{lo0},{la1},{lo1}););out geom;'
cache='data/ws47/overpass_band.json'
try: D=json.load(open(cache))
except Exception:
    # Overpass unreachable 2026-11-11 -> OSM main API /map in tiles (ODbL), polite 1.5 s spacing
    import xml.etree.ElementTree as ET, time
    nodes={}; ways={}
    la=la0
    while la<la1:
        lo=lo0
        while lo<lo1:
            u=f'https://api.openstreetmap.org/api/0.6/map?bbox={lo:.5f},{la:.5f},{min(lo+0.01,lo1):.5f},{min(la+0.008,la1):.5f}'
            for t in range(3):
                try:
                    r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'nj-scenes-research/1.0'}),timeout=90).read(); break
                except Exception as ex: print('retry',u,ex); time.sleep(5); r=None
            if r:
                X=ET.fromstring(r)
                for n in X.iter('node'): nodes[n.get('id')]=(float(n.get('lon')),float(n.get('lat')))
                for w in X.iter('way'):
                    tg={t.get('k'):t.get('v') for t in w.iter('tag')}
                    if 'building' in tg or 'highway' in tg: ways[w.get('id')]=([nd.get('ref') for nd in w.iter('nd')],tg)
            time.sleep(1.5); lo+=0.01
        la+=0.008
    D={'elements':[{'id':int(i),'tags':tg,'geometry':[{'lon':nodes[r][0],'lat':nodes[r][1]} for r in refs if r in nodes]} for i,(refs,tg) in ways.items()]}
    json.dump(D,open(cache,'w'))
halfw={'primary':7.5,'secondary':6.5,'tertiary':5.5,'residential':4.5,'unclassified':4.5,'living_street':3.5}
roads=[];blds=[]
for w in D['elements']:
    if 'geometry' not in w: continue
    pts=[P(g['lon'],g['lat']) for g in w['geometry']]
    t=w.get('tags',{})
    if 'building' in t and len(pts)>=4: blds.append(Polygon(pts).buffer(2.5))
    elif t.get('highway') in halfw and len(pts)>=2: roads.append((LineString(pts),t['highway'],w['id'],t.get('name','')))
halfw={'primary':7.5,'secondary':6.5,'tertiary':5.5,'residential':4.5,'unclassified':4.5,'living_street':3.5}
roadarea=unary_union([l.buffer(halfw[h]) for l,h,_,_ in roads]); bldarea=unary_union(blds)
inner=poly.buffer(120); outer=poly.buffer(700)
band=outer.difference(inner)
random.seed(4711); out=[]
for l,h,wid,name in roads:
    seg=l.intersection(band)
    if seg.is_empty: continue
    L=l.length; s=random.uniform(0,20)
    while s<L:
        p=l.interpolate(s); q2=l.interpolate(min(L,s+1)); dx,dy=q2.x-p.x,q2.y-p.y; n=math.hypot(dx,dy) or 1
        side=random.choice((-1,1)); off=halfw[h]+random.uniform(1.8,4.0)
        pt=Point(p.x-dy/n*off*side,p.y+dx/n*off*side)
        if band.contains(pt) and not roadarea.contains(pt) and not bldarea.contains(pt) and random.random()<0.7:
            out.append({'x':round(pt.x,2),'y':round(pt.y,2),'way':wid,'street':name,'hw':h,'rot':round(random.uniform(0,6.283),3),'scale':round(random.uniform(0.8,1.15),3),'species':random.choice(['PinOak','RedMaple','LondonPlane','Sweetgum'])})
        s+=random.uniform(22,40)
# thin: drop points closer than 9 m
keep=[]
for o in out:
    if all((o['x']-k2['x'])**2+(o['y']-k2['y'])**2>81 for k2 in keep[-60:]): keep.append(o)
json.dump({'source':'OSM via Overpass (ODbL), fetched 2026-11-11 ws47 (OSM API /map tiles)','crs':'Blender m = (EPSG:6527 ftUS - origin)*m_per_ftUS','band':'120-700 m outside boundary polygon','n':len(keep),'trees':keep},open('data/ws47/band_trees.json','w'))
print('W47 roads',len(roads),'blds',len(blds),'trees',len(keep))
