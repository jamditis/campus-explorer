# ws219: draped stall/edge/crosswalk paint (WS179 x2, WS130, WS135a, WS138a) -> world-XY masks (R), 2 cm/px, one tile per object
import json,numpy as np
from PIL import Image,ImageDraw
P=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws220/paint220.json'))
SS=0.01; OUT=0.02; tiles=[]
for nm,o in P.items():
    if not o['F']: print('skip',nm); continue
    V=np.array(o['V']); idx=sorted(set(i for f,_ in o['F'] for i in f))
    X0,Y0=V[idx,0].min()-0.2,V[idx,1].min()-0.2; X1,Y1=V[idx,0].max()+0.2,V[idx,1].max()+0.2
    W=int(np.ceil((X1-X0)/OUT))*2; H=int(np.ceil((Y1-Y0)/OUT))*2
    R=Image.new('L',(W,H)); d=ImageDraw.Draw(R)
    for f,_ in o['F']: d.polygon([((V[i][0]-X0)/SS,(Y1-V[i][1])/SS) for i in f],fill=255)
    r=np.asarray(R.resize((W//2,H//2),Image.BOX)); full=np.dstack([r,np.zeros_like(r),np.zeros_like(r)]).astype(np.uint8)
    key='c'
    fn='ws220%s_mask_tile_%d.png'%(key,len(tiles)); Image.fromarray(full).save('/workspace/nj-scenes/montclair-state/data/'+fn)  # name matches the exporter regex (ws\d+[a-z]?)_mask_tile_
    tiles.append([key,fn,X0,X0+r.shape[1]*OUT,Y1-r.shape[0]*OUT,Y1,nm,o['mats'][0][1]])
    print(fn,r.shape,'cover m2',round((r>128).sum()*OUT*OUT,2))
json.dump(tiles,open('/workspace/nj-scenes/montclair-state/data/ws220_mask_tiles.json','w'))  # 8-field, read by fix220a
# 5-field [file,x0,x1,y0,y1] per prefix for tools/web-export/paint.py
for key in sorted(set(t[0] for t in tiles)):
    json.dump([[t[1],t[2],t[3],t[4],t[5]] for t in tiles if t[0]==key],open('/workspace/nj-scenes/montclair-state/data/ws220%s_mask_tiles.json'%key,'w'))
