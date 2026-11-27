# ws259 UNIFY W64: 2023 J5D6 LiDAR ground (class 2) + all-return max W of the WS103 walk S half (x -264..-240, y -242..-214), 1 m cells
import laspy, numpy as np
OE,ON=575880.0,738340.0; F=1200/3937
X0,X1,Y0,Y1=-264.,-240.,-242.,-214.
G=[];A=[]
rd=laspy.open('data/lpc_2023_J5D6.laz')  # x >= -268 is in J5D6
for ch in rd.chunk_iterator(2_000_000):
    x=(np.asarray(ch.x)-OE)*F; y=(np.asarray(ch.y)-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
    if m.any():
        c=np.asarray(ch.classification)[m]; z=np.asarray(ch.z)[m]*0.3048006096
        A.append(np.c_[x[m],y[m],z,c])
A=np.vstack(A); print('pts',len(A),'classes',np.unique(A[:,3],return_counts=True))
g=A[A[:,3]==2]
for y in (-238,-234,-230,-226,-222,-218):
    row=[]
    for x in range(-262,-240,2):
        s=g[(np.abs(g[:,0]-x)<1)&(np.abs(g[:,1]-y)<1)]
        row.append(round(float(np.median(s[:,2])),2) if len(s) else None)
    print('W64 ground y',y,'x -262..-242 step 2:',row)
