# Session ov-prep (parallel, read-only; no .blend opened): why Calcia's LiDAR roof reads patchy red/white in the main aerial.
# Recomputes build_scene/prep_geom's per-vertex ortho 'red' tile flag (RA) on 0.5 m samples inside Calcia's OSM footprint,
# plus DSM roughness/slope, and writes a diagnosis + fix recipe. Run from montclair-state/north.
import json, numpy as np
from shapely.geometry import Polygon
import shapely
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
OUT='data/ov_prep/'
g=json.load(open('data/north_geom.json')); Z=np.load('data/grid_1m.npz')
res={}
img=np.asarray(Image.open('data/ortho2020_north.jpg').convert('RGB')).astype(np.float32)/255; H,W,_=img.shape
def ortho(x,y):
    c=(x+600)/820*W; r=(1-(y+260)/1660)*H
    return np.stack([ndi.map_coordinates(img[...,k],[r-0.5,c-0.5],order=1) for k in range(3)],-1)
for OID,SLUG in (('313024770','calcia'),('313021892','dickson'),('375626230','feliciano')):
    b=[x for x in g['buildings'] if x['osm_id']==OID][0]; P=Polygon(b['footprint'])
    x0,y0,x1,y1=P.bounds; s=0.5
    XX,YY=np.meshgrid(np.arange(x0,x1,s)+s/2,np.arange(y0,y1,s)+s/2); ins=shapely.contains_xy(P,XX,YY)
    oc=ortho(XX,YY)
    red=np.clip(((oc[...,0]-oc[...,2])-0.10)/0.08,0,1)*(oc[...,0]>oc[...,1])   # same formula as prep_geom.py l.113
    lum=(oc**2.2)@np.array([0.2126,0.7152,0.0722])
    tile_b=float(red[ins].mean()); redfrac=float((red[ins]>0.5).mean())
    lab,n=ndi.label((red>0.5)&ins); sizes=ndi.sum(np.ones_like(red),lab,range(1,n+1)) if n else np.array([])
    # where the red cells sit: distance to outline
    d=shapely.distance(P.exterior,shapely.points(XX[ins],YY[ins]))
    rin=(red[ins]>0.5)
    # DSM roughness (1 m grid)
    r_=(YY-0.0+260).astype(int); c_=(XX+600).astype(int); D=Z['dsm'][r_,c_]; T=Z['dtm_filled'][r_,c_]
    gy,gx=np.gradient(np.where(np.isfinite(Z['dsm']),Z['dsm'],np.nan)); sl=np.degrees(np.arctan(np.hypot(gx,gy)))[r_,c_]
    res[SLUG]=dict(osm_id=OID,samples_0p5m=int(ins.sum()),ortho_red_mean=round(tile_b,3),red_gt0p5_frac=round(redfrac,3),
        red_blobs=int(n),red_blob_sizes_m2_top10=[round(float(v)*s*s,1) for v in sorted(sizes,reverse=True)[:10]],
        red_cells_by_edge_dist_m={f'{a}-{a+2}':round(float(rin[(d>=a)&(d<a+2)].mean()),3) if ((d>=a)&(d<a+2)).sum()>20 else None for a in range(0,16,2)},
        ortho_lum_p10_50_90=[round(float(v),3) for v in np.percentile(lum[ins],[10,50,90])],
        tpo_rule=round(float(np.clip((np.median(lum[ins])-0.28)/0.12,0,1)),2),
        dsm_slope_deg_p50_p90=[round(float(v),1) for v in np.nanpercentile(sl[ins],[50,90])],
        dsm_p10_50_90=[round(float(v),2) for v in np.nanpercentile(D[ins],[10,50,90])])
    # diagnostic image: ortho | red mask | DSM-DTM, 4x
    def pad(a): return np.where(ins[...,None] if a.ndim==3 else ins,a,a*0.35)
    A=(np.clip(pad(oc),0,1)*255).astype(np.uint8)[::-1]
    Rm=np.zeros_like(A); Rm[...,0]=(red[::-1]*255).astype(np.uint8); Rm[...,1]=Rm[...,2]=(ins[::-1]*60).astype(np.uint8)
    h=np.clip((D-T)/12,0,1)[::-1]; Hm=np.repeat((np.nan_to_num(h)*255).astype(np.uint8)[...,None],3,-1)
    Hm[~ins[::-1]]//=3
    cat=np.concatenate([A,np.full((A.shape[0],4,3),255,np.uint8),Rm,np.full((A.shape[0],4,3),255,np.uint8),Hm],1)
    im=Image.fromarray(cat).resize((cat.shape[1]*4,cat.shape[0]*4),Image.NEAREST); dr=ImageDraw.Draw(im)
    dr.text((4,4),f"{SLUG}: ortho 2020 | prep_geom 'red' tile flag (red>0 = would render TILE) | DSM-DTM 0-12 m; 0.5 m cells, 4x; N up",fill=(255,255,0))
    im.save(OUT+f'{SLUG}_roof_tileflag_diag_ov.png')
json.dump(res,open(OUT+'day6_roof_tileflag_ov.json','w'),indent=1); print(json.dumps(res,indent=1))
