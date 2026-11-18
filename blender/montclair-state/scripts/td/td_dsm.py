# td: Webster Hall (OSM 313029100) roof/ground stats from north/data/grid_1m.npz (2017 B17 + 2023 B23 1 m grids)
import numpy as np,json,sys
G=np.load('north/data/grid_1m.npz'); X0,X1,Y0,Y1,R=[float(v) for v in G['extent']]
d=G['dsm']; t=G['dtm_filled']; b=G['bld']
def inpoly(x,y,P):
    P=np.array(P); n=len(P); ins=np.zeros(x.shape,bool); j=n-1
    for i in range(n):
        xi,yi=P[i]; xj,yj=P[j]
        c=((yi>y)!=(yj>y))&(x<(xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi); ins^=c; j=i
    return ins
W=json.load(open('data/td/east_osm.json'))['ways']
P=W['313029100']['pts']; print('pts',P)
P_=np.array(P); x0,x1,y0,y1=P_[:,0].min()-3,P_[:,0].max()+3,P_[:,1].min()-3,P_[:,1].max()+3
i0,i1=int((y0-Y0)/R),int((y1-Y0)/R); j0,j1=int((x0-X0)/R),int((x1-X0)/R)
sub=d[i0:i1,j0:j1]; ys,xs=np.mgrid[i0:i1,j0:j1]; CX,CY=xs*R+X0+R/2,ys*R+Y0+R/2
m=inpoly(CX,CY,P)
print('cells',m.sum(),'dsm pct',np.round(np.nanpercentile(sub[m],[5,25,50,75,95]),2))
print('dtm around',np.round(np.nanpercentile(t[i0:i1,j0:j1][~m],[5,50,95]),2),'bld frac in',b[i0:i1,j0:j1][m].mean())
np.set_printoptions(linewidth=250)
print('dsm-relief grid (rows north->south, every 2 m, z-130):')
for r in range(sub.shape[0]-1,-1,-2): print(''.join(('%3d'%int(round(sub[r,c]-130)) if (m[r,c] and not np.isnan(sub[r,c])) else ('  ~' if m[r,c] else '  .')) for c in range(0,sub.shape[1],2)))
np.savez('data/td/webster_dsm.npz',dsm=sub,mask=m,cx=CX,cy=CY,dtm=t[i0:i1,j0:j1])
