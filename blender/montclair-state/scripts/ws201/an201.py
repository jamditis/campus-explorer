import numpy as np,sys
from numpy.lib.stride_tricks import sliding_window_view as sw
for f in sys.argv[1:]:
    d=np.load(f); Z,O,N=d['Z'],d['O'],list(d['names'])
    k75,k80,k81=[N.index([n for n in N if n.startswith(p)][0]) for p in ('WS75','WS80','WS81')]
    M=np.where(np.isin(O,[k75,k80]),Z,np.nan); P=np.pad(M,3,constant_values=np.nan); nb=np.nanmax(sw(P,(7,7)),axis=(2,3))
    m=O==k81; dd=(nb-Z)[m]
    A=np.isin(O,[k75,k80,k81]); dx=np.abs(np.diff(Z,axis=0)); ch=(O[1:]!=O[:-1])&A[1:]&A[:-1]
    print(f,'WS81 top cells',m.sum(),'below-neighbour p50/p90/max',np.nanpercentile(dd,[50,90,100]).round(3),'| steps at obj change >1cm',int((dx[ch]>0.01).sum()),'of',ch.sum(),'max',dx[ch].max().round(3))
