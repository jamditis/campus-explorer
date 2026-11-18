# ws179 parallel: 2023 + 2017 LiDAR extract for WS166 street-tree mulch-ring evidence + WS110 S apron t 6-14 (read-only, no Blender)
import laspy, numpy as np, os
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-315.,-240.,-295.,-235.
D='/workspace/nj-scenes/montclair-state/'
for tag,fs in [('2023',['north/data/USGS_LPC_NJ_NE6County_B23_J5D5.laz','data/lpc_2023_J5D6.laz']),
               ('2017',['north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D5.laz','north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz'])]:
  P=[]
  for f in fs:
    rd=laspy.open(D+f)
    for ch in rd.chunk_iterator(1_000_000):
      ex,ey=np.asarray(ch.x),np.asarray(ch.y)
      x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
      if m.any():
        rn=np.asarray(ch.return_number)[m]; nr=np.asarray(ch.number_of_returns)[m]
        P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m],rn,nr].astype(np.float32))
  P=np.vstack(P); np.save(D+'prep/ws179_mulch/las179_%s.npy'%tag,P)
  print(tag,'N',len(P),np.unique(P[:,3],return_counts=True),flush=True)
