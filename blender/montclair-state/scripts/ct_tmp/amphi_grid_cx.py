# cx parallel: 0.5 m ground grid + 0.40 m contours for the amphitheater (OSM way 232850516), from data/pts_crop.npz (LiDAR 2023, classes 2/1).
import json, numpy as np
from PIL import Image, ImageDraw
D='/workspace/nj-scenes/montclair-state/'; O=D+'north/data/day_heroes/cx/amphi/'
j=json.load(open(D+'north/data/day_heroes/ct/amphi_locate_ct.json'))
P=np.array(j['osm']['232850516']['pts'])
z=np.load(D+'data/pts_crop.npz'); px,py,pz,pc=z['x'],z['y'],z['z'],z['c']
B=12.0; R=0.5
x0,y0=P[:,0].min()-B,P[:,1].min()-B; x1,y1=P[:,0].max()+B,P[:,1].max()+B
nx,ny=int((x1-x0)/R)+1,int((y1-y0)/R)+1
m=(px>=x0)&(px<x1)&(py>=y0)&(py<y1)
res={}
for cls,name in ((2,'ground'),(1,'unclass'),(6,'building')):
    k=m&(pc==cls); ix=((px[k]-x0)/R).astype(int); iy=((py[k]-y0)/R).astype(int)
    g=np.full((ny,nx),np.nan,np.float32); order=np.lexsort((pz[k],iy*nx+ix)); lin=(iy*nx+ix)[order]; zz=pz[k][order]
    # median per cell
    u,st,cnt=np.unique(lin,return_index=True,return_counts=True)
    med=zz[st+cnt//2]; g.flat[u]=med; res[name]=g; print(name,int(k.sum()),'cells',len(u))
G=res['ground'].copy()
# fill gaps by iterative neighbour mean (max 6 passes)
for _ in range(6):
    nanm=np.isnan(G)
    if not nanm.any(): break
    pad=np.pad(G,1,constant_values=np.nan)
    nb=np.stack([pad[1+dy:1+dy+ny,1+dx:1+dx+nx] for dy in (-1,0,1) for dx in (-1,0,1) if dy or dx])
    fill=np.nanmean(np.where(np.isnan(nb),np.nan,nb),0)
    G[nanm]=fill[nanm]
np.savez_compressed(O+'amphi_grid_0p5m_cx.npz',ground=G,ground_raw=res['ground'],unclass=res['unclass'],building=res['building'],x0=x0,y0=y0,res=R,outline=P)
# hillshade + contours + outline PNG (north up, 4 px per cell)
S=4; gz=np.nan_to_num(G,nan=np.nanmin(G))
dy_,dx_=np.gradient(gz,R); sl=np.arctan(np.hypot(dx_,dy_)); asp=np.arctan2(-dx_,dy_)
az,alt=np.radians(315),np.radians(45)
hs=np.clip(np.sin(alt)*np.cos(sl)+np.cos(alt)*np.sin(sl)*np.cos(az-asp),0,1)
img=Image.fromarray((np.flipud(hs)*255).astype(np.uint8)).resize((nx*S,ny*S)).convert('RGB'); d=ImageDraw.Draw(img)
lv=np.arange(132.6,141.5,0.40)
for L in lv:
    a=gz>=L; e=(a[:,1:]!=a[:,:-1]); f=(a[1:,:]!=a[:-1,:])
    for (yy,xx) in zip(*np.nonzero(e)): d.point((int((xx+1)*S),int((ny-1-yy)*S+S//2)),fill=(220,60,40))
    for (yy,xx) in zip(*np.nonzero(f)): d.point((int(xx*S+S//2),int((ny-1-yy-1)*S+S)),fill=(220,60,40))
pp=[((x-x0)/R*S,(ny-(y-y0)/R)*S) for x,y in P]; d.line(pp,fill=(40,120,255),width=2)
img.save(O+'amphi_hillshade_contours_0p40_cx.png')
# row profile inside outline along axis1 (up-slope), 0.5 m bins
ax=np.array(j['axis1']); c=np.array(j['centroid'])
yy,xx=np.mgrid[0:ny,0:nx]; X=x0+(xx+0.5)*R; Y=y0+(yy+0.5)*R
def pip(P,x,y):
    ins=np.zeros(x.shape,bool)
    for i in range(len(P)-1):
        (a1,b1),(a2,b2)=P[i],P[i+1]; ins^=((b1>y)!=(b2>y))&(x<(a2-a1)*(y-b1)/(b2-b1+1e-12)+a1)
    return ins
ins=pip(P,X,Y); A=(X-c[0])*ax[0]+(Y-c[1])*ax[1]
prof=[]
for t in np.arange(-22,24,0.5):
    k=ins&(A>=t)&(A<t+0.5)&~np.isnan(res['ground'])
    if k.sum()>3: prof.append((float(t),int(k.sum()),round(float(np.median(res['ground'][k])),3)))
json.dump({'grid':{'x0':x0,'y0':y0,'res':R,'nx':nx,'ny':ny},'contour_levels':lv.round(2).tolist(),'profile_axis1_0p5':prof},open(O+'amphi_grid_meta_cx.json','w'),indent=1)
print('done',nx,ny,'profile bins',len(prof))
