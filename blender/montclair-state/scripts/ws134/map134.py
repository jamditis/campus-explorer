import numpy as np
from PIL import Image
P=np.load('scripts/ws134/las134.npy')
X0,X1,Y0,Y1=-125,-30,-300,-190
W,H=int((X1-X0)*4),int((Y1-Y0)*4)
img=np.zeros((H,W,3),np.uint8)
b=P[P[:,3]==6]; g=P[P[:,3]==2]; v=P[P[:,3]==1]
def put(A,col):
    i=((Y1-A[:,1])*4).astype(int); j=((A[:,0]-X0)*4).astype(int); m=(i>=0)&(i<H)&(j>=0)&(j<W); img[i[m],j[m]]=col(A[m])
put(g,lambda A:np.c_[np.clip(A[:,4]/200,0,255),np.clip(A[:,4]/200,0,255),np.clip(A[:,4]/200,0,255)].astype(np.uint8))
put(v,lambda A:np.tile([0,120,0],(len(A),1)))
z0=b[:,2].min(); print('bldg z range',z0,b[:,2].max())
put(b,lambda A:np.c_[255*np.ones(len(A)),np.clip((A[:,2]-122)*12,0,255),np.zeros(len(A))].astype(np.uint8))
# grid lines every 10 m
for x in range(-120,-30,10): img[:,int((x-X0)*4)]=[0,0,255]
for y in range(-290,-190,10): img[int((Y1-y)*4),:]=[0,0,255]
Image.fromarray(img).resize((W*2,H*2),0).save('scripts/ws134/las_cls134.png')
# roof height summary on 2 m grid of class6
for y in range(-192,-300,-3):
    row=[]
    for x in range(-124,-30,3):
        t=b[(np.abs(b[:,0]-x)<1.5)&(np.abs(b[:,1]-y)<1.5)]
        row.append('%3d'%round(np.median(t[:,2])-120) if len(t)>2 else '  .')
    print('%4d'%y,''.join(row))
