# ws76: crisp stall-line paint mask from the 2020 ortho. Only strokes inside by-eye row zones (world coords) are kept;
# each stroke -> one straight 0.12 m line (PCA axis, length clamped). Zones flagged blue = accessible stalls (blue paint).
from PIL import Image, ImageDraw; import numpy as np, scipy.ndimage as nd
Image.MAX_IMAGE_PIXELS=None
im=np.asarray(Image.open('north/data/ortho2020_north.jpg').convert('RGB')).astype(float)/255
X0,X1,Y0,Y1,S=-330,-215,-145,-40,0.05
def colrow(x,y): return (x+600)/820*2023-0.5, (1-(y+260)/1660)*4096-0.5
def world(c,r): return (c+0.5)/2023*820-600, (1-(r+0.5)/4096)*1660-260
lum=im@[.2126,.7152,.0722]; th=lum-nd.grey_opening(lum,size=(4,4))
# zones: (name, polygon world xy, blue, default stall dir deg, len)
Z=[('sprague_N_row',[(-254.5,-86.5),(-218,-91.5),(-218.5,-99.5),(-255,-94.5)],False,95,5.0),
   ('sprague_SE',[(-232,-125),(-221,-127),(-221,-134),(-232,-132)],False,60,4.5),
   ('cogen_blue_N',[(-283,-56),(-262.5,-57.5),(-262.5,-65),(-283,-63.5)],True,115,4.5),
   ('cogen_blue_S',[(-285,-65.5),(-266.5,-67),(-266.5,-74),(-285,-72.5)],True,115,4.5)]
def inpoly(poly,x,y):
    import numpy as np
    ins=np.zeros(x.shape,bool); n=len(poly)
    for i in range(n):
        (xa,ya),(xb,yb)=poly[i],poly[(i+1)%n]
        cond=((ya>y)!=(yb>y))&(x<(xb-xa)*(y-ya)/(yb-ya+1e-12)+xa); ins^=cond
    return ins
H,W=lum.shape
lines=[]
for nm,poly,blue,ddeg,L in Z:
    pts=[colrow(*p) for p in poly]; cs=[p[0] for p in pts]; rs=[p[1] for p in pts]
    c0,c1,r0,r1=int(min(cs)),int(max(cs))+2,int(min(rs)),int(max(rs))+2
    cc,rr=np.meshgrid(np.arange(c0,c1),np.arange(r0,r1)); inz=inpoly(pts,cc.astype(float),rr.astype(float))
    t=th[r0:r1,c0:c1]; thr=np.percentile(t[inz],80)
    m=inz&(t>max(thr,0.02))
    lab,n=nd.label(m); k=0
    for i in range(1,n+1):
        ys,xs=np.where(lab==i)
        if len(xs)<2: continue
        wx,wy=world(xs+c0,ys+r0); P=np.c_[wx,wy]; c=P.mean(0)
        d=np.array([np.cos(np.radians(ddeg)),np.sin(np.radians(ddeg))])
        if len(xs)>=4:
            u,s,vt=np.linalg.svd(P-c); 
            if s[0]>1.8*s[1]: d=vt[0]
        proj=(P-c)@d; l=np.clip(np.ptp(proj)+0.4,3.0,L)
        lines.append((c-d*l/2,c+d*l/2,blue)); k+=1
    print(nm,'strokes',k)
np.save('scripts/ws76/lines.npy',np.array([[a[0],a[1],b[0],b[1],bl] for a,b,bl in lines]))
nx,ny=int((X1-X0)/S),int((Y1-Y0)/S)
img=Image.new('RGB',(nx,ny)); dr=ImageDraw.Draw(img)
def px(p): return ((p[0]-X0)/S,(Y1-p[1])/S)
for a,b,bl in lines: dr.line([px(a),px(b)],fill=(0,255,0) if bl else (255,0,0),width=3)
img.save('data/ws76_lot_paint_mask.png')
# preview over ortho
xs=np.arange(X0,X1,S)+S/2; ys=np.arange(Y1,Y0,-S)-S/2; XX,YY=np.meshgrid(xs,ys); cc,rr=colrow(XX,YY)
pv=np.stack([nd.map_coordinates(im[...,k],[rr,cc],order=1) for k in range(3)],-1)
M=np.asarray(img); pv[M[...,0]>0]=[1,0,0]; pv[M[...,1]>0]=[0,1,1]
Image.fromarray((pv[0:1300,600:2300]*255).astype(np.uint8)).resize((850,650)).save('scripts/ws76/stalls_preview.png')
print('lines',len(lines))
