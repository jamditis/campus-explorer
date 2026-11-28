# ws269c: rasterize the 31 traced paint strokes (paint269k.json) to world-XY mask tiles (AGENTS.md rule 7: markings are paint in
# the asphalt material). 3 cm/px, drawn at 1.5 cm then box-filtered (anti-aliased), tiles <= 1000 px, only tiles with paint kept.
import json, numpy as np
from PIL import Image, ImageDraw
D=json.load(open('scripts/ws269/paint269k.json'))
S=0.03; T=30.0; X0,Y0=-393.0,-63.0; NX,NY=3,2   # x -393..-303, y -63..-3 (paving y <= -19.5)
tiles=[]
for i in range(NX):
    for j in range(NY):
        tx0,ty0=X0+i*T,Y0+j*T; tx1,ty1=tx0+T,ty0+T; n=int(T/S); ss=2
        im=Image.new('L',(n*ss,n*ss),0); dr=ImageDraw.Draw(im); k=0
        px=lambda x,y:((x-tx0)/S*ss,(ty1-y)/S*ss)
        for x0,y0,x1,y1,w in D['segs']:
            if max(x0,x1)<tx0-1 or min(x0,x1)>tx1+1 or max(y0,y1)<ty0-1 or min(y0,y1)>ty1+1: continue
            dr.line([px(x0,y0),px(x1,y1)],fill=255,width=max(1,round(w/S*ss))); k+=1
        if not k: continue
        a=np.asarray(im,dtype=float).reshape(n,ss,n,ss).mean((1,3))
        if a.max()<1: continue
        nm='ws269_lot33_paint_tile_%d_%d.png'%(i,j)
        Image.fromarray(a.astype(np.uint8)).convert('RGB').save('data/'+nm,optimize=True); tiles.append([nm,tx0,tx1,ty0,ty1]); print(nm,k,'strokes')
json.dump(tiles,open('data/ws269_mask_tiles.json','w')); print(tiles)
