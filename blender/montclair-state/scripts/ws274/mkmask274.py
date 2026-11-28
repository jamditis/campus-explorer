# ws274: paint the W72 residual markings into the College Ave / Lot 33 asphalt mask (AGENTS.md rule 7: markings are paint).
# Evidence: NJ 2020 0.1 m ortho (scripts/ws269/url269.txt). (a) westbound turn arrow just E of the Carlisle Rd stop bar: bright blobs
# at (-379.5,-20.2) and (-380,-23); read as one left-turn arrow (stem W, head S) — arrow TYPE UNVERIFIED. (b) hatched no-parking box at the
# E end of the parking bay by the red-roof building, x -338.6...-334.4, y -25.4...-28.3; top-15% pixel colour (182,190,161) is yellower than
# the white arrows (191,201,183) and dashes -> faded yellow, colour UNVERIFIED.
# Output: data/ws274_lot33_paint_tile_0_1.png (= ws269 tile 0_1 + arrow) and data/ws274_lot33_hatch_yellow_tile.png + data/ws274_mask_tiles.json.
import json, math, numpy as np
from PIL import Image, ImageDraw
S=0.03; ss=2
def tile(path_in, tx0,tx1,ty0,ty1, draw):
    n=int(round((tx1-tx0)/S)); m=int(round((ty1-ty0)/S))
    im=Image.new('L',(n*ss,m*ss),0); dr=ImageDraw.Draw(im)
    px=lambda x,y:((x-tx0)/S*ss,(ty1-y)/S*ss)
    draw(dr,px)
    a=np.asarray(im,dtype=float).reshape(m,ss,n,ss).mean((1,3))
    if path_in:
        b=np.asarray(Image.open(path_in).convert('L'),dtype=float); a=np.maximum(a,b)
    return a
W=lambda w:max(1,round(w/S*ss))
def arrow(dr,px):
    stem=[(-377.8,-20.7),(-379.3,-20.7),(-379.75,-21.0),(-379.9,-21.5),(-379.9,-22.2)]
    dr.line([px(*p) for p in stem],fill=255,width=W(0.30),joint='curve')
    dr.polygon([px(-380.5,-22.15),px(-379.3,-22.15),px(-379.9,-23.45)],fill=255)
# base = the ws269 strokes for this tile minus the arrow fragment ws269 traced as a line (-379.34,-20.54)->(-378.65,-21.33)
SEG=[s for s in json.load(open('scripts/ws269/paint269k.json'))['segs'] if not (abs(s[0]+379.34)<0.02 and abs(s[1]+20.54)<0.02)]
def both(dr,px):
    for x0,y0,x1,y1,w in SEG: dr.line([px(x0,y0),px(x1,y1)],fill=255,width=W(w))
    arrow(dr,px)
a=tile(None,-393.0,-363.0,-33.0,-3.0,both)
Image.fromarray(a.astype(np.uint8)).convert('RGB').save('data/ws274_lot33_paint_tile_0_1.png',optimize=True)
# hatch box in road-aligned coords
P0=np.array([-338.6,-24.85]); d=np.array([4.2,-1.15]); d/=np.linalg.norm(d); nrm=np.array([d[1],-d[0]])   # nrm points S (into road)
def H(u,v): p=P0+d*u+nrm*v; return float(p[0]),float(p[1])
U0,U1,V0,V1=0.0,4.3,0.55,3.25
def hatch(dr,px):
    box=[H(U0,V0),H(U1,V0),H(U1,V1),H(U0,V1),H(U0,V0)]
    dr.line([px(*p) for p in box],fill=255,width=W(0.12))
    k=0.0
    while k<U1+ (V1-V0):
        ua,va=k,V0; ub,vb=k-(V1-V0),V1        # 45-degree stripes
        # clip to the box
        if ub<U0: vb=V0+(ua-U0); ub=U0
        if ua>U1: va=V0+(ua-U1); ua=U1
        if va<vb: dr.line([px(*H(ua,va)),px(*H(ub,vb))],fill=255,width=W(0.15))
        k+=0.9
hx0,hx1,hy0,hy1=-340.0,-332.0,-30.0,-23.0
b=tile(None,hx0,hx1,hy0,hy1,hatch)
Image.fromarray(b.astype(np.uint8)).convert('RGB').save('data/ws274_lot33_hatch_yellow_tile.png',optimize=True)
json.dump({'white':[['ws274_lot33_paint_tile_0_1.png',-393.0,-363.0,-33.0,-3.0,'ws269_lot33_paint_tile_0_1.png']],
           'yellow':[['ws274_lot33_hatch_yellow_tile.png',hx0,hx1,hy0,hy1]]},open('data/ws274_mask_tiles.json','w'))
print('arrow px',int((a>128).sum()),'hatch px',int((b>128).sum()))
