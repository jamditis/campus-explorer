# ws219: RHD SE College Ave crosswalk bars (ey_rhd_se_crosswalks, draped slabs) -> world-XY paint mask (R), 1 cm/px
import json,numpy as np
from PIL import Image,ImageDraw
Z=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws219/cw219.json'))['ey_rhd_se_crosswalks']
V=np.array(Z['V']); print('V',V.min(0).round(2),V.max(0).round(2))
X0,X1,Y0,Y1=-261.5,-255.8,-59.3,-51.6; SS=0.005; OUT=0.01
W=int(round((X1-X0)/SS)); H=int(round((Y1-Y0)/SS)); R=Image.new('L',(W,H)); d=ImageDraw.Draw(R)
px=lambda v:((v[0]-X0)/SS,(Y1-v[1])/SS)
n=0
for p,nz in zip(Z['P'],Z['NZ']):
    if nz>0.5: d.polygon([px(V[i]) for i in p],fill=255); n+=1
s=int(OUT/SS); r=np.asarray(R.resize((W//s,H//s),Image.BOX))
full=np.dstack([r,np.zeros_like(r),np.zeros_like(r)]).astype(np.uint8)
nm='ws219z_mask_rhd_se_crosswalk.png'; Image.fromarray(full).save('/workspace/nj-scenes/montclair-state/data/'+nm)
json.dump([[nm,X0,X0+r.shape[1]*OUT,Y1-r.shape[0]*OUT,Y1]],open('/workspace/nj-scenes/montclair-state/data/ws219z_mask_tiles.json','w'))
print('top faces',n,'mask',r.shape,'cover px',int((r>128).sum()))
Image.fromarray(r).resize((r.shape[1]//2,r.shape[0]//2)).save('/workspace/nj-scenes/montclair-state/scripts/ws219/mask219_prev.png')
