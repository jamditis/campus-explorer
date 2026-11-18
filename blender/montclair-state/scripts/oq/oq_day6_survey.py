# Session oe (generalised from nd) background prep; env OID, SLUG, NAME, SKIP_ORTHO=1
# Session nd background prep (read-only, no .blend opened): Ben Samuels Children's Center (OSM 313031568) DSM/DTM survey,
# height-class map + ASCII, 2020-ortho crop with 5 m / 10 m scene grid. Same georef/method as mb/mc/md (Annex).
import json, numpy as np
from shapely.geometry import Polygon, Point
from shapely import vectorized
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
Image.MAX_IMAGE_PIXELS=None
import os
OID=os.environ['OID']; OUT='data/oq_prep/'; SLUG=os.environ['SLUG']; NAME=os.environ['NAME']
g=json.load(open('data/north_geom.json')); Z=np.load('data/grid_1m.npz')
b=[x for x in g['buildings'] if x['osm_id']==OID][0]; P=Polygon(b['footprint'])
try:
    from shapely.geometry import shape
    BND=None
    import re
    bj=json.load(open('data/boundary.json')) if __import__('os').path.exists('data/boundary.json') else None
except Exception: bj=None
mr=P.minimum_rotated_rectangle; c=list(mr.exterior.coords)
e=[np.hypot(c[i+1][0]-c[i][0],c[i+1][1]-c[i][1]) for i in range(2)]
ang=[np.degrees(np.arctan2(c[i+1][1]-c[i][1],c[i+1][0]-c[i][0]))%180 for i in range(2)]
x0,y0,x1,y1=P.bounds
xs=np.arange(int(np.floor(x0)),int(np.ceil(x1))+1); ys=np.arange(int(np.floor(y0)),int(np.ceil(y1))+1); XX,YY=np.meshgrid(xs+0.5,ys+0.5)
m=vectorized.contains(P,XX,YY); r=(YY-0.5+260).astype(int); cc=(XX-0.5+600).astype(int)
rec={'name':b['name'],'osm_id':OID,'tags':b['tags'],'area_m2':round(P.area),'centroid':[round(v,1) for v in P.centroid.coords[0]],
     'bbox':[round(v,1) for v in P.bounds],'mrr_m':[round(v,1) for v in e],'mrr_axes_deg':[round(v,1) for v in ang],'n_verts':len(b['footprint']),
     'geom_ground':b.get('ground'),'geom_roof':b.get('roof'),'height_src':b.get('height_src'),'levels_split':b.get('levels_split'),
     'note':'percentiles p10/p50/p90/max + cell count over 1 m cells inside the OSM footprint'}
for k in Z.keys():
    A=Z[k]
    if A.ndim!=2: continue
    try: v=A[r[m],cc[m]]
    except Exception: continue
    v=v.astype(float); v=v[np.isfinite(v)]
    if v.size: rec[k]=[float(np.round(np.percentile(v,q),2)) for q in (10,50,90,100)]+[int(v.size)]
dsm=Z['dsm']; dtm=Z['dtm_filled']
pad=10; X0,Y0,X1,Y1=int(np.floor(x0))-pad,int(np.floor(y0))-pad,int(np.ceil(x1))+pad,int(np.ceil(y1))+pad
sl=(slice(Y0+260,Y1+260),slice(X0+600,X1+600)); D=dsm[sl]; T=dtm[sl]; h=D-T
XXa,YYa=np.meshgrid(np.arange(X0,X1)+0.5,np.arange(Y0,Y1)+0.5); inside=vectorized.contains(P,XXa,YYa)
hi=h[inside]; cls={}
for lo,hh,nm in [(-9,1.0,'ground/terrace <1 m'),(1.0,2.5,'1-2.5 m'),(2.5,5.5,'one storey 2.5-5.5 m'),(5.5,9,'5.5-9 m (two storeys or pitched ridge)'),(9,60,'>9 m (trees?)')]:
    cls[nm]=int(((hi>=lo)&(hi<hh)).sum())
