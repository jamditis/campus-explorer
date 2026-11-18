import json,numpy as np
O=json.load(open('scripts/ws102/osm102.json'))['1557427669']['p']
P=np.array(O)[::-1]; seg=np.diff(P,axis=0); L=np.hypot(*seg.T); C=np.r_[0,np.cumsum(L)]
z=np.load('data/pts_crop.npz'); x,y,h,cl=z['x'],z['y'],z['z'],z['c']
m=(x>-265)&(x<-195)&(y>-260)&(y<-150)&(cl==2); x,y,h=x[m],y[m],h[m]
# project to (s,off) using the polyline
best_s=np.full(len(x),1e9);best_o=np.full(len(x),1e9);bd=np.full(len(x),1e9)
for k in range(len(L)):
    d=seg[k]/L[k]; n=np.array([d[1],-d[0]]); rx=x-P[k,0]; ry=y-P[k,1]; t=rx*d[0]+ry*d[1]; o=rx*n[0]+ry*n[1]
    tt=np.clip(t,0,L[k]); dist=np.hypot(rx-tt*d[0],ry-tt*d[1]); u=dist<bd
    bd[u]=dist[u]; best_s[u]=C[k]+t[u]; best_o[u]=o[u]
np.savez('scripts/ws102/lid_so.npz',s=best_s,o=best_o,z=h,x=x,y=y)
print('pts',len(x))
offs=np.arange(-9,9.1,1.0)
print('   s  '+' '.join('%6.1f'%v for v in offs))
for s in range(-4,96,4):
    r=[]
    for o in offs:
        q=(abs(best_s-s)<1.0)&(abs(best_o-o)<0.5); r.append(np.median(h[q]) if q.sum()>=3 else np.nan)
    print('%5d '%s+' '.join('%6.2f'%v if v==v else '   .  ' for v in r))
