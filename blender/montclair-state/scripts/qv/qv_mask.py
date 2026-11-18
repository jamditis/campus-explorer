# qv: lawn mask PNG for the N/W skirt lawn shader (no Blender). 0.5 m/px over x -10..160, y 228..352 (MAIN local m).
# 1 = lawn, 0 = Richardson footprint only (other OSM footprints there are not built in MAIN yet -> lawn placeholder, UNVERIFIED).
import json,numpy as np
from PIL import Image,ImageDraw,ImageFilter
X0,X1,Y0,Y1,R=-60.,170.,228.,362.,0.5
W,H=int((X1-X0)/R),int((Y1-Y0)/R)
D=json.load(open('data/scene_data.json'))
im=Image.new('L',(W,H),255); dr=ImageDraw.Draw(im); n=0
def px(p): return ((p[0]-X0)/R,(Y1-p[1])/R)   # row 0 = north (image top) -> v=1 at Y1
polys=[]  # qv decision: out-of-scene footprints (Student Center/Health Drop-In = day 8, Reid Hall = outside boundary) read as lawn placeholder
polys.append(json.load(open('data/qp/rich_poly.json'))['outer'])
for p in polys:
    if max(q[0] for q in p)<X0 or min(q[0] for q in p)>X1 or max(q[1] for q in p)<Y0 or min(q[1] for q in p)>Y1: continue
    dr.polygon([px(q) for q in p],fill=0); n+=1
im=im.filter(ImageFilter.GaussianBlur(1.2))
im.save('data/qv/qv_lawn_mask.png'); print('MASK',W,H,n,np.asarray(im).mean()/255)
