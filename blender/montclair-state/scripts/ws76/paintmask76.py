# ws76: lot paint mask (white stall lines + blue accessible-stall paint) from the NJ 2020 ortho (u=(x+600)/820, v=(y+260)/1660, ~0.405 m/px).
# Output: data/ws76_lot_paint_mask.png  R=white line, G=blue paint; world box x -330..-215, y -145..-40 at 0.05 m/px.
from PIL import Image; import numpy as np, scipy.ndimage as nd
Image.MAX_IMAGE_PIXELS=None
im=np.asarray(Image.open('north/data/ortho2020_north.jpg').convert('RGB')).astype(float)/255
X0,X1,Y0,Y1,S=-330,-215,-145,-40,0.05
def colrow(x,y): return (x+600)/820*2023-0.5, (1-(y+260)/1660)*4096-0.5
c0,r1=colrow(X0,Y0); c1,r0=colrow(X1,Y1)
C0,C1,R0,R1=int(c0)-4,int(c1)+5,int(r0)-4,int(r1)+5
P=im[R0:R1,C0:C1]
lum=P@[.2126,.7152,.0722]
th=lum-nd.grey_opening(lum,size=(4,4))          # thin bright features (<~1.6 m)
blue=P[...,2]-np.maximum(P[...,0],P[...,1])
sat=(P.max(2)-P.min(2))
W=(th>0.07)&(lum>0.42)&(sat<0.14)
B=(blue>0.025)&(lum>0.25)&(lum<0.7)
# drop big compact white blobs (cars, roofs, sidewalks) at native res
lab,n=nd.label(W); 
for i,sl in enumerate(nd.find_objects(lab),1):
    a=(lab[sl]==i).sum(); h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
    if a>14 and a>0.45*h*w: W[lab==i]=False
lab,n=nd.label(B); sz=nd.sum(B,lab,range(1,n+1)); B=np.isin(lab,1+np.where(sz>=4)[0])
# resample to 0.05 m world grid (bilinear of soft scores), threshold → crisp
xs=np.arange(X0,X1,S)+S/2; ys=np.arange(Y1,Y0,-S)-S/2   # rows top=north
XX,YY=np.meshgrid(xs,ys); cc,rr=colrow(XX,YY)
def samp(A): return nd.map_coordinates(A.astype(float),[rr-R0,cc-C0],order=1)
ws=samp(np.where(W,th,0)); bs=samp(B)
Wo=ws>0.075; Bo=bs>0.5
np.save('scripts/ws76/paint_W.npy',Wo); np.save('scripts/ws76/paint_B.npy',Bo)
out=np.zeros(XX.shape+(3,),np.uint8); out[...,0]=Wo*255; out[...,1]=Bo*255
Image.fromarray(out).save('data/ws76_lot_paint_mask.png')
print('mask',out.shape,'white px',Wo.sum(),'blue px',Bo.sum())
# preview over ortho
pv=np.clip(np.stack([samp(P[...,k]) for k in range(3)],-1),0,1); pv[Wo]=[1,0,0]; pv[Bo]=[0,1,1]
Image.fromarray((pv*255).astype(np.uint8)).resize((1150,1050)).save('scripts/ws76/paint_preview.png')
