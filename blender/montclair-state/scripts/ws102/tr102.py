import json,numpy as np
from PIL import Image
o=np.asarray(Image.open('data/ortho2020.png').convert('RGB')).astype(float);S=4.096
def samp(x,y):
    px=(x+250)*S; py=(250-y)*S; i=int(py); j=int(px)
    return o[i-1:i+2,j-1:j+2].reshape(-1,3).mean(0)
O=json.load(open('scripts/ws102/osm102.json'))['1557427669']['p']
P=np.array(O)[::-1]  # north->south
# param by arc
seg=np.diff(P,axis=0); L=np.hypot(*seg.T); C=np.r_[0,np.cumsum(L)]
def at(s):
    k=min(np.searchsorted(C,s)-1,len(L)-1); k=max(k,0); t=(s-C[k])/L[k]; p=P[k]+t*seg[k]; d=seg[k]/L[k]; return p,d
for s in np.arange(0,100,4):
    p,d=at(s); n=np.array([d[1],-d[0]])  # right-hand normal (west-ish?)
    row=''
    for off in np.arange(-12,12.1,0.5):
        q=p+n*off; r,g,b=samp(*q); br=(r+g+b)/3; sat=max(r,g,b)-min(r,g,b)
        ch='#' if br>175 else ('g' if g>r+8 and g>b else ('r' if r>g+15 else ('=' if br>115 else '.')))
        row+=ch
    print('%5.1f (%7.1f,%7.1f) n=(%.2f,%.2f) %s'%(s,p[0],p[1],n[0],n[1],row))
