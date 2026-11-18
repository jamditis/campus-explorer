import numpy as np,json,sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from PIL import Image,ImageDraw
from shapely.geometry import Polygon
from shapely.ops import unary_union
X0,X1,Y0,Y1=-245,-185,-120,-55
z=np.load('data/pts_crop.npz'); x,y,h,c=z['x'],z['y'],z['z'],z['c']
m=(x>X0)&(x<X1)&(y>Y0)&(y<Y1)
x,y,h,c=x[m],y[m],h[m],c[m]
print('pts',m.sum(),np.unique(c,return_counts=True))
g=c==2
R=0.25; W=int((X1-X0)/R); H=int((Y1-Y0)/R)
ix=((x-X0)/R).astype(int); iy=((Y1-y)/R).astype(int)
img=np.full((H,W),np.nan); cnt=np.zeros((H,W))
s=np.zeros((H,W))
np.add.at(s,(iy[g],ix[g]),h[g]); np.add.at(cnt,(iy[g],ix[g]),1)
img=np.where(cnt>0,s/np.maximum(cnt,1),np.nan)
np.save('scripts/ws98/gnd025.npy',img)
# ortho crop
o=Image.open('data/ortho2020.png'); S=o.size[0]/500
oc=o.crop((int((X0+250)*S),int((250-Y1)*S),int((X1+250)*S),int((250-Y0)*S))).resize((W*2,H*2))
# hillshade of ground
f=img.copy(); 
from scipy import ndimage
nanm=np.isnan(f); idx=ndimage.distance_transform_edt(nanm,return_distances=False,return_indices=True); f=f[tuple(idx)]
gy,gx=np.gradient(f,R)
sl=np.hypot(gx,gy)
hs=np.clip(128+ 600*( -gx*0.7+gy*0.7)*R,0,255)
Image.fromarray(np.clip(sl*255/0.6,0,255).astype(np.uint8)).resize((W*2,H*2)).save('scripts/ws98/slope.png')
# outline
D=json.load(open('scripts/ws96/dump96.json'))
polys=[]
for n in D:
    if n.startswith(('WS75','WS76','WS79','WS80','WS94')):
        V=D[n]['v']
        for fc in D[n]['f']:
            p=Polygon([(V[i][0],V[i][1]) for i in fc]).buffer(0)
            if p.area>0: polys.append(p)
U=unary_union(polys).buffer(0.3).buffer(-0.3)
def px(a,b): return ((a-X0)/R*2,(Y1-b)/R*2)
for im,name in ((oc,'ortho_lotE.png'),(Image.open('scripts/ws98/slope.png').convert('RGB'),'slope_lotE.png')):
    d=ImageDraw.Draw(im)
    for gg in getattr(U,'geoms',[U]):
        d.line([px(*p) for p in gg.exterior.coords],fill=(255,0,0),width=1)
    for t in range(-240,-185,5):
        d.line([px(t,Y1),px(t,Y1-1)],fill=(255,255,0)); d.text(px(t,Y1-1),str(t),fill=(255,255,0))
    for t in range(-115,-55,5):
        d.text(px(X0,t),str(t),fill=(255,255,0))
    im.save('scripts/ws98/'+name)
print('dump keys',[k for k in D][:20])
