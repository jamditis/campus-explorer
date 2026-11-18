import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-95.,-58.,-212.,-162.
rd=laspy.open('data/lpc_2023_J5D6.laz'); P=[]
for ch in rd.chunk_iterator(1_000_000):
    x=(np.asarray(ch.x)-OE)*F; y=(np.asarray(ch.y)-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any(): P.append(np.c_[x[m],y[m],np.asarray(ch.z)[m]*0.3048006096,np.asarray(ch.classification)[m],np.asarray(ch.intensity)[m]])
P=np.vstack(P); np.save('scripts/ws142/las142.npy',P); print('N',len(P),np.unique(P[:,3],return_counts=True))
