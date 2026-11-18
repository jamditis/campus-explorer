import json,numpy as np
from PIL import Image,ImageDraw
D=json.load(open('scripts/ws102/dump102.json'))
o=Image.open('data/ortho2020.png');S=o.size[0]/500
X0,X1,Y0,Y1=-262,-170,-290,-140; K=10
im=o.crop((int((X0+250)*S),int((250-Y1)*S),int((X1+250)*S),int((250-Y0)*S))).resize(((X1-X0)*K,(Y1-Y0)*K))
im.save('scripts/ws102/ortho102.png')
d=ImageDraw.Draw(im); P=lambda x,y:((x-X0)*K,(Y1-y)*K)
cols={'WS27_CollegeAve_carriageway':(255,255,0),'WS27_CollegeAve_curb':(255,128,0),'UA_CollegeAve_spur':(255,0,0),'UA_NormalAve_N':(0,255,255),'UA_NormalAve_CR':(0,128,255),'WS35':(255,0,255),'Footpaths':(0,255,0),'Roads':(255,255,255)}
for n,fs in D.items():
    c=next((v for k,v in cols.items() if n.startswith(k)),None)
    if not c: continue
    for f in fs: d.polygon([P(q[0],q[1]) for q in f],outline=c)
for t in range(X0,X1,10): d.text(P(t,Y1-1),str(t),fill=(255,255,0))
for t in range(Y0,Y1,10): d.text(P(X0+0.5,t),str(t),fill=(255,255,0))
im.save('scripts/ws102/ov102.png'); print(o.size,S)
