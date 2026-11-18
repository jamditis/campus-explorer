# ws179: College Ave S-of-Normal leg (OSM 232846669) cross-profiles in the ws173 road frame: z + intensity vs t at s bands, for curb edges. Read-only.
import numpy as np
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N); T=np.array([N[1],-N[0]])
P=np.load('/workspace/nj-scenes/montclair-state/prep/ws179_mulch/las179_2023.npy'); g=P[P[:,3]==2]
q=g[:,:2]-A; t=q@T; s=q@N
for a,b in [(-12,-10.5),(-13.5,-12),(-16,-14),(-20,-17),(-25,-22)]:
  print('== s %.1f..%.1f   t: z(cm rel. min) / I(k)'%(a,b))
  zs=[];Is=[]
  for tc in np.arange(0,20,0.5):
    m=(t>=tc)&(t<tc+0.5)&(s>=a)&(s<b)
    zs.append(np.median(g[m,2]) if m.sum()>2 else np.nan); Is.append(np.median(g[m,4])/1000 if m.sum()>2 else np.nan)
  zs=np.array(zs); z0=np.nanmin(zs)
  print('  t  '+' '.join('%4.1f'%x for x in np.arange(0,20,0.5)))
  print('  dz '+' '.join('%4d'%round((z-z0)*100) if z==z else '   .' for z in zs))
  print('  I  '+' '.join('%4.0f'%i if i==i else '   .' for i in Is))
