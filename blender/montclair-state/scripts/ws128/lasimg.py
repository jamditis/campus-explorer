import laspy, numpy as np
from pyproj import Transformer
from PIL import Image, ImageDraw
import json
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-254.,-222.,-254.,-222.; R=0.25
rd=laspy.open('data/lpc_2023_J5D6.laz'); crs=rd.header.parse_crs()
tr=Transformer.from_crs(crs.sub_crs_list[0] if crs.is_compound else crs,6527,always_xy=True) if (crs.to_epsg()!=6527 and 'New Jersey (ftUS)' not in crs.name) else None
P=[]
for ch in rd.chunk_iterator(3_000_000):
    ex,ey=np.asarray(ch.x),np.asarray(ch.y)
    if tr is not None: ex,ey=tr.transform(ex,ey)
    x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]])
P=np.vstack(P); g=P[P[:,3]==2]
nx=int((X1-X0)/R); ny=int((Y1-Y0)/R)
s=np.zeros((ny,nx)); c=np.zeros((ny,nx))
ix=((g[:,0]-X0)/R).astype(int); iy=((Y1-g[:,1])/R).astype(int)
np.add.at(s,(iy,ix),g[:,4]); np.add.at(c,(iy,ix),1)
I=np.where(c>0,s/np.maximum(c,1),np.nan)
# fill nan by 3x3 mean
for _ in range(3):
    m=np.isnan(I); 
    if not m.any(): break
    pad=np.pad(I,1,constant_values=np.nan); st=np.stack([pad[a:a+ny,b:b+nx] for a in range(3) for b in range(3)])
    I=np.where(m,np.nanmean(st,0),I)
v=np.clip((np.nan_to_num(I,nan=0)-1500)/11000*255,0,255).astype(np.uint8)
im=Image.fromarray(v).convert('RGB').resize((nx*4,ny*4),Image.NEAREST); d=ImageDraw.Draw(im)
S=4/R
Pt=lambda x,y:((x-X0)*S,(Y1-y)*S)
pl=json.load(open('scripts/ws128/plan128.json'))
cols={'WS127':(255,0,255),'WS115':(0,255,255),'WS112_C':(255,128,0),'WS102':(255,0,0),'WS111':(0,255,0),'WS103':(0,0,255)}
import collections
for n,L in pl.items():
    col=next((v for k,v in cols.items() if n.startswith(k)),None)
    if col is None: continue
    ec=collections.Counter()
    for f in L:
        for i in range(len(f)): ec[tuple(sorted((tuple(f[i][:2]),tuple(f[(i+1)%len(f)][:2]))))]+=1
    for (a,b),k in ec.items():
        if k==1: d.line([Pt(*a),Pt(*b)],fill=col,width=2)
for x in range(int(X0),int(X1)+1,2): d.text(Pt(x,Y1-0.3),str(x),fill=(255,255,0))
for y in range(int(Y0),int(Y1)+1,2): d.text(Pt(X0+0.1,y),str(y),fill=(255,255,0))
im.save('scripts/ws128/las_int128.png'); print(im.size)
