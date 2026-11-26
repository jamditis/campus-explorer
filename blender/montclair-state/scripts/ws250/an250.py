import pickle, numpy as np, sys
D='scripts/ws250/'; tg=sys.argv[1]; fg=sys.argv[2]
T=pickle.load(open(D+'p250_%s.pkl'%tg,'rb')); FP=pickle.load(open(D+'p250_%s.pkl'%fg,'rb'))
xs=range(-200,-138,4); ys=range(214,138,-4)
def show(title,f):
    print(title); print('     '+''.join('%5d'%x for x in xs))
    for y in ys: print('%4d '%y+''.join(f(x,y) for x in xs))
def tl(x,y):
    l,r=T[(x,y)]; z=r.get('Terrain_LiDAR_DTM_1m')
    return '  .  ' if z is None or not np.isfinite(l) else '%5.1f'%(z-l)
show('terrain-lidar',tl)
bad=[(k,FP[k][1]['Footpaths_OSM']-T[k][1]['Terrain_LiDAR_DTM_1m']) for k in FP if 'Footpaths_OSM' in FP[k][1] and 'Terrain_LiDAR_DTM_1m' in T[k][1]]
print('footpath-terrain n',len(bad),'min %.3f max %.3f'%(min(b for _,b in bad),max(b for _,b in bad)))
a=[T[k][1]['Terrain_LiDAR_DTM_1m']-T[k][0] for k in T if 'Terrain_LiDAR_DTM_1m' in T[k][1] and np.isfinite(T[k][0]) and -190<=k[0]<=-146 and 146<=k[1]<=209]
print('core |d|>0.3:',sum(abs(v)>0.3 for v in a),'of',len(a),'max %.2f'%max(map(abs,a)))
miss=[k for k in T if 'Terrain_LiDAR_DTM_1m' not in T[k][1]]; print('terrain ray misses',len(miss))
