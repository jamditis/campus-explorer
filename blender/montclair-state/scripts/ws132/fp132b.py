import numpy as np
P=np.load('scripts/ws132/las132.npy'); b=P[P[:,3]==6]
c=np.hypot(1,0.24); u=np.array([1,-0.24])/c; v=np.array([0.24,1])/c
O=np.array([-150.,-242.])
def loc(A): d=A[:,:2]-O; return np.c_[d@u,d@v,A[:,2]]
L=loc(b); hi=L[L[:,2]>133]; lo=L[(L[:,2]>126)&(L[:,2]<=133)]
def runs(S,t,ax):
    q=S[np.abs(S[:,1-ax]-t)<0.5]
    if len(q)==0: return ''
    xs=np.sort(q[:,ax]); out=[]; s=xs[0]; p=xs[0]
    for x in xs[1:]:
        if x-p>1.6: out.append((s,p)); s=x
        p=x
    out.append((s,p)); return ' '.join('%.1f..%.1f'%r for r in out if r[1]-r[0]>1)
for t in np.arange(16,-22,-2.0): print('t%4.0f HI %-36s LO %s'%(t,runs(hi,t,0),runs(lo,t,0)))
for s in np.arange(-30,30,3.0): print('s%4.0f HI %-36s LO %s'%(s,runs(hi,s,1),runs(lo,s,1)))
