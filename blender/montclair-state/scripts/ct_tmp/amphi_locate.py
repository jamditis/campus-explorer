import sys, json, xml.etree.ElementTree as ET
sys.path.insert(0,'/workspace/nj-scenes/blender_pylib_proj')
import numpy as np
from pyproj import Transformer
FT=1200/3937; tr=Transformer.from_crs("EPSG:4326","EPSG:6527",always_xy=True)
c_e,c_n=tr.transform(-74.19720,40.86000); E0,N0=round(c_e,-1),round(c_n,-1)
def loc(lon,lat):
    e,n=tr.transform(lon,lat); return ((e-E0)*FT,(n-N0)*FT)
r=ET.parse('/workspace/nj-scenes/montclair-state/data/msu_osm.xml').getroot()
nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.iter('node')}
out={}
for w in r.iter('way'):
    t={x.get('k'):x.get('v') for x in w.findall('tag')}
    if w.get('id') in ('232850516',) or t.get('name','').lower().startswith('amphi') or t.get('leisure')=='outdoor_seating':
        pts=[loc(*nodes[x.get('ref')]) for x in w.findall('nd') if x.get('ref') in nodes]
        out[w.get('id')]={'tags':t,'pts':[(round(a,2),round(b,2)) for a,b in pts]}
P=np.array(out['232850516']['pts'])
print('amphi way 232850516 local xy bbox', P.min(0), P.max(0), 'centroid', P[:-1].mean(0))
z=np.load('/workspace/nj-scenes/montclair-state/data/pts_crop.npz'); px,py,pz,pc=z['x'],z['y'],z['z'],z['c']
def pip(P,x,y):
    ins=np.zeros(len(x),bool); n=len(P)
    for i in range(n-1):
        x1,y1=P[i]; x2,y2=P[i+1]
        c=((y1>y)!=(y2>y)) & (x < (x2-x1)*(y-y1)/(y2-y1+1e-12)+x1)
        ins ^= c
    return ins
m=pip(P,px,py); print('lidar pts inside', m.sum(), 'classes', np.unique(pc[m],return_counts=True))
g=m&((pc==2)|(pc==1))
print('ground/unclass z p0/p10/p50/p90/p100', np.round(np.percentile(pz[g],[0,10,50,90,100]),2))
# principal axis + profile along it
c=P[:-1].mean(0); Q=np.c_[px[g],py[g]]-c; U,S,Vt=np.linalg.svd(P[:-1]-c,full_matrices=False); ax=Vt[0]; ax2=Vt[1]
a=Q@ax; b=Q@ax2
print('axis1', np.round(ax,3), 'extent', round(a.min(),1), round(a.max(),1), 'axis2', np.round(ax2,3), 'extent', round(b.min(),1), round(b.max(),1))
prof=[]
for t0 in np.arange(np.floor(b.min()), b.max(), 1.0):
    k=(b>=t0)&(b<t0+1)&(np.abs(a)<6)
    if k.sum()>3: prof.append((float(t0), int(k.sum()), round(float(np.median(pz[g][k])),2)))
print('profile along axis2 (|axis1|<6): t, n, zmed'); [print(p) for p in prof]
prof1=[]
for t0 in np.arange(np.floor(a.min()), a.max(), 1.0):
    k=(a>=t0)&(a<t0+1)&(np.abs(b)<4)
    if k.sum()>3: prof1.append((float(t0), int(k.sum()), round(float(np.median(pz[g][k])),2)))
print('profile along axis1 (|axis2|<4)'); [print(p) for p in prof1]
# tall thin objects (lighting towers) near it: class 1/6 points > ground+8
near=(np.abs(px-c[0])<45)&(np.abs(py-c[1])<45)&(pz>np.percentile(pz[g],90)+8)
print('tall returns near (>p90+8 m):', near.sum())
if near.sum():
    H=np.c_[px[near],py[near],pz[near]]
    from collections import defaultdict
    cl=defaultdict(list)
    for x,y,zz in H: cl[(int(x//3),int(y//3))].append(zz)
    for k_,v in sorted(cl.items(), key=lambda kv:-len(kv[1]))[:12]: print('cell3m',(k_[0]*3,k_[1]*3),len(v),round(max(v),2))
json.dump({'osm':out,'centroid':[float(c[0]),float(c[1])],'axis1':ax.tolist(),'axis2':ax2.tolist(),'profile_axis2':prof,'profile_axis1':prof1}, open('/workspace/nj-scenes/montclair-state/north/data/day_heroes/ct/amphi_locate_ct.json','w'), indent=1)
