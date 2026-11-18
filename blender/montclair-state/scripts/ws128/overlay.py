import json,sys
from PIL import Image, ImageDraw
X0,X1,Y0,Y1=[float(v) for v in (sys.argv[1] if len(sys.argv)>1 else '-250,-226,-252,-228').split(',')]
im=Image.open('data/ortho2020.png').convert('RGB'); W=im.size[0]; s=16
px=lambda x:(0.5+x/500)*W; py=lambda y:(0.5-y/500)*W
ox,oy=int(px(X0)),int(py(Y1))
c=im.crop((ox,oy,int(px(X1)),int(py(Y0)))); c=c.resize((c.size[0]*s,c.size[1]*s),Image.LANCZOS)
base=c.copy(); d=ImageDraw.Draw(c)
P=lambda x,y:((px(x)-ox)*s,(py(y)-oy)*s)
cols={'WS127':(255,0,255),'WS115':(0,255,255),'WS112_C':(255,128,0),'WS112_W':(255,255,0),'WS102':(255,0,0),'WS111':(0,255,0),'WS103':(0,0,255)}
pl=json.load(open('scripts/ws128/plan128.json'))
for n,L in pl.items():
    col=next((v for k,v in cols.items() if n.startswith(k)),None)
    if col is None: continue
    for f in L: d.polygon([P(v[0],v[1]) for v in f],outline=col)
for x in range(int(X0),int(X1)+1,2):
    d.text(P(x,Y1-0.6),str(x),fill=(255,255,255))
for y in range(int(Y0),int(Y1)+1,2):
    d.text(P(X0+0.2,y),str(y),fill=(255,255,255))
out=Image.new('RGB',(c.size[0]*2,c.size[1])); out.paste(base,(0,0)); out.paste(c,(c.size[0],0))
out.save('scripts/ws128/overlay128.png'); print(out.size)
