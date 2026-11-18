# ws179: same rings but SINGLE-return ground points only (no canopy attenuation) + control: multi-return ground under canopy away from any tree.
import numpy as np
D='/workspace/nj-scenes/montclair-state/prep/ws179_mulch/'
T={'WS166_aisle_bed':(-303.7,-249.8),'WS166_row1':(-294.5,-252.5),'WS166_row2':(-286.5,-253.5),'WS166_row3':(-276.5,-255.5),
   'WS166_lawn_N':(-282.9,-244.5),'WS165_aisle_mouth':(-298.6,-239.1)}
for tag in ['2023','2017']:
  P=np.load(D+'las179_%s.npy'%tag); g=P[P[:,3]==2]
  s=g[g[:,6]==1]; mlt=g[g[:,6]>1]
  print('==',tag,'ground single',len(s),'multi',len(mlt),'| all-lawn ref single median I (6-10 m ring of row trees):',end=' ')
  for k,(cx,cy) in T.items():
    out=[]
    for nm,G in [('single',s),('multi',mlt)]:
      d=np.hypot(G[:,0]-cx,G[:,1]-cy); r=[]
      for a,b in [(0,1),(1,2),(2,3),(3,5),(5,8)]:
        m=(d>=a)&(d<b); r.append('%d:%s(n%d)'%(b,('%5.0f'%np.median(G[m,4])) if m.sum() else '  -  ',m.sum()))
      out.append(nm+' '+' '.join(r))
    print('\n%-18s %s\n%-18s %s'%(k,out[0],'',out[1]),end='')
  print()
