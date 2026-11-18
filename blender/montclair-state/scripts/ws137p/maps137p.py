import numpy as np
from PIL import Image, ImageDraw
X0,X1,Y0,Y1=-185,-85,-305,-240
P=np.load('las137p.npy'); S=8  # px per m
W,H=(X1-X0)*S,(Y1-Y0)*S
def grid(im):
    d=ImageDraw.Draw(im)
    for x in range(X0,X1+1,5):
        c=(0,0,255) if x%10==0 else (90,90,255); d.line([((x-X0)*S,0),((x-X0)*S,H)],fill=c,width=1)
        if x%10==0: d.text(((x-X0)*S+2,2),str(x),fill=(255,255,0))
    for y in range(Y0,Y1+1,5):
        c=(0,0,255) if y%10==0 else (90,90,255); d.line([(0,(Y1-y)*S),(W,(Y1-y)*S)],fill=c,width=1)
        if y%10==0: d.text((2,(Y1-y)*S+2),str(y),fill=(255,255,0))
    return im
o=Image.open('ortho_Natural2020.jpg').convert('RGB').resize((W,H),Image.LANCZOS)
grid(o).save('ortho137p_grid.png')
# ground intensity raster 0.25 m (class 2), median-filled
g=P[P[:,3]==2]; R=4
gi=np.full(((Y1-Y0)*R,(X1-X0)*R),np.nan); cnt=np.zeros_like(gi); acc=np.zeros_like(gi)
i=((Y1-g[:,1])*R).astype(int); j=((g[:,0]-X0)*R).astype(int); m=(i>=0)&(i<gi.shape[0])&(j>=0)&(j<gi.shape[1])
np.add.at(acc,(i[m],j[m]),g[m,4]); np.add.at(cnt,(i[m],j[m]),1)
gi=np.where(cnt>0,acc/np.maximum(cnt,1),np.nan)
v=np.nan_to_num(gi,nan=0); v=np.clip((v-gi[cnt>0].min())/np.percentile(gi[cnt>0],99)*255,0,255).astype(np.uint8)
im=Image.fromarray(np.dstack([v,v,v])).resize((W,H),0)
# overlay buildings (class6) red, veg (class1 high) faint green dots
a=np.array(im)
b=P[P[:,3]==6]; i=((Y1-b[:,1])*S).astype(int); j=((b[:,0]-X0)*S).astype(int); m=(i>=0)&(i<H)&(j>=0)&(j<W); a[i[m],j[m]]=[200,40,40]
grid(Image.fromarray(a)).save('lasint137p_grid.png')
# DTM 0.5 m from class-2 (mean z) for slope/curb detection
R=2; acc=np.zeros(((Y1-Y0)*R,(X1-X0)*R)); cnt=np.zeros_like(acc)
i=((Y1-g[:,1])*R).astype(int); j=((g[:,0]-X0)*R).astype(int); m=(i>=0)&(i<acc.shape[0])&(j>=0)&(j<acc.shape[1])
np.add.at(acc,(i[m],j[m]),g[m,2]); np.add.at(cnt,(i[m],j[m]),1)
dtm=np.where(cnt>0,acc/np.maximum(cnt,1),np.nan); np.save('dtm137p_0p5m.npy',dtm)
gy,gx=np.gradient(np.nan_to_num(dtm,nan=np.nanmean(dtm)),0.5)
sl=np.hypot(gx,gy); s=np.clip(sl/0.4*255,0,255).astype(np.uint8)  # 0.4 m/m = white (curbs show as lines)
grid(Image.fromarray(np.dstack([s,s,s])).resize((W,H),0)).save('slope137p_grid.png')
print('dtm range',np.nanmin(dtm),np.nanmax(dtm),'nan frac',np.isnan(dtm).mean())
