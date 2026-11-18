import laspy, numpy as np
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-254.,-229.,-252.,-224.
rd=laspy.open('data/lpc_2023_J5D6.laz'); crs=rd.header.parse_crs(); name=crs.name if crs else '?'
tr=None
if crs is not None and crs.to_epsg()!=6527 and 'New Jersey (ftUS)' not in name:
    tr=Transformer.from_crs(crs.sub_crs_list[0] if crs.is_compound else crs,6527,always_xy=True)
vf=0.3048006096 if ('ftUS' in name.split('+')[-1] or 'foot' in name.split('+')[-1].lower()) else 1.0
P=[]
for ch in rd.chunk_iterator(3_000_000):
    ex,ey=np.asarray(ch.x),np.asarray(ch.y)
    if tr is not None: ex,ey=tr.transform(ex,ey)
    x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*vf,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]])
P=np.vstack(P); np.save('scripts/ws128/las_pts.npy',P); print('pts',len(P),name)
g=P[P[:,3]==2]
for y in (-250,-246,-244,-242,-240,-238,-236,-232,-228):
    s=g[np.abs(g[:,1]-y)<0.35]; out=[]
    for x in np.arange(-253,-232,0.5):
        t=s[np.abs(s[:,0]-x)<0.25]
        out.append('%.1f:%s/%s'%(x,'%.2f'%np.median(t[:,2]) if len(t) else '-', '%d'%np.median(t[:,4]) if len(t) else '-'))
    print(y,' '.join(out))
