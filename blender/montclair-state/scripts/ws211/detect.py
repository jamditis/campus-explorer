import json,numpy as np
from PIL import Image
import scipy.ndimage as nd
from scipy.signal import find_peaks
im=np.asarray(Image.open('ortho_lot.png').convert('RGB')).astype(float)
x0,x1,y0,y1=-258,-212,-92,-60; S=0.05
L=im.mean(2); th=L-nd.grey_opening(L,size=(30,30)); th=nd.gaussian_filter(th,2)
P=json.load(open('paint.json')); V=np.array(P['WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED']['V'])
C=np.array([V[i*141:(i+1)*141,:2].mean(0) for i in range(18)])
t=np.array([0.969,-0.249]); t/=np.linalg.norm(t); n=np.array([-t[1],t[0]])
res={}
for row,idx in (('A',range(0,9)),('B',range(9,18))):
    c=C[list(idx)]; o=c.mean(0); nn=((c-o)@n).mean(); tt=(c-o)@t
    ts=np.arange(tt.min()-3,tt.max()+3,0.05); prof=[]
    for tv in ts:
        best=0
        for nv in np.arange(nn-1.0,nn+1.0,0.05):
            p=o+t*tv+n*nv; cc=int((p[0]-x0)/S); rr=int((y1-p[1])/S)
            if 0<=rr<th.shape[0] and 0<=cc<th.shape[1]: best=max(best,th[rr,cc])
        prof.append(best)
    prof=np.array(prof); pk,pr=find_peaks(prof,distance=int(1.8/0.05),prominence=3)
    order=np.argsort(-prof[pk])[:9]; pk=np.sort(pk[order])
    # refine n position for each peak
    pts=[]
    for k in pk:
        tv=ts[k]; best=(0,0)
        for nv in np.arange(nn-1.0,nn+1.0,0.05):
            p=o+t*tv+n*nv; cc=int((p[0]-x0)/S); rr=int((y1-p[1])/S)
            if th[rr,cc]>best[0]: best=(th[rr,cc],nv)
        pts.append((o+t*tv+n*best[1]).tolist())
    pts=np.array(pts); g=np.diff((pts-o)@t)
    print(row,'peaks',len(pk),'heights',np.round(prof[pk],1)); print(' t gaps',np.round(g,2)); print(' model t',np.round(np.sort(tt),2)); print(' real t',np.round((pts-o)@t,2),' n',np.round((pts-o)@n,2),'model n',round(nn,2))
    res[row]={'o':o.tolist(),'real':pts.tolist(),'model':c.tolist()}
json.dump(res,open('rows_detect.json','w'))