rec['h_classes_inside']=cls; rec['h_inside_p10_50_90']=[float(x) for x in np.nanpercentile(hi,[10,50,90]).round(2)]
# per-quadrant roof heights along the mrr axes (rough split hint)
cx,cy=P.centroid.coords[0]; a=np.radians(ang[0]); ux,uy=np.cos(a),np.sin(a)
U=(XXa-cx)*ux+(YYa-cy)*uy; V=-(XXa-cx)*uy+(YYa-cy)*ux; q={}
for su in (-1,1):
    for sv in (-1,1):
        mm=inside&(np.sign(U)==su)&(np.sign(V)==sv)&np.isfinite(D)
        if mm.sum(): q[f'u{"+" if su>0 else "-"}v{"+" if sv>0 else "-"}']=[float(x) for x in np.percentile(D[mm],[50,90]).round(2)]+[int(mm.sum())]
rec['dsm_quadrants_p50_p90_n']=q
json.dump(rec,open(OUT+SLUG+'_survey_oe.json','w'),indent=1)
ch=' .:-=+*#%@'
with open(OUT+SLUG+'_dsm_ascii_oe.txt','w') as f:
    f.write(f"{NAME} OSM {OID}; h=DSM-DTM 1 m cells; chars "+' '.join(f"{c!r}={i}-{i+1}m" for i,c in enumerate(ch))+f"; x {X0}..{X1} left->right, y {Y1}..{Y0} top->bottom; UPPER-CASE '#'... same; 'o' marks OSM outline cells\n")
    edge=inside^ndi.binary_erosion(inside)
    for rr in range(D.shape[0]-1,-1,-1):
        f.write(''.join(('o' if edge[rr,k] and (not np.isfinite(h[rr,k]) or h[rr,k]<1) else (ch[min(9,max(0,int(h[rr,k])))] if np.isfinite(h[rr,k]) else '?')) for k in range(D.shape[1]))+'\n')
im=np.clip(h[::-1]/10,0,1); Image.fromarray((np.nan_to_num(im)*255).astype(np.uint8)).resize((D.shape[1]*8,D.shape[0]*8),Image.NEAREST).save(OUT+SLUG+'_dsm_minus_dtm_8x_oe.png')
# ortho crop with grid
if os.environ.get('SKIP_ORTHO')=='1': print('OK',json.dumps(rec)[:2500]); raise SystemExit
img=Image.open('data/ortho2020_north.jpg').convert('RGB'); imo=np.asarray(img).astype(np.float32)/255; H,W,_=imo.shape
def px(x,y): return ((x+600)/820*W, (1-(y+260)/1660)*H)
pad=14; X0,Y0,X1,Y1=x0-pad,y0-pad,x1+pad,y1+pad
c0,r0=px(X0,Y1); c1,r1=px(X1,Y0); step=0.1
cols=np.linspace(c0,c1,int((X1-X0)/step)); rows=np.linspace(r0,r1,int((Y1-Y0)/step)); CC,RR=np.meshgrid(cols,rows)
A=np.stack([ndi.map_coordinates(imo[...,k],[RR-0.5,CC-0.5],order=1) for k in range(3)],-1)
gI=Image.fromarray((np.clip(A,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(gI); hh,ww=A.shape[:2]
def tp(x,y): return ((x-X0)/(X1-X0)*ww,(Y1-y)/(Y1-Y0)*hh)
for x in np.arange(np.ceil(X0/5)*5,X1,5): d.line([tp(x,Y0),tp(x,Y1)],fill=(255,0,0) if x%10==0 else (0,110,255),width=1)
for y in np.arange(np.ceil(Y0/5)*5,Y1,5): d.line([tp(X0,y),tp(X1,y)],fill=(255,0,0) if y%10==0 else (0,110,255),width=1)
d.line([tp(*p) for p in list(P.exterior.coords)],fill=(255,255,0),width=2)
d.text((4,4),f"{NAME} OSM {OID} outline (yellow); grid 5 m blue / 10 m red; x {X0:.0f}..{X1:.0f} y {Y0:.0f}..{Y1:.0f}; 2020 NJ ortho",fill=(255,255,0))
gI.save(OUT+SLUG+'_ortho2020_grid_oe.png'); print('OK',json.dumps(rec)[:1500],gI.size)
