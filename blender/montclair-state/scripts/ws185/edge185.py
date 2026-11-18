# ws185: per-x transitions S->N on the 2023 class-2 intensity (0.25 m, 1.25 m median): lot asphalt -> grass strip -> turf; + curb arc fit from ortho picks
import numpy as np
I=np.load('prep/ws185_lot36N/int185_0p25m.npy'); X0,Y1,r=-352.,-190.,0.25
arc=np.array([(-318.0,-216.0),(-325.0,-219.3),(-329.7,-221.3),(-335.0,-222.7),(-345.0,-223.0)])  # 2020 ortho white curb, by eye on ortho181_grid.png (±0.3 m)
x,y=arc[:,0],arc[:,1]; A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
cx,cy,c=np.linalg.lstsq(A,b,rcond=None)[0]; R=np.sqrt(c+cx*cx+cy*cy); res=np.hypot(x-cx,y-cy)-R
print('curb arc circle c=(%.2f,%.2f) R=%.2f resid'%(cx,cy,R),res.round(2))
def curb_y(xx): return cy-np.sqrt(max(R*R-(xx-cx)**2,0))
out=[]
for xx in np.arange(-350,-317.9,1.0):
  cidx=int((xx-X0)/r); prof=np.nanmedian(I[:,cidx-1:cidx+2],axis=1)  # row0=y-190
  ys=Y1-np.arange(len(prof))*r
  cy_=curb_y(xx)
  # scan from y -234 north to the curb: last asphalt (<3800) cell, first grass (>6500) cell
  m=(ys<=cy_)&(ys>=-236)
  yy=ys[m][::-1]; pp=prof[m][::-1]
  la=yy[np.where(pp<3800)[0]].max() if (pp<3800).any() else np.nan
  fg=[v for v,p in zip(yy,pp) if p>6500 and v>la] if not np.isnan(la) else [v for v,p in zip(yy,pp) if p>6500]
  fg=min(fg) if fg else np.nan
  w=cy_-fg if not np.isnan(fg) else 0.0
  out.append((xx,cy_,la,fg,w)); print('x %6.1f curb y %7.2f | last asphalt y %7.2f | grass from y %7.2f | grass strip width %.2f'%(xx,cy_,la,fg,w))
np.savetxt('prep/ws185_lot36N/edge185.txt',np.array(out),fmt='%.2f',header='x curb_y last_asphalt_y grass_start_y grass_width (scene m) ws185')
