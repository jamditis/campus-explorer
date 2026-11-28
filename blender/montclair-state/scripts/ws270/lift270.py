# ws270: new paving lift for WS268 College Ave / Lot 33 (shared by the offline check and f270a.py).
# Old (f268c): L = max(gauss(maxf(Rp,2),1.5), maxf(Rp,1)) with Rp sampled up to 2.5 m OUTSIDE the polygon -> the police-lawn foot
# (residual +0.5..+1.0 m just N of the N curb, x -365..-359) pulled the N edge up 0.6-0.7 m (soft ridge), and the 1.5 m blur
# left short lumpy swells over the W mounds by Carlisle Rd. New: only samples inside the polygon (or < 0.4 m outside) count, and
# the lift is a smooth upper envelope (iterate L = max(L0, gauss(L, s))) so it still clears every sample but rolls gently.
import numpy as np
def maxf(a,k):
    o=a.copy()
    for di in range(-k,k+1):
        for dj in range(-k,k+1): o=np.maximum(o,np.roll(np.roll(a,di,0),dj,1))
    return o
def gauss(a,s):
    k=int(3*s); w=np.exp(-0.5*(np.arange(-k,k+1)/s)**2); w/=w.sum()
    a=np.apply_along_axis(lambda r: np.convolve(np.pad(r,k,mode='edge'),w,'valid'),1,a)
    return np.apply_along_axis(lambda r: np.convolve(np.pad(r,k,mode='edge'),w,'valid'),0,a)
def lift_new(Rp,mask,s=3.0,it=60):
    L0=maxf(np.where(mask,Rp,0.0),1); L=L0.copy()
    for _ in range(it): L=np.maximum(L0,gauss(L,s))
    return L, L0
def lift_env(Rp,mask,s=1.5,it=20):
    L0=maxf(np.where(mask,Rp,0.0),1); Ln=L0.copy()
    for _ in range(it): Ln=np.maximum(L0,gauss(Ln,s))
    G=gauss(Ln,1.0)
    for _ in range(12):   # local top-up where the blur dipped under the samples
        D=np.maximum(np.where(mask,L0-G,0),0)
        if D.max()<0.002: break
        G=G+gauss(maxf(D,1),1.0)*1.6
    return G
