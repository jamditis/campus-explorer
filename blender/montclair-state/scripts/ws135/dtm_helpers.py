Z=np.load(D+'dtm134.npy'); ZX0,ZY0,_=np.load(D+'dtm134_xy.npy')
_nan=np.isnan(Z)
if _nan.any():
    _jj,_ii=np.nonzero(~_nan); _vals=Z[~_nan]
    for _j,_i in zip(*np.nonzero(_nan)):
        _k=np.argmin((_jj-_j)**2+(_ii-_i)**2); Z[_j,_i]=_vals[_k]
def dtm(x,y):
    fx=(x-ZX0); fy=(y-ZY0); i=int(min(max(math.floor(fx),0),Z.shape[1]-2)); j=int(min(max(math.floor(fy),0),Z.shape[0]-2))
    tx=fx-i; ty=fy-j
    return float(Z[j,i]*(1-tx)*(1-ty)+Z[j,i+1]*tx*(1-ty)+Z[j+1,i]*(1-tx)*ty+Z[j+1,i+1]*tx*ty)
def pip(poly,x,y):
    ins=False; n_=len(poly)
    for k in range(n_):
        x1,y1=poly[k]; x2,y2=poly[(k+1)%n_]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1)+x1: ins=not ins
    return ins
