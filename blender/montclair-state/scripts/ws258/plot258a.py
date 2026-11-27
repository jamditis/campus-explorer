import json,sys
from PIL import Image,ImageDraw
d=json.load(open('probe258a.json'))
X0,X1,Y0,Y1=-265,-180,-235,-120; S=10
W,H=int((X1-X0)*S),int((Y1-Y0)*S)
im=Image.new('RGB',(W,H),'white'); dr=ImageDraw.Draw(im)
P=lambda x,y:((x-X0)*S,(Y1-y)*S)
col=lambda n:(220,60,60) if n.startswith('Footpaths') else (60,60,60) if n.startswith('Roads') else (90,140,220) if 'walk' in n.lower() or 'sidewalk' in n.lower() or 'plaza' in n.lower() else (200,200,200)
for o in sorted(d,key=lambda o:o['name'].startswith('Footpaths')):
    if o['hide_render']: continue
    for p in o['polys']:
        dr.polygon([P(v[0],v[1]) for v in p],fill=col(o['name']),outline=(0,0,0) if o['name'].startswith('Footpaths') else None)
for x in range(X0,X1+1,5):
    dr.line([P(x,Y0),P(x,Y1)],fill=(0,200,0) if x%25==0 else (210,240,210)); dr.text(P(x+0.3,Y1-1),str(x),fill=(0,120,0))
for y in range(Y0,Y1+1,5):
    dr.line([P(X0,y),P(X1,y)],fill=(0,200,0) if y%25==0 else (210,240,210)); dr.text(P(X0+0.3,y+1.5),str(y),fill=(0,120,0))
im.save('plot258a.png'); print(W,H)
