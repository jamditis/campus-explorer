import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter, gaussian_filter
from PIL import Image, ImageDraw
X0,X1,Y0,Y1=-185,-85,-305,-240
P=np.load('las137p.npy'); g=P[P[:,3]==2]
R=4  # 0.25 m
xs=X0+(np.arange((X1-X0)*R)+.5)/R; ys=Y1-(np.arange((Y1-Y0)*R)+.5)/R
GX,GY=np.meshgrid(xs,ys)
Z=griddata(g[:,:2],g[:,2],(GX,GY),'linear'); I=griddata(g[:,:2],g[:,4],(GX,GY),'nearest')
np.save('dtm137p_0p25m.npy',Z.astype(np.float32)); np.save('int137p_0p25m.npy',I.astype(np.float32))
Zs=gaussian_filter(np.nan_to_num(Z,nan=np.nanmean(Z)),0.8)
gy,gx=np.gradient(Zs,1/R); gy=-gy
hs=np.clip(128+ (gx*-1+gy*1)*400,0,255)  # hillshade from NW
sl=np.hypot(gx,gy)
# roughness: std of residual from 2 m mean
res=Zs-uniform_filter(Zs,9); rough=np.sqrt(uniform_filter(res**2,9))
Il=uniform_filter(I,5); Isd=np.sqrt(np.maximum(uniform_filter(I**2,9)-uniform_filter(I,9)**2,0))
S=8
def save(arr,name):
    im=Image.fromarray(arr.astype(np.uint8)).resize(((X1-X0)*S,(Y1-Y0)*S),Image.BILINEAR).convert('RGB')
    d=ImageDraw.Draw(im)
    for x in range(X0,X1+1,5): d.line([((x-X0)*S,0),((x-X0)*S,im.height)],fill=(0,0,255) if x%10==0 else (90,90,255))
    for y in range(Y0,Y1+1,5): d.line([(0,(Y1-y)*S),(im.width,(Y1-y)*S)],fill=(0,0,255) if y%10==0 else (90,90,255))
    im.save(name)
save(hs,'hill137p_grid.png'); save(np.clip(sl/0.25*255,0,255),'slope137p_grid.png')
save(np.clip(Isd/np.percentile(Isd,98)*255,0,255),'intsd137p_grid.png')
np.savez_compressed('feat137p.npz',Z=Zs,slope=sl,Isd=Isd,Il=Il,xs=xs,ys=ys)
