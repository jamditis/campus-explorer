import numpy as np,sys
for f in sys.argv[1:]:
    d=np.load(f); Z,O,N=d['Z'],d['O'],list(d['names'])
    ks=[i for i,n in enumerate(N) if n[:4] in ('WS75','WS80','WS81','WS94','WS96')]
    A=np.isin(O,ks); out=[]
    for ax in (0,1):
        Zm=np.moveaxis(Z,ax,0); Om=np.moveaxis(O,ax,0); Am=np.moveaxis(A,ax,0)
        # slope-corrected step: z[i+1]-2z[i]+z[i-1]
        st=np.abs(Zm[2:]-2*Zm[1:-1]+Zm[:-2]); ch=(Om[2:]!=Om[1:-1])&Am[2:]&Am[1:-1]&Am[:-2]
        out+=list(st[ch])
    out=np.array(out); 
    lk=[i for i,n in enumerate(N) if n.startswith(('Terrain','WS68','Roads','Footp'))]
    print(f.split('/')[-1],'seam 2nd-diff p50 %.4f p90 %.4f max %.3f n>5mm %d n>1cm %d'%(np.percentile(out,50),np.percentile(out,90),out.max(),(out>0.005).sum(),(out>0.01).sum()),'| non-lot top cells',int(np.isin(O,lk).sum()))
