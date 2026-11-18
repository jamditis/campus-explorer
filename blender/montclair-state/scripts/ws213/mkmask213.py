# ws213: rasterize WS76_lot_stall_paint_white_ortho2020_UNVERIFIED (all faces: Sprague N row, cogen rows, accessible-lot bits) -> world-XY mask (R=white), 1 cm/px, tiles<=1000
import json,numpy as np
from PIL import Image,ImageDraw
Image.MAX_IMAGE_PIXELS=None
P=json.load(open('../ws211/paint.json'))['WS76_lot_stall_paint_white_ortho2020_UNVERIFIED']
X0,X1,Y0,Y1=-286.0,-218.0,-96.0,-55.0; SS=0.005; OUT=0.01
W=int(round((X1-X0)/SS)); H=int(round((Y1-Y0)/SS))
R=Image.new('L',(W,H)); d=ImageDraw.Draw(R)
V=np.array(P['V'])
def px(v): return ((v[0]-X0)/SS,(Y1-v[1])/SS)
for p in P['P']: d.polygon([px(V[i]) for i in p],fill=255)
s=int(OUT/SS); r=np.asarray(R.resize((W//s,H//s),Image.BOX))
HH,WW=r.shape; T=1000; OV=4; tiles=[]
full=np.dstack([r,np.zeros_like(r),np.zeros_like(r)]).astype(np.uint8)
Image.fromarray(r).save('/workspace/nj-scenes/montclair-state/data/ws213_white_paint_mask.png')
for ty in range(0,HH,T):
    for tx in range(0,WW,T):
        c0,c1=max(0,tx-OV),min(WW,tx+T+OV); r0,r1=max(0,ty-OV),min(HH,ty+T+OV); sub=full[r0:r1,c0:c1]
        if sub.max()==0: continue
        nm=f'ws213_mask_tile_{tx//T}_{ty//T}.png'; Image.fromarray(sub).save('/workspace/nj-scenes/montclair-state/data/'+nm)
        tiles.append((nm, X0+c0*OUT, X0+c1*OUT, Y1-r1*OUT, Y1-r0*OUT))
json.dump(tiles,open('/workspace/nj-scenes/montclair-state/data/ws213_mask_tiles.json','w')); print('tiles',len(tiles),WW,HH,'cover',(r>127).sum()*1e-4,'m2')
# preview on ws211 ortho (x -258..-212, y -92..-60 @0.05) for the overlap
im=np.asarray(Image.open('../ws211/ortho_lot.png').convert('RGB')).copy(); oh,ow=im.shape[:2]
yy,xx=np.mgrid[0:oh,0:ow]; wx=-258+(xx+.5)*0.05; wy=-60-(yy+.5)*0.05
ci=((wx-X0)/OUT).astype(int); ri=((Y1-wy)/OUT).astype(int); ok=(ci>=0)&(ci<WW)&(ri>=0)&(ri<HH)
m=np.zeros(ok.shape); m[ok]=r[ri[ok],ci[ok]]; im2=im.copy(); im2[m>128]=[255,0,255]
Image.fromarray(np.hstack([im,im2])).save('prev213.jpg',quality=85)
