import numpy as np, json
from math import exp
B='/workspace/nj-scenes/montclair-state/scripts/ws102/'
P=np.array(json.load(open(B+'osm102.json'))['1557427669']['p'])[::-1]; seg=np.diff(P,axis=0); L=np.hypot(*seg.T); C=np.r_[0,np.cumsum(L)]
def raw(s):
    k=max(min(np.searchsorted(C,s)-1,len(L)-1),0); return P[k]+(s-C[k])*seg[k]/L[k]
S0,S1=0.0,88.5
ss=np.arange(-6,S1+6.01,0.5); cl=np.array([raw(s) for s in ss])
w=np.array([exp(-0.5*(i*0.5/2.0)**2) for i in range(-8,9)]); w/=w.sum()
cs=np.stack([np.convolve(np.pad(cl[:,i],8,mode='edge'),w,'valid') for i in range(2)],1)
def frame(s):
    i=np.interp(s,ss,np.arange(len(ss))); a=int(min(i,len(ss)-2)); t=i-a
    p=cs[a]*(1-t)+cs[a+1]*t; d=cs[min(a+1,len(ss)-1)]-cs[max(a-1,0)]; d=d/np.linalg.norm(d); n=np.array([d[1],-d[0]]); return p,n
SF=np.arange(-6,S1+6,0.25); FR=[frame(s) for s in SF]; PP=np.array([f[0] for f in FR]); NN=np.array([f[1] for f in FR])
def so(q):
    dd=np.hypot(*(PP-q[:2]).T); a=int(np.argmin(dd)); return SF[a], float((q[:2]-PP[a])@NN[a])
