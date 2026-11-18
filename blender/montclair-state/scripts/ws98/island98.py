import numpy as np,sys,json
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
from shapely.geometry import MultiPoint,Point,Polygon
from PIL import Image
z=np.load('data/pts_crop.npz'); x,y,h,c=z['x'],z['y'],z['z'],z['c']
m=(c==2)&(x>-222)&(x<-199)&(y>-86)&(y<-64); x,y,h=x[m],y[m],h[m]
# robust plane fit iteratively
A=np.c_[x,y,np.ones_like(x)]; keep=np.ones(len(x),bool)
for it in range(6):
    co,*_=np.linalg.lstsq(A[keep],h[keep],rcond=None); r=h-A@co; keep=r<0.06
print('plane',co, 'slope x %.3f y %.3f'%(co[0],co[1]))
r=h-A@co
# ortho darkness
o=np.asarray(Image.open('data/ortho2020.png').convert('L')).astype(float); S=2048/500
def dark(X,Y):
    return o[int((250-Y)*S),int((X+250)*S)]
R=0.5
xs=np.arange(-222,-199,R); ys=np.arange(-86,-64,R)
G=np.zeros((len(ys),len(xs)))
for i,Y in enumerate(ys):
    for j,X in enumerate(xs):
        k=(np.abs(x-X)<0.5)&(np.abs(y-Y)<0.5)
        G[i,j]=np.median(r[k]) if k.sum()>1 else np.nan
for i in range(len(ys)-1,-1,-1):
    print('%6.1f '%ys[i]+''.join(' ' if np.isnan(v) else ('#' if v>0.15 else ('+' if v>0.08 else '.')) for v in G[i]))
print('       '+''.join(str(int(abs(X))%10) if X==int(X) else ' ' for X in xs))
pts=[(xs[j],ys[i]) for i in range(len(ys)) for j in range(len(xs)) if G[i,j]>0.10]
json.dump({'plane':[float(a) for a in co],'pts':[(float(a),float(b)) for a,b in pts]},open('scripts/ws98/island_pts.json','w'))
