# ws74: cogen-lot asphalt mask from the NJ 2020 ortho (north/data/ortho2020_north.jpg; u=(x+600)/820, v=(y+260)/1660), 0.5 m cells
from PIL import Image; import numpy as np, scipy.ndimage as nd
im=np.asarray(Image.open('north/data/ortho2020_north.jpg').convert('RGB')).astype(float)/255
X0,X1,Y0,Y1,S=-324,-262,-97,-46,0.5
xs=np.arange(X0,X1,S)+S/2; ys=np.arange(Y0,Y1,S)+S/2
C=((xs+600)/820*2023).astype(int); R=((1-(ys+260)/1660)*4096).astype(int)
P=np.stack([np.stack([im[r-1:r+2,c-1:c+2].reshape(-1,3).mean(0) for c in C]) for r in R])
mx=P.max(2); mn=P.min(2); sat=(mx-mn)/(mx+1e-6); lum=P@[.2126,.7152,.0722]
g_dom=P[...,1]-np.maximum(P[...,0],P[...,2])
M=(sat<0.17)&(lum>0.3)&(lum<0.72)&(g_dom<0.05)
XX,YY=np.meshgrid(xs,ys)
plant=(XX>-322.8)&(XX<-285.2)&(YY>-85.8)&(YY<-59.2)
M&=~plant; M&=~((XX<-305)&(YY<-90))
M=nd.binary_closing(M,iterations=2); M=nd.binary_opening(M,iterations=2)
lab,n=nd.label(M); sz=nd.sum(M,lab,range(1,n+1)); M=np.isin(lab,1+np.where(sz>=200)[0])
M=nd.binary_fill_holes(M)&~plant
np.save('scripts/ws74/mask.npy',M); np.save('scripts/ws74/mask_grid.npy',np.array([X0,X1,Y0,Y1,S])); print(M.sum(),M.size)
v=P.copy(); v[M]=v[M]*0.4+np.array([1,0,0])*0.6
Image.fromarray((v*255).astype('uint8')).resize((M.shape[1]*5,M.shape[0]*5),0).transpose(Image.FLIP_TOP_BOTTOM).save('scripts/ws74/cogen_lot_mask_preview.png')
