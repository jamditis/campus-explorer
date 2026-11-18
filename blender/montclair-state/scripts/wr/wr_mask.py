"""wr: extend WM_litter_mask south from y215 to y140 (new extent x120-320, y140-420, 1 m).
Same recipe as wm (OSM wood 315835594 AND 2017 B17 J5D6 CHM>3 canopy fraction over 9 m, 0.35..0.65 ramp,
OSM buildings +2 m excluded, gauss 2.8 m, gated to modelled tree crowns r+... soft) using the wo grid
(chm_grid_sw_1m, x40-260 y140-335). Old mask kept exactly for y>=240, max-merged in the y215-240 seam."""
import numpy as np, json, shutil
from scipy import ndimage as nd
from PIL import Image
R='/workspace/nj-scenes/montclair-state'
shutil.copy2(f'{R}/data/wm/litter_mask_wm.npz',f'{R}/data/wr/litter_mask_wm_pre_wr.npz')
shutil.copy2(f'{R}/data/wm/wm_litter_mask.png',f'{R}/data/wr/wm_litter_mask_pre_wr.png')
old=np.load(f'{R}/data/wm/litter_mask_wm.npz'); Mold=old['m']; assert Mold.shape==(205,200)
X0,Y0,NX,NY=120.,140.,200,280
gx,gy=np.meshgrid(X0+np.arange(NX)+.5,Y0+np.arange(NY)+.5)
g=np.load(f'{R}/data/wo/chm_grid_sw_1m.npz'); k=[q for q in g.files if q.endswith('dtm')][0]
dtm=g[k]; dsm=g[k.replace('dtm','dsm')]; GX0,GY0=40,140
m=np.isnan(dtm); idx=nd.distance_transform_edt(m,return_distances=False,return_indices=True); dtmf=dtm[tuple(idx)]
chmg=np.where(np.isnan(dsm),0,dsm-dtmf)
chm=np.zeros((NY,NX)); have=np.zeros((NY,NX),bool)
ix=np.floor(gx).astype(int)-GX0; iy=np.floor(gy).astype(int)-GY0
ok=(ix>=0)&(ix<dtm.shape[1])&(iy>=0)&(iy<dtm.shape[0])
chm[ok]=chmg[iy[ok],ix[ok]]; have[ok]=True
def pip(px,py,poly):
    poly=np.array(poly); ins=np.zeros(px.shape,bool); n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        ins^=((y1>py)!=(y2>py)) & (px < (x2-x1)*(py-y1)/(y2-y1+1e-12)+x1)
    return ins
ways=json.load(open(f'{R}/data/td/east_osm.json'))['ways']
bld=np.zeros_like(chm,bool)
for kk,e in ways.items():
    if 'building' in e['tags']: bld|=pip(gx,gy,e['pts'])
bld=nd.binary_dilation(bld,iterations=2)
can=((chm>3)&~bld&have).astype(float)
frac=nd.uniform_filter(can,9)
inw=pip(gx,gy,json.load(open(f'{R}/data/wk/wood.json'))['ring'])
M=np.clip((frac-0.35)/0.3,0,1)*inw*(~bld)*have
M=nd.gaussian_filter(M,2.8)
# fade only at the real data edges (grid south edge y140, east edge x260)
b=np.minimum(gy-140.,260.-gx); bw=np.clip((b-1)/4,0,1); M*=bw*bw*(3-2*bw)
M=np.clip(M,0,1)
# crown gating: wm trees + wq trees (r ~ 0.35 h, 3..9 m)
tr=[tuple(t) for t in json.load(open(f'{R}/data/wm/trees_xy.json'))]
for a in json.load(open(f'{R}/data/wq/fix_report.json'))['added']:
    tr.append((a['x'],a['y'],float(np.clip(0.35*a['h'],3,9))))
cov=np.zeros_like(M)
for x,y,r in tr:
    d=np.hypot(gx-x,gy-y); cov=np.maximum(cov,np.clip((min(0.6*r,7.0)+1-d)/2+0.5,0,1))
cov=nd.gaussian_filter(cov,1.5)
Mnew=M*np.clip(cov*1.25,0,1)
# merge
Mfin=Mnew.copy(); j0=int(215-Y0)
Mo=np.zeros_like(Mfin); Mo[j0:,:]=Mold
seam=(gy>=215)&(gy<240); north=gy>=240
Mfin[north]=Mo[north]; Mfin[seam]=np.maximum(Mo[seam],Mnew[seam])
# safety: nothing outside OSM wood that wasn't already there; no buildings
Mfin[(gy<215)&(~inw)]=0
chk={'old_region_maxdiff':float(np.abs(Mfin[north]-Mo[north]).max()),
 'new_cells_gt0.5':int((Mfin[gy<215]>.5).sum()),'new_cells_gt0.2':int((Mfin[gy<215]>.2).sum()),
 'raised_outside_wood':int(((Mfin-Mo>0.02)&~inw).sum()),'raised_on_bld':int(((Mfin-Mo>0.02)&bld).sum()),
 'seam_raise_max':float((Mfin[seam]-Mo[seam]).max())}
# mask under WQ trees
vals=[]
for a in json.load(open(f'{R}/data/wq/fix_report.json'))['added']:
    vals.append(round(float(Mfin[int(a['y']-Y0),int(a['x']-X0)]),2))
chk['under_wq_trees']=vals; chk['wq_mean']=float(np.mean(vals))
# plateau south of Stone / stone lawn check: cells in y215-235 outside wood
chk['lawn_outside_wood_max_y<240']=float(Mfin[(gy<240)&~inw].max())
print(json.dumps(chk))
json.dump(chk,open(f'{R}/data/wr/mask_report.json','w'),indent=1)
np.savez(f'{R}/data/wm/litter_mask_wm.npz',m=Mfin,m_pre_wr=Mold,extent=np.array([X0,X0+NX,Y0,Y0+NY,1.]))
np.savez(f'{R}/data/wr/litter_mask_wr.npz',m=Mfin,m_pre_wr=Mold,extent=np.array([X0,X0+NX,Y0,Y0+NY,1.]))
png=(np.flipud(Mfin)*65535).astype(np.uint16)
Image.fromarray(png).save(f'{R}/data/wr/wr_litter_mask.png')
for j in range(int(250-Y0),-1,-4):
    print(''.join('#' if Mfin[j,i]>.6 else ('+' if Mfin[j,i]>.2 else ('B' if bld[j,i] else ('w' if inw[j,i] else '.'))) for i in range(0,140,2)), int(Y0+j))
