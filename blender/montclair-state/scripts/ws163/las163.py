import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-350.,-270.,-290.,-140.
P=[]
for fn in ['data/lpc_2023_J5D6.laz','north/data/USGS_LPC_NJ_NE6County_B23_J5D5.laz']:
    import os
    if not os.path.exists(fn):
        import glob; c=glob.glob('**/*J5D5*.laz',recursive=True)
        if fn.endswith('J5D5.laz') and c: fn=c[0]
        else: continue
    rd=laspy.open(fn)
    try: crs=rd.header.parse_crs()
    except Exception as e: crs=None
    print(fn, crs.name if crs else None); tr=None
    for ch in rd.chunk_iterator(2_000_000):
        ex,ey=np.asarray(ch.x),np.asarray(ch.y)
        if tr is not None: ex,ey=tr.transform(ex,ey)
        x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
        if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]].astype(np.float32))
    print(fn,'ok')
P=np.vstack(P); np.save('prep/ws163_lot3S/las163.npy',P)
print("N",len(P),np.unique(P[:,3],return_counts=True))
