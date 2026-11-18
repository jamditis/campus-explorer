# ws211c: rebuild the accessible-lot paint mask to the 2020 ortho stall-by-stall layout (rows A/B: 9 ISA stalls each,
# stalls ~2.8 m, paired around shared hatched access aisles ~1.75 m; symbols at the detected ortho positions).
import json,numpy as np
from PIL import Image,ImageDraw
X0,X1,Y0,Y1=-256.0,-214.0,-88.0,-62.0; SS=0.005; OUT=0.01
W=int((X1-X0)/SS); H=int((Y1-Y0)/SS)
P=json.load(open('paint.json')); D=json.load(open('rows_detect.json'))
t=np.array([0.969,-0.249]); t/=np.linalg.norm(t); n=np.array([-t[1],t[0]])
def px(v): return ((v[0]-X0)/SS,(Y1-v[1])/SS)
# old raster (for symbol stamps)
old=np.asarray(Image.open('/workspace/nj-scenes/montclair-state/data/ws211_access_lot_paint_mask.png').resize((W,H),Image.NEAREST)).copy()
R=np.zeros((H,W),np.uint8); G=np.zeros((H,W),np.uint8)
VB=np.array(P['WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED']['V'])[:,:2]
SW=2.8; LW=0.12; HW=0.10; HP=0.55
gimg=Image.new('L',(W,H)); gd=ImageDraw.Draw(gimg)
def quad(o,ta,tb,na,nb): return [px(o+t*ta+n*na),px(o+t*tb+n*na),px(o+t*tb+n*nb),px(o+t*ta+n*nb)]
log=[]
for row in ('A','B'):
    o=np.array(D[row]['o']); real=np.array(D[row]['real']); model=np.array(D[row]['model'])
    # row axis fit through real symbols (slight rotation vs model)
    rt=(real-o)@t; rn=(real-o)@n; a,b=np.polyfit(rt,rn,1)
    # line n-extent from the old blue line verts of this row
    vb=VB[np.abs((VB-o)@n)<4.0]; nv=(vb-o)@n; tv=(vb-o)@t
    n0,n1=np.percentile(nv,0.5),np.percentile(nv,99.5)
    order=np.argsort(rt); rt=rt[order]; real=real[order]
    bounds=set(); aisles=[]
    for i,s in enumerate(rt):
        bounds.add(round(s-SW/2,3)); bounds.add(round(s+SW/2,3))
    for i in range(len(rt)-1):
        if rt[i+1]-rt[i]>3.6: aisles.append((rt[i]+SW/2,rt[i+1]-SW/2))
    # end aisle E of the last stall (hatched zone visible at both row E ends in the 2020 ortho; row A UNVERIFIED)
    aw=np.mean([b2-a2 for a2,b2 in aisles]); aisles.append((rt[-1]+SW/2,rt[-1]+SW/2+aw)); bounds.add(round(rt[-1]+SW/2+aw,3))
    def nof(tt): return a*tt+b  # local n offset of the row axis
    bl=sorted(bounds); merged=[]
    for v in bl:
        if merged and v-merged[-1][-1]<0.4: merged[-1].append(v)
        else: merged.append([v])
    bounds=[float(np.mean(m)) for m in merged]
    for bt in bounds:
        sh=nof(bt)
        gd.polygon(quad(o,bt-LW/2,bt+LW/2,n0+sh,n1+sh),fill=255)
    for (ta,tb) in aisles:
        sh=nof((ta+tb)/2)
        # 45 deg hatch inside the aisle rectangle
        tmp=Image.new('L',(W,H)); td=ImageDraw.Draw(tmp)
        k=n0
        while k<n1+(tb-ta):
            p1=o+t*ta+n*(k+sh); p2=o+t*tb+n*(k-(tb-ta)+sh)
            td.line([px(p1),px(p2)],fill=255,width=int(HW/SS)); k+=HP
        m=Image.new('L',(W,H)); ImageDraw.Draw(m).polygon(quad(o,ta,tb,n0+sh,n1+sh),fill=255)
        gimg.paste(tmp,(0,0),Image.fromarray((np.asarray(m)&np.asarray(tmp)).astype(np.uint8)))
    # move each symbol stamp (blue square + white glyph) from model centre to detected centre
    mo=model[np.argsort((model-o)@t)]
    for m_c,r_c in zip(mo,real):
        cx,cy=px(m_c); hw=int(0.9/SS); x0p,y0p=int(cx)-hw,int(cy)-hw
        st=old[y0p:y0p+2*hw,x0p:x0p+2*hw]
        nx,ny=px(r_c); X=int(nx)-hw; Y=int(ny)-hw
        R[Y:Y+2*hw,X:X+2*hw]=np.maximum(R[Y:Y+2*hw,X:X+2*hw],st[...,0]); G[Y:Y+2*hw,X:X+2*hw]=np.maximum(G[Y:Y+2*hw,X:X+2*hw],st[...,1])
    log.append((row,len(rt),len(aisles),round(aw,2),round(n1-n0,2),[round(v,2) for v in rt]))
G=np.maximum(G,np.asarray(gimg))
for l in log: print('ROW',l)
sc=int(OUT/SS)
r=np.asarray(Image.fromarray(R).resize((W//sc,H//sc),Image.BOX)); g=np.asarray(Image.fromarray(G).resize((W//sc,H//sc),Image.BOX))
full=np.dstack([r,g,np.zeros_like(r)]).astype(np.uint8)
Image.fromarray(full).save('/workspace/nj-scenes/montclair-state/data/ws211c_access_lot_paint_mask.png')
HH,WW=full.shape[:2]; T=1000; OV=4; tiles=[]
for ty in range(0,HH,T):
    for tx in range(0,WW,T):
        c0,c1=max(0,tx-OV),min(WW,tx+T+OV); r0,r1=max(0,ty-OV),min(HH,ty+T+OV); sub=full[r0:r1,c0:c1]
        if sub.max()==0: continue
        nm=f'ws211c_mask_tile_{tx//T}_{ty//T}.png'; Image.fromarray(sub).save('/workspace/nj-scenes/montclair-state/data/'+nm)
        tiles.append((nm, X0+c0*OUT, X0+c1*OUT, Y1-r1*OUT, Y1-r0*OUT))
json.dump(tiles,open('/workspace/nj-scenes/montclair-state/data/ws211c_mask_tiles.json','w')); print('tiles',len(tiles))
# preview over ortho
im=Image.open('ortho_lot.png').convert('RGB'); ox0,oy1=-258,-60
big=im.resize((im.width*2,im.height*2)); a=np.asarray(big).copy()
for yy in range(a.shape[0]):
    pass
yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]]; wx=ox0+(xx+.5)*0.025; wy=oy1-(yy+.5)*0.025
ci=((wx-X0)/OUT).astype(int); ri=((Y1-wy)/OUT).astype(int); ok=(ci>=0)&(ci<WW)&(ri>=0)&(ri<HH)
mg=np.zeros(ok.shape); mr=np.zeros(ok.shape); mg[ok]=full[ri[ok],ci[ok],1]; mr[ok]=full[ri[ok],ci[ok],0]
a[mg>128]=[255,0,255]; a[mr>128]=[255,255,0]
Image.fromarray(a).crop((0,150,1840,1250)).resize((1380,825)).save('mask2_on_ortho.jpg',quality=88)
