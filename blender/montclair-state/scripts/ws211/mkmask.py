import json,numpy as np
from PIL import Image,ImageDraw
P=json.load(open('paint.json'))
X0,X1,Y0,Y1=-256.0,-214.0,-88.0,-62.0; SS=0.005; OUT=0.01
def sline(x): return -86.5+( -91.5+86.5)*(x+254.5)/(36.5)   # Sprague N row north edge
def keepW(c): return X0+0.3<c[0]<X1-0.3 and Y0+0.3<c[1]<Y1-0.3 and c[1]>sline(c[0])+1.0 and not (c[0]<-249.5 and c[1]>-66.5)
W=int((X1-X0)/SS); H=int((Y1-Y0)/SS)
R=Image.new('L',(W,H)); G=Image.new('L',(W,H)); dR=ImageDraw.Draw(R); dG=ImageDraw.Draw(G)
def px(v): return ((v[0]-X0)/SS,(Y1-v[1])/SS)
sel={}
for nm,d in P.items():
    V=np.array(d['V']); keep=[]
    for fi,p in enumerate(d['P']):
        c=V[p,:2].mean(0)
        if 'white_ortho' in nm and not keepW(c): continue
        if not (X0<c[0]<X1 and Y0<c[1]<Y1): print('OUT',nm,fi,c); continue
        keep.append(fi); pts=[px(V[i]) for i in p]
        (dG if 'blue' in nm else dR).polygon(pts,fill=255)
    sel[nm]=keep; print(nm,len(d['P']),'->',len(keep))
json.dump(sel,open('moved_faces.json','w'))
s=int(OUT/SS)
r=np.asarray(R.resize((W//s,H//s),Image.BOX)); g=np.asarray(G.resize((W//s,H//s),Image.BOX))
g=np.where(r>0,np.maximum(g,0),g)
Image.fromarray(np.dstack([r,g,np.zeros_like(r)]).astype(np.uint8)).save('/workspace/nj-scenes/montclair-state/data/ws211_access_lot_paint_mask.png')
print('mask',W//s,H//s)
# --- ws211: join gapped stall lines (ws76 drape dropped samples off-asphalt -> line breaks) into continuous straight lines
import scipy.ndimage as nd
g0=np.asarray(G)>127; lab,n=nd.label(g0); segs=[]
for i in range(1,n+1):
    ys,xs=np.where(lab==i)
    if len(xs)<160: continue
    P2=np.c_[X0+xs*SS, Y1-ys*SS]; c=P2.mean(0); u,sv,vt=np.linalg.svd(P2-c,full_matrices=False)
    if sv[0]<2.5*sv[1]: continue  # square
    d=vt[0]; d=d if d[1]>0 else -d; pr=(P2-c)@d; w=np.ptp((P2-c)@np.array([-d[1],d[0]]))
    segs.append((c,d,pr.min(),pr.max(),w))
t=np.array([0.969,-0.249]); used=[False]*len(segs); groups=[]
for i,(c,d,a,b,w) in enumerate(segs):
    if used[i]: continue
    grp=[i]; used[i]=True
    for j in range(i+1,len(segs)):
        if used[j]: continue
        c2,d2=segs[j][0],segs[j][1]
        perp=abs((c2-c)@np.array([-d[1],d[0]]))
        short=(segs[j][3]-segs[j][2])<1.2 or (b-a)<1.2
        if perp<0.25 and (abs(d@d2)>0.995 or (short and abs(d@d2)>0.95)): grp.append(j); used[j]=True
    groups.append(grp)
Gd=ImageDraw.Draw(G); nj=0
for grp in groups:
    if len(grp)<2: continue
    c,d=segs[grp[0]][0],segs[grp[0]][1]
    ends=[]
    for k in grp:
        ck,dk,a,b,w=segs[k]; ends+= [ck+dk*a, ck+dk*b]
    E=np.array(ends); pr=(E-c)@d; A=c+d*pr.min(); B=c+d*pr.max(); wid=np.median([segs[k][4] for k in grp])
    if np.linalg.norm(B-A)>7.5: print('SKIP long',A,B); continue
    Gd.line([px(A),px(B)],fill=255,width=max(1,int(round(wid/SS)))); nj+=1; print('JOIN',len(grp),'segs ->',np.round(A,2),np.round(B,2),'len %.2f w %.3f'%(np.linalg.norm(B-A),wid))
print('joined',nj)
g=np.asarray(G.resize((W//s,H//s),Image.BOX))
Image.fromarray(np.dstack([r,g,np.zeros_like(r)]).astype(np.uint8)).save('/workspace/nj-scenes/montclair-state/data/ws211_access_lot_paint_mask.png')
# --- tiles <=1024 px so render texture limits (1024) never downsample the paint
full=np.dstack([r,g,np.zeros_like(r)]).astype(np.uint8); HH,WW=full.shape[:2]; T=1000; OV=4; tiles=[]
import os
for f in os.listdir('/workspace/nj-scenes/montclair-state/data'):
    if f.startswith('ws211_mask_tile_'): os.remove('/workspace/nj-scenes/montclair-state/data/'+f)
for ty in range(0,HH,T):
    for tx in range(0,WW,T):
        c0,c1=max(0,tx-OV),min(WW,tx+T+OV); r0,r1=max(0,ty-OV),min(HH,ty+T+OV)
        sub=full[r0:r1,c0:c1]
        if sub.max()==0: continue
        nm=f'ws211_mask_tile_{tx//T}_{ty//T}.png'; Image.fromarray(sub).save('/workspace/nj-scenes/montclair-state/data/'+nm)
        tiles.append((nm, X0+c0*OUT, X0+c1*OUT, Y1-r1*OUT, Y1-r0*OUT))
json.dump(tiles,open('/workspace/nj-scenes/montclair-state/data/ws211_mask_tiles.json','w')); print('tiles',len(tiles))
