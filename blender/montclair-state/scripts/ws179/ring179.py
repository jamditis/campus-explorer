# ws179: ground-return intensity in rings around the LiDAR-placed WS165/WS166 trees (mulch ring evidence). Read-only.
import numpy as np
D='/workspace/nj-scenes/montclair-state/prep/ws179_mulch/'
T={'WS166_aisle_bed':(-303.5,-250.5),'WS166_row1':(-293.5,-251.5),'WS166_row2':(-286.5,-253.5),'WS166_row3':(-276.5,-255.5),
   'WS166_lawn_N':(-283.5,-246.5),'WS165_aisle_mouth':(-298.58,-240.85)}
for tag in ['2023','2017']:
  P=np.load(D+'las179_%s.npy'%tag); g=P[P[:,3]==2]; v=P[P[:,3]==1]
  print('==',tag,'ground',len(g))
  for k,(cx,cy) in T.items():
    d=np.hypot(g[:,0]-cx,g[:,1]-cy); row=[]
    for a,b in [(0,0.75),(0.75,1.5),(1.5,2.5),(2.5,4),(4,6)]:
      m=(d>=a)&(d<b); row.append('%.2g-%.2g:n%d I%s'%(a,b,m.sum(),('%5.0f'%np.median(g[m,4])) if m.sum() else '  -  '))
    # trunk refinement: lowest class-1 points 0.5-2.5 m above ground near the crown peak
    dv=np.hypot(v[:,0]-cx,v[:,1]-cy); gz=np.median(g[d<4,2]) if (d<4).any() else np.nan
    m=(dv<3)&(v[:,2]-gz>0.4)&(v[:,2]-gz<2.2)
    tr=('trunk~(%.1f,%.1f) n%d'%(v[m,0].mean(),v[m,1].mean(),m.sum())) if m.sum()>=3 else 'trunk n%d'%m.sum()
    print('%-18s gz %.2f | %s | %s'%(k,gz,' | '.join(row),tr))
