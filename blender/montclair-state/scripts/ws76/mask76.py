# ws76b: accessible-stall lot E of the RHD drive (ortho shows paving + wheelchair symbols; model had lawn). 0.4 m cells.
from PIL import Image; import numpy as np, scipy.ndimage as nd
Image.MAX_IMAGE_PIXELS=None
im=np.asarray(Image.open('north/data/ortho2020_north.jpg').convert('RGB')).astype(float)/255
X0,X1,Y0,Y1,S=-270,-214,-92,-58,0.4
xs=np.arange(X0,X1,S)+S/2; ys=np.arange(Y0,Y1,S)+S/2
C=((xs+600)/820*2023).astype(int); R=((1-(ys+260)/1660)*4096).astype(int)
P=np.stack([np.stack([im[r,c] for c in C]) for r in R])
P=nd.uniform_filter(P,size=(3,3,1))
mx=P.max(2); mn=P.min(2); sat=(mx-mn)/(mx+1e-6); lum=P@[.2126,.7152,.0722]
g_dom=P[...,1]-np.maximum(P[...,0],P[...,2])
M=(sat<0.2)&(lum>0.3)&(lum<0.8)&(g_dom<0.04)
M=nd.binary_closing(M,iterations=2); M=nd.binary_opening(M,iterations=1)
lab,n=nd.label(M); sz=nd.sum(M,lab,range(1,n+1)); M=np.isin(lab,1+np.where(sz>=150)[0]); M=nd.binary_fill_holes(M)
np.save('scripts/ws76/mask76.npy',M); np.save('scripts/ws76/mask76_grid.npy',np.array([X0,X1,Y0,Y1,S]))
v=P.copy(); v[M]=v[M]*0.5+np.array([1,0,0])*0.5
Image.fromarray((np.clip(v[::-1],0,1)*255).astype(np.uint8)).resize((M.shape[1]*6,M.shape[0]*6),Image.NEAREST).save('scripts/ws76/mask76_preview.png')
print(M.shape,M.sum())
# by-eye north edge of the paving (lawn strip with trees along College Ave is north of it): (-257,-65.5) -> (-216,-71)
XX,YY=np.meshgrid(xs,ys); yN=-65.5+(XX+257)*(-5.5/41)
M&=(YY<yN)
np.save('scripts/ws76/mask76.npy',M)
v=P.copy(); v[M]=v[M]*0.5+np.array([1,0,0])*0.5
Image.fromarray((np.clip(v[::-1],0,1)*255).astype(np.uint8)).resize((M.shape[1]*6,M.shape[0]*6),Image.NEAREST).save('scripts/ws76/mask76_preview.png')
print('clipped',M.sum())
