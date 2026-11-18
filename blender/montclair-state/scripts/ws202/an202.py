import numpy as np,sys,collections
d=np.load(sys.argv[1]); Z,O,N,xs,ys=d['Z'],d['O'],list(d['names']),d['xs'],d['ys']
print([ (i,n,int((O==i).sum())) for i,n in enumerate(N)])
res=collections.Counter(); pts=[]
for ax in (0,1):
    Zm=np.moveaxis(Z,ax,0); Om=np.moveaxis(O,ax,0)
    st=Zm[2:]-2*Zm[1:-1]+Zm[:-2]
    # also first-order step across change, slope corrected using cell before
    ch=(Om[2:]!=Om[1:-1])
    idx=np.argwhere(ch&(np.abs(st)>0.003))
    for a,b in idx:
        i,j=(a+1,b) if ax==0 else (b,a+1)
        res[(N[Om[a+1,b]][:6],N[Om[a+2,b]][:6])]+=1; pts.append((xs[i],ys[j],st[a,b],N[Om[a+1,b]][:5],N[Om[a+2,b]][:5]))
print(res.most_common(12))
pts=np.array([(p[0],p[1],p[2]) for p in pts])
if len(pts):
  H,xe,ye=np.histogram2d(pts[:,0],pts[:,1],bins=[np.arange(-242,-223,1),np.arange(-107,-93,1)])
  for k in np.argsort(-H.ravel())[:15]:
    i,j=np.unravel_index(k,H.shape); print('cell',xe[i],ye[j],int(H[i,j]))
# also non-seam curvature bumps inside lot
A=np.isin(O,[i for i,n in enumerate(N) if n[:4] in('WS75','WS80','WS81','WS94','WS96')])
c=np.abs(Z[2:,1:-1]+Z[:-2,1:-1]+Z[1:-1,2:]+Z[1:-1,:-2]-4*Z[1:-1,1:-1])
print('lot lap p50 %.4f p99 %.4f n>4mm %d'%(np.nanpercentile(c[A[1:-1,1:-1]],50),np.nanpercentile(c[A[1:-1,1:-1]],99),(c[A[1:-1,1:-1]]>0.004).sum()))
