import numpy as np,sys
from scipy.ndimage import generic_filter, median_filter
d=np.load(sys.argv[1]); Z,O,N,xs,ys=d['Z'],d['O'],list(d['names']),d['xs'],d['ys']
L=[i for i,n in enumerate(N) if n[:4] in('WS75','WS80','WS81','WS94','WS96','WS76','WS19','WS82') and 'paint' not in n.lower()]
A=np.isin(O,L); k=int(0.4/(xs[1]-xs[0]))|1
Zf=np.where(A,Z,np.nan)
M=generic_filter(Zf,np.nanmedian,size=k,mode='nearest') if Z.size<60000 else median_filter(np.nan_to_num(Zf,nan=-999),size=k)
R=np.where(A&(M>-900),Z-M,np.nan)
np.savez(sys.argv[2],R=R,xs=xs,ys=ys,O=O,Z=Z)
print('low>1.5mm',int((R<-0.0015).sum()),'low>3mm',int((R<-0.003).sum()))
