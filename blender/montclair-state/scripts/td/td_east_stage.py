# td parallel staging: DSM/DTM stats for the unmodelled buildings east/north-east of the Student Center (next-area prep). Read-only.
import numpy as np,json
G=np.load('north/data/grid_1m.npz'); X0,X1,Y0,Y1,R=[float(v) for v in G['extent']]; d=G['dsm']; t=G['dtm_filled']
def inpoly(x,y,P):
    P=np.array(P); n=len(P); ins=np.zeros(x.shape,bool); j=n-1
    for i in range(n):
        xi,yi=P[i]; xj,yj=P[j]; ins^=((yi>y)!=(yj>y))&(x<(xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi); j=i
    return ins
W=json.load(open('data/td/east_osm.json'))['ways']; out={}
for wid,w in W.items():
    if 'building' not in w['tags']: continue
    P=np.array(w['pts']); x0,x1,y0,y1=P[:,0].min()-2,P[:,0].max()+2,P[:,1].min()-2,P[:,1].max()+2
    if x1>X1: note='partly outside grid (x>%d)'%X1
    else: note=''
    i0,i1=max(0,int((y0-Y0)/R)),int((y1-Y0)/R); j0,j1=max(0,int((x0-X0)/R)),min(d.shape[1],int((x1-X0)/R))
    ys,xs=np.mgrid[i0:i1,j0:j1]; m=inpoly(xs*R+X0+R/2,ys*R+Y0+R/2,P); sd=d[i0:i1,j0:j1][m]; sd=sd[~np.isnan(sd)]
    rng=t[i0:i1,j0:j1][~m]; rng=rng[~np.isnan(rng)]
    rec={'name':w['tags'].get('name'),'type':w['tags'].get('building'),'bbox':[round(float(v),1) for v in (P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max())],'cells':int(m.sum()),'note':note}
    if len(sd) and len(rng):
        g=float(np.median(rng)); rec.update(ground_med=round(g,2),dsm_p50=round(float(np.percentile(sd,50)),2),dsm_p90=round(float(np.percentile(sd,90)),2),height_p90_m=round(float(np.percentile(sd,90))-g,1))
    out[wid]=rec; print(wid,rec)
out['_note']=('Webster Hall (313029100) was DEMOLISHED May-Jul 2025 (MSU RFP 1612); the site is the Interdisciplinary Science Building construction site '
 '(groundbreaking Jul 21 2026, HOK, 5 storeys, opens 2028-29; bounded by Quad Road S, Stone Street E, Webster Road W). The 2017 DSM still shows the old 3-storey dorm. '
 'Sources: montclair.edu news (ISB groundbreaking), hok.com 2026-08 news, newyorkyimby.com 2026-08-09. Do NOT model Webster Hall as standing without Joe deciding the scene date.')
json.dump(out,open('data/td/east_buildings_dsm.json','w'),indent=1)
