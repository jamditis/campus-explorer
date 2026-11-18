import numpy as np
from scipy.ndimage import median_filter, generic_filter
D='prep/ws185_lot36N/'
P=np.load(D+'las185_2023.npy'); g=P[P[:,3]==2]
X0,X1,Y0,Y1=-352.,-300.,-236.,-190.; r=0.25
nx,ny=int((X1-X0)/r),int((Y1-Y0)/r)
ix=((g[:,0]-X0)/r).astype(int); iy=((Y1-g[:,1])/r).astype(int)
S=np.zeros((ny,nx));C=np.zeros((ny,nx));Z=np.zeros((ny,nx))
np.add.at(S,(iy,ix),g[:,4]);np.add.at(C,(iy,ix),1);np.add.at(Z,(iy,ix),g[:,2])
I=np.where(C>0,S/np.maximum(C,1),np.nan); Zm=np.where(C>0,Z/np.maximum(C,1),np.nan)
def nanmed(a):
  a=a[~np.isnan(a)]; return np.median(a) if len(a) else np.nan
Im=generic_filter(I,nanmed,size=5,mode='nearest')
Zs=generic_filter(Zm,nanmed,size=5,mode='nearest')
np.save(D+'int185_0p25m.npy',Im); np.save(D+'dtm185_0p25m.npy',Zs)
print('intensity p5/50/95',np.nanpercentile(Im,[5,50,95]))
# per-x column scan from y -232 northwards: class sequence (A asphalt <3.8k, G grass >5.5k, M mid)
for x in np.arange(-346,-300,2.0):
  c=int((x-X0)/r); col=Im[:,c]; zc=Zs[:,c]
  s=''
  for y in np.arange(-232,-190,1.0):
    rr=int((Y1-y)/r); v=np.nanmedian(col[max(rr-2,0):rr+2])
    s+= '?' if np.isnan(v) else ('A' if v<3800 else ('G' if v>5500 else 'm'))
  zs=' '.join('%.1f'%np.nanmedian(zc[int((Y1-y)/r)-2:int((Y1-y)/r)+2]) for y in range(-232,-190,4))
  print('x%5.0f %s | z(y-232..-192 step4) %s'%(x,s,zs))
# image
import PIL.Image as Im_
a=np.nan_to_num(Im,nan=0); a=np.clip(a/12000*255,0,255).astype(np.uint8)
Im_.fromarray(a).resize((nx*4,ny*4),0).save(D+'int185.png')
