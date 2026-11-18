import laspy, numpy as np, sys
OE,ON=575880.0,738340.0; F=1200/3937
import os
X0,X1,Y0,Y1=[float(v) for v in os.environ.get("BOX","-240,-150,-310,-260").split(",")]
for tag,f in [('2017','/workspace/nj-scenes/montclair-state/north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz'),('2023','/workspace/nj-scenes/montclair-state/data/lpc_2023_J5D6.laz')]:
  P=[]; rd=laspy.open(f); ft=rd.header.x_scale
  for ch in rd.chunk_iterator(2_000_000):
    ex,ey=np.asarray(ch.x),np.asarray(ch.y)
    x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]].astype(np.float32))
  P=np.vstack(P) if P else np.zeros((0,5),np.float32); np.save('/workspace/nj-scenes/montclair-state/prep/ws175_scurb/las175%s_%s.npy'%(os.environ.get("SUF",""),tag),P)
  print(tag,'N',len(P),flush=True)
