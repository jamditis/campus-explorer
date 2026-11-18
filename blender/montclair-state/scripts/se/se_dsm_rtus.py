# se: find rooftop blobs on the Student Center L0/L1 roofs from the B17 DSM (1 m). Output data/se/sc_roof_blobs.json
import numpy as np, json
from shapely.geometry import Polygon
from shapely import contains_xy
class Path:
    def __init__(s,o): s.p=Polygon(o)
    def contains_points(s,a): return contains_xy(s.p,a[:,0],a[:,1])
from scipy import ndimage
G=np.load('north/data/grid_1m.npz'); X0,X1,Y0,Y1,R=[float(v) for v in G['extent']]; dsm=G['dsm']
L=json.load(open('north/data/day_heroes/student_center_levels_20261014.json'))['levels']
ys,xs=np.mgrid[0:dsm.shape[0],0:dsm.shape[1]]; CX,CY=xs*R+X0+R/2, ys*R+Y0+R/2
out={}
for lv in L:
    top=lv['top']
    for p in lv['polys']:
        P=Path(p['outer']); m=P.contains_points(np.c_[CX.ravel(),CY.ravel()]).reshape(dsm.shape)
        # erode 1 cell to skip parapet/edge
        mi=ndimage.binary_erosion(m,iterations=2)
        h=dsm-top
        if lv['name']=='L0_low':
            # exclude L1 area
            P1=Path(L[1]['polys'][0]['outer']); m1=P1.contains_points(np.c_[CX.ravel(),CY.ravel()]).reshape(dsm.shape)
            mi&=~ndimage.binary_dilation(m1,iterations=2)
        roof=mi&(np.abs(h)<0.4)
        blob=mi&(h>0.5)&(h<5)
        lab,n=ndimage.label(blob)
        bl=[]
        for i in range(1,n+1):
            c=lab==i; k=c.sum()
            bl.append(dict(x=float(CX[c].mean()),y=float(CY[c].mean()),cells=int(k),h=float(np.percentile(h[c],80)),
              x0=float(CX[c].min()-.5),x1=float(CX[c].max()+.5),y0=float(CY[c].min()-.5),y1=float(CY[c].max()+.5)))
        print(lv['name'],top,'roofcells',int(roof.sum()),'blobs',n,'roof med',float(np.median(dsm[roof])) if roof.any() else None)
        for b in sorted(bl,key=lambda b:-b['cells'])[:25]: print('  ',{k:round(v,2) for k,v in b.items()})
        out[lv['name']]=dict(top=top,outer=p['outer'],blobs=bl)
json.dump(out,open('data/se/sc_roof_blobs.json','w'),indent=1)
