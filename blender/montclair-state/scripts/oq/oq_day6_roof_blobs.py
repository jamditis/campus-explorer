# oq day-6 prep (read-only): candidate roof units / bumps on Dickson, Calcia, Feliciano from the 1 m DSM.
# A blob = connected cells inside the footprint (eroded 2 m off the edge) standing >=0.8 m over a 7x7 median of the roof (local roof plane).
# Output data/oq_prep/day6_roof_blobs_oq.json + .md. Candidates only (could be skylights, penthouses, trees overhanging): check vs ortho.
import json, numpy as np
from shapely.geometry import Polygon
from shapely import vectorized
from scipy import ndimage as ndi
g=json.load(open('data/north_geom.json')); Z=np.load('data/grid_1m.npz'); dsm=Z['dsm']; dtm=Z['dtm_filled']
out={}; md=['# Day-6 roof bump candidates from the 1 m DSM (session oq, Oct 31 2026 ~6:35 PM ET; UNVERIFIED, check vs ortho)','']
for oid,slug in (('313021892','dickson'),('313024770','calcia'),('375626230','feliciano')):
    b=[x for x in g['buildings'] if x['osm_id']==oid][0]; P=Polygon(b['footprint']); Pi=P.buffer(-2)
    x0,y0,x1,y1=[int(v) for v in P.bounds]; x0-=2;y0-=2;x1+=3;y1+=3
    D=dsm[y0+260:y1+260,x0+600:x1+600].astype(float); T=dtm[y0+260:y1+260,x0+600:x1+600].astype(float)
    XX,YY=np.meshgrid(np.arange(x0,x1)+0.5,np.arange(y0,y1)+0.5); ins=vectorized.contains(Pi,XX,YY)
    base=ndi.median_filter(np.where(np.isfinite(D),D,np.nanmedian(D)),size=9)
    bump=(D-base>=0.8)&ins&((D-T)<25)
    lab,n=ndi.label(bump); bl=[]
    for i in range(1,n+1):
        mm=lab==i; k=int(mm.sum())
        if k<2 or k>120: continue
        xs,ys=XX[mm],YY[mm]
        bl.append({'x':round(float(xs.mean()),1),'y':round(float(ys.mean()),1),'ex':round(float(xs.max()-xs.min()+1),1),'ey':round(float(ys.max()-ys.min()+1),1),
                   'cells':k,'top':round(float(D[mm].max()),2),'over_roof':round(float((D-base)[mm].max()),2)})
    bl.sort(key=lambda d:-d['cells'])
    rp=np.nanpercentile(D[vectorized.contains(P,XX,YY)],[10,50,90]).round(2).tolist()
    out[slug]={'osm_id':oid,'roof_dsm_p10_50_90':rp,'blobs':bl}
    md.append(f'## {b["name"]} (OSM {oid}) roof DSM p10/50/90 {rp}; {len(bl)} bump candidates')
    for d in bl[:20]: md.append(f'- ({d["x"]}, {d["y"]}) {d["ex"]}×{d["ey"]} m, {d["cells"]} cells, top {d["top"]} (+{d["over_roof"]} m over local roof)')
    md.append('')
json.dump(out,open('data/oq_prep/day6_roof_blobs_oq.json','w'),indent=1); open('data/oq_prep/day6_roof_blobs_oq.md','w').write('\n'.join(md)); print('\n'.join(md)[:2500])
