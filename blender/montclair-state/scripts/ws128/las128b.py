import laspy, numpy as np
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-236.,-200.,-258.,-234.
rd=laspy.open('data/lpc_2023_J5D6.laz'); crs=rd.header.parse_crs()
tr=Transformer.from_crs(crs.sub_crs_list[0] if crs.is_compound else crs,6527,always_xy=True) if (crs.to_epsg()!=6527 and 'New Jersey (ftUS)' not in crs.name) else None
P=[]
for ch in rd.chunk_iterator(3_000_000):
    ex,ey=np.asarray(ch.x),np.asarray(ch.y)
    if tr is not None: ex,ey=tr.transform(ex,ey)
    x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]])
P=np.vstack(P); g=P[P[:,3]==2]; np.save('scripts/ws128/las_E.npy',P)
for x in (-232,-228,-224,-220,-216,-212,-208,-204):
    s=g[np.abs(g[:,0]-x)<0.4]; out=[]
    for y in np.arange(-236,-257.5,-0.5):
        t=s[np.abs(s[:,1]-y)<0.25]
        out.append('%.1f:%s/%s'%(y,'%.2f'%np.median(t[:,2]) if len(t) else '-', '%d'%(np.median(t[:,4])/100) if len(t) else '-'))
    print(x,' '.join(out))
