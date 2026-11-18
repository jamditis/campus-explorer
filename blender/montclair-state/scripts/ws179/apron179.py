# ws179: WS110 S side t -4..30 (road frame of ws173/175) LiDAR class-2 single-return intensity + z map: driveway/apron at t 6-14 evidence. Read-only.
import numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
for tag in ['2023','2017']:
  P=np.load('/workspace/nj-scenes/montclair-state/prep/ws179_mulch/las179_%s.npy'%tag)
  g=P[(P[:,3]==2)]
  q=g[:,:2]-A; t=q@T; s=q@N
  print('== %s class-2 intensity (k, median per 1 m cell; "." none); rows s 0..-26 (N->S), cols t -4..29'%tag)
  print('      '+''.join('%3d'%c if c%4==0 else '   ' for c in range(-4,30)))
  for sr in range(0,-27,-1):
    line=''
    for tc in range(-4,30):
      m=(t>=tc)&(t<tc+1)&(s<=sr)&(s>sr-1)
      line+=('%3d'%round(np.median(g[m,4])/1000)) if m.sum() else '  .'
    print('%5d '%sr+line)
  # z profile across s at t bands
  print('-- median z by s (rows) for t bands 0-6 / 6-14 / 14-22')
  for sr in range(-6,-25,-1):
    out=[]
    for a,b in [(0,6),(6,14),(14,22)]:
      m=(t>=a)&(t<b)&(s<=sr)&(s>sr-1); out.append('%.2f'%np.median(g[m,2]) if m.sum() else ' -  ')
    print('%5d  %s'%(sr,'  '.join(out)))
  c6=P[P[:,3]==6]; q=c6[:,:2]-A; t6=q@T; s6=q@N; m=(t6>-4)&(t6<30)&(s6<0)&(s6>-30)
  print('class6 (building) in window:',m.sum(), ('t %.1f..%.1f s %.1f..%.1f'%(t6[m].min(),t6[m].max(),s6[m].min(),s6[m].max())) if m.sum() else '')
