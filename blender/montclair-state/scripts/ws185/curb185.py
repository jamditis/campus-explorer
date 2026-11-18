# ws185: fit the Sprague turf-edge white curb arc (2020 ortho, 15 px/m) + zone stats from 2023 intensity
import numpy as np
from PIL import Image
a=np.asarray(Image.open('prep/ws181_lot36/ortho181.jpg').convert('RGB')).astype(float)
H,W,_=a.shape; s=W/60.0
def px(x,y): return int((x+355)*s), int((-200-y)*s)
L=a.mean(2); sat=a.max(2)-a.min(2)
pts=[]
for x in np.arange(-352,-317,0.5):
  c=int((x+355)*s)
  r0,r1=int((200-212)*-s),int((200-226)*-s)  # y -212..-226
  col=L[r0:r1,c]; sc=sat[r0:r1,c]
  m=(col>150)&(sc<40)
  if m.any():
    k=np.argmax(np.where(m,col,0)); y=-200-(r0+k)/s; pts.append((x,y,col[k]))
P=np.array(pts); print('white-curb samples',len(P))
for p in P[::4]: print('  x %.1f y %.2f L %.0f'%tuple(p))
# circle fit (algebraic)
x,y=P[:,0],P[:,1]; A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
cx,cy,c=np.linalg.lstsq(A,b,rcond=None)[0]; R=np.sqrt(c+cx*cx+cy*cy)
res=np.hypot(x-cx,y-cy)-R
print('circle c=(%.2f,%.2f) R=%.2f resid rms %.2f max %.2f'%(cx,cy,R,np.sqrt((res**2).mean()),abs(res).max()))
ok=abs(res)<0.6; x,y=x[ok],y[ok]; A=np.c_[2*x,2*y,np.ones_like(x)]; b=x*x+y*y
cx,cy,c=np.linalg.lstsq(A,b,rcond=None)[0]; R=np.sqrt(c+cx*cx+cy*cy); res=np.hypot(x-cx,y-cy)-R
print('refit n=%d c=(%.2f,%.2f) R=%.2f rms %.2f'%(ok.sum(),cx,cy,R,np.sqrt((res**2).mean())))
np.savetxt('prep/ws185_lot36N/curb_arc185.txt',np.c_[x,y],fmt='%.2f',header='ortho2020 white curb samples (scene m); circle c=(%.2f,%.2f) R=%.2f'%(cx,cy,R))
# intensity zone stats
I=np.load('prep/ws185_lot36N/int185_0p25m.npy'); X0,Y1,r=-352.,-190.,0.25
def zone(x0,x1,y0,y1):
  c0,c1=int((x0-X0)/r),int((x1-X0)/r); r0,r1=int((Y1-y1)/r),int((Y1-y0)/r)
  return np.nanpercentile(I[r0:r1,c0:c1],[10,50,90]).round(0)
for nm,z in [('turf field x-345..-325 y-212..-200',(-345,-325,-212,-200)),('E turf band x-321..-318 y-208..-195',(-321,-318,-208,-195)),
             ('apron x-316..-313 y-210..-195',(-316,-313,-210,-195)),('strip x-350..-336 y-226..-223',(-350,-336,-226,-223)),
             ('tongue x-330..-326 y-219..-216',(-330,-326,-219,-216)),('lot x-330..-320 y-232..-225',(-330,-320,-232,-225))]:
  print(nm,zone(*z))
