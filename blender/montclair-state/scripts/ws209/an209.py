import json,numpy as np
def tri_interp(V,F,pts):
    out=np.full(len(pts),np.nan)
    A=V[F]
    for k,(x,y) in enumerate(pts):
        a,b,c=A[:,0,:],A[:,1,:],A[:,2,:]
        d=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1])
        l1=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/d
        l2=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/d
        l3=1-l1-l2; m=(l1>=-1e-6)&(l2>=-1e-6)&(l3>=-1e-6)
        if m.any(): z=(l1*a[:,2]+l2*b[:,2]+l3*c[:,2])[m]; out[k]=z.max()
    return out
def polys_to_tris(P):
    V=[];F=[]
    for p in P:
        i0=len(V); V+=p
        for j in range(1,len(p)-1): F.append([i0,i0+j,i0+j+1])
    return np.array(V),np.array(F)
