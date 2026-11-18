import numpy as np, json
from scipy import ndimage as nd
z=np.load('data/wk/chm_grid_1m.npz'); print(z.files)
X0,X1,Y0,Y1,_=z['extent']
k=[f for f in z.files if 'B17' in f and f.endswith('dtm')][0]; kd=k.replace('dtm','dsm')
dtm=z[k]; dsm=z[kd]
chm=dsm-dtm; chm=np.where(np.isnan(chm),0,chm)
can=(chm>3).astype(float)
frac=nd.uniform_filter(can,9)
ring=json.load(open('data/wk/wood.json'))['ring']
ny,nx=dtm.shape; gx,gy=np.meshgrid(X0+np.arange(nx)+.5,Y0+np.arange(ny)+.5)
def pip(px,py,poly):
    poly=np.array(poly); ins=np.zeros(px.shape,bool); n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        c=((y1>py)!=(y2>py)) & (px < (x2-x1)*(py-y1)/(y2-y1+1e-12)+x1)
        ins^=c
    return ins
inw=pip(gx,gy,ring)
m=np.clip((frac-0.35)/0.3,0,1)*inw
m=nd.gaussian_filter(m,2.8)
print('grid',dtm.shape,'inwood',inw.mean(),'canopy',can.mean(),'mask>0.5',(m>.5).sum())
np.savez('data/wk/litter_mask.npz',m=m,extent=z['extent'])
# coarse ascii map
for j in range(ny-1,-1,-4): print(''.join('#' if m[j,i]>.6 else ('+' if m[j,i]>.2 else ('w' if inw[j,i] else '.')) for i in range(0,nx,2)), int(Y0+j))
