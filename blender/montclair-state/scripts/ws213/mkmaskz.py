# ws213: zebra walkway (WS76) + lot-entrance crosswalk bars (WS204) -> world-XY mask (R), 1 cm/px, tiles<=1000
import json,numpy as np
from PIL import Image,ImageDraw
Z=json.load(open('zebra.json'))
X0,X1,Y0,Y1=-264.0,-251.0,-94.0,-57.0; SS=0.005; OUT=0.01
W=int(round((X1-X0)/SS)); H=int(round((Y1-Y0)/SS)); R=Image.new('L',(W,H)); d=ImageDraw.Draw(R)
def px(v): return ((v[0]-X0)/SS,(Y1-v[1])/SS)
for nm,o in Z.items():
    V=np.array(o['V']); print(nm,V.min(0).round(2),V.max(0).round(2))
    for p in o['P']: d.polygon([px(V[i]) for i in p],fill=255)
s=int(OUT/SS); r=np.asarray(R.resize((W//s,H//s),Image.BOX)); HH,WW=r.shape
full=np.dstack([r,np.zeros_like(r),np.zeros_like(r)]).astype(np.uint8); T=1000; OV=4; tiles=[]
for ty in range(0,HH,T):
    for tx in range(0,WW,T):
        c0,c1=max(0,tx-OV),min(WW,tx+T+OV); r0,r1=max(0,ty-OV),min(HH,ty+T+OV); sub=full[r0:r1,c0:c1]
        if sub.max()==0: continue
        nm=f'ws213z_mask_tile_{tx//T}_{ty//T}.png'; Image.fromarray(sub).save('/workspace/nj-scenes/montclair-state/data/'+nm)
        tiles.append((nm, X0+c0*OUT, X0+c1*OUT, Y1-r1*OUT, Y1-r0*OUT))
json.dump(tiles,open('/workspace/nj-scenes/montclair-state/data/ws213z_mask_tiles.json','w')); print('tiles',len(tiles),WW,HH)
im=np.asarray(Image.open('../ws211/ortho_lot.png').convert('RGB')).copy(); oh,ow=im.shape[:2]
yy,xx=np.mgrid[0:oh,0:ow]; wx=-258+(xx+.5)*0.05; wy=-60-(yy+.5)*0.05
ci=((wx-X0)/OUT).astype(int); ri=((Y1-wy)/OUT).astype(int); ok=(ci>=0)&(ci<WW)&(ri>=0)&(ri<HH)
m=np.zeros(ok.shape); m[ok]=r[ri[ok],ci[ok]]; im2=im.copy(); im2[m>128]=[255,0,255]
Image.fromarray(np.hstack([im,im2])[:, :]).crop((0,0,400,640)).save('prevz.jpg',quality=85)
Image.fromarray(np.hstack([im[:, :200],im2[:, :200]])).resize((800,1280)).save('prevz.jpg',quality=85)
