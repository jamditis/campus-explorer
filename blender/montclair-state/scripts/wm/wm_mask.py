"""wm: combined leaf-litter mask image (world XY x120-320, y215-420, 1 m) = OSM wood 315835594 AND 2017 B17 J5D6 CHM canopy>3 m
fraction over 9 m (0.35..0.65 ramp, gauss 2.8 m), OSM building footprints (+2 m) excluded from canopy, north fade y350-362 (as wk),
8 m border fade. Same recipe as wk_mask.py, but DTM holes nearest-filled and the grid extended south/west past the WJ ext."""
import numpy as np, json
from scipy import ndimage as nd
from PIL import Image
X0,Y0,NX,NY=120.,215.,200,205
dtm=np.full((NY,NX),np.nan); dsm=np.full((NY,NX),np.nan)
def put(f,ox,oy):
    z=np.load(f); k=[q for q in z.files if 'J5D6' in q and q.endswith('dtm')][0]
    a=z[k]; b=z[k.replace('dtm','dsm')]; j0=int(ox-X0); i0=int(oy-Y0)
    sub_t=dtm[i0:i0+a.shape[0], j0:j0+a.shape[1]]; sub_s=dsm[i0:i0+a.shape[0], j0:j0+a.shape[1]]
    m=np.isnan(sub_t); sub_t[m]=a[m]; m=np.isnan(sub_s); sub_s[m]=b[m]
put('data/wk/chm_grid_1m.npz',140,285)      # wk grid first (same values as wk)
put('data/wm/chm_grid_south_1m.npz',120,215)
# nearest-fill DTM holes
m=np.isnan(dtm); idx=nd.distance_transform_edt(m,return_distances=False,return_indices=True)
dtmf=dtm[tuple(idx)]
chm=np.where(np.isnan(dsm),0,dsm-dtmf)
gx,gy=np.meshgrid(X0+np.arange(NX)+.5,Y0+np.arange(NY)+.5)
def pip(px,py,poly):
    poly=np.array(poly); ins=np.zeros(px.shape,bool); n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        ins^=((y1>py)!=(y2>py)) & (px < (x2-x1)*(py-y1)/(y2-y1+1e-12)+x1)
    return ins
ways=json.load(open('data/td/east_osm.json'))['ways']
bld=np.zeros_like(chm,bool)
for k,e in ways.items():
    if 'building' in e['tags']: bld|=pip(gx,gy,e['pts'])
bld=nd.binary_dilation(bld,iterations=2)
can=((chm>3)&~bld).astype(float)
frac=nd.uniform_filter(can,9)
inw=pip(gx,gy,json.load(open('data/wk/wood.json'))['ring'])
M=np.clip((frac-0.35)/0.3,0,1)*inw*(~bld)
M=nd.gaussian_filter(M,2.8)
M*=np.clip((362-gy)/12,0,1)
b=np.minimum.reduce([gx-X0,X0+NX-gx,gy-Y0,Y0+NY-gy]); bw=np.clip((b-2)/8,0,1); M*=bw*bw*(3-2*bw)
M=np.clip(M,0,1)
print('bld cells',bld.sum(),'M>0.5',(M>.5).sum(),'border(<10m) max',M[b<10].max())
# compare with wk mask on its grid
wk=np.load('data/wk/litter_mask.npz')['m']; sub=M[70:205,20:190]
print('vs wk: mean abs diff',np.abs(sub-wk).mean(),'max',np.abs(sub-wk).max())
np.savez('data/wm/litter_mask_wm.npz',m=M,extent=np.array([X0,X0+NX,Y0,Y0+NY,1.]))
Image.fromarray((np.flipud(M)*65535).astype(np.uint16)).save('data/wm/wm_litter_mask.png')
for j in range(NY-1,-1,-6): print(''.join('#' if M[j,i]>.6 else ('+' if M[j,i]>.2 else ('B' if bld[j,i] else '.')) for i in range(0,NX,2)), int(Y0+j))
# --- wm pass 2: only under modelled tree crowns (r+2 m, soft 2 m), so the coarse skirt doesn't show bare brown fields with no trees
tr=json.load(open('data/wm/trees_xy.json')); cov=np.zeros_like(M)
for x,y,r in tr:
    d=np.hypot(gx-x,gy-y); cov=np.maximum(cov,np.clip((min(0.6*r,7.0)+1-d)/2+0.5,0,1))
cov=nd.gaussian_filter(cov,1.5)
M2=M*np.clip(cov*1.25,0,1)
print('pass2 M>0.5',(M2>.5).sum(),'trees',len(tr))
np.savez('data/wm/litter_mask_wm.npz',m=M2,m_pre_trees=M,extent=np.array([X0,X0+NX,Y0,Y0+NY,1.]))
Image.fromarray((np.flipud(M2)*65535).astype(np.uint16)).save('data/wm/wm_litter_mask.png')
for j in range(NY-1,-1,-6): print(''.join('#' if M2[j,i]>.6 else ('+' if M2[j,i]>.2 else ('t' if cov[j,i]>.5 else '.')) for i in range(0,NX,2)), int(Y0+j))
