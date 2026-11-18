import numpy as np,sys
from scipy.ndimage import median_filter
d=np.load(sys.argv[1]); Z,O,N,xs,ys=d['Z'],d['O'],list(d['names']),d['xs'],d['ys']
L=[i for i,n in enumerate(N) if n[:4] in('WS75','WS80','WS81','WS94','WS96','WS76','WS19')]
A=np.isin(O,L)
Zf=np.where(A,Z,np.nan)
# local plane residual: z - median of 0.4 m window (approx plane on gentle slope)
k=int(0.4/(xs[1]-xs[0]))|1
M=median_filter(np.nan_to_num(Zf,nan=-999),size=k)
R=np.where(A&(M>-900),Z-M,np.nan)
X,Y=np.meshgrid(xs,ys,indexing='ij')
for thr in (0.002,0.003,0.005):
    lo=R<-thr; print('low>%gmm'%(thr*1000),int(lo.sum()),'high',int((R>thr).sum()))
lo=R<-0.002
for i in L:
    s=lo&(O==i); 
    if s.sum(): print(N[i][:8],'low cells',int(s.sum()),'mean %.4f'%np.nanmean(R[s]))
# where
H,xe,ye=np.histogram2d(X[lo],Y[lo],bins=[np.arange(-239,-230,0.5),np.arange(-84.5,-77,0.5)])
print(np.flipud(H.T.astype(int)))
np.savez('r202i.npz',R=R,xs=xs,ys=ys,O=O)
