import json
from PIL import Image, ImageDraw
r=json.load(open('/workspace/nj-scenes/montclair-state/data/wa/probe.json'))
X0,X1,Y0,Y1=190,260,345,425; S=12
W,H=int((X1-X0)*S),int((Y1-Y0)*S)
im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
P=lambda x,y:((x-X0)*S,(Y1-y)*S)
cols={'TK_Bohn_Hall_232853538_base_UNVERIFIED':(210,210,210),'TL_Bohn_Hall_L1_0_rect_UNVERIFIED':(170,210,250),'TL_Bohn_Hall_L2_0_rect_UNVERIFIED':(110,160,210),'TL_Bohn_Hall_L3_0_rect_UNVERIFIED':(60,110,170),'TL_Bohn_Hall_L4_0_rect_UNVERIFIED':(20,60,120),'TL_Bohn_Hall_PH_0_rect_UNVERIFIED':(250,160,60),'TL_Bohn_Hall_PH_1_rect_UNVERIFIED':(250,100,30)}
order=list(cols)
tops=[f for f in r['faces'] if f['kind']=='top' and f['obj'] in cols]
tops.sort(key=lambda f:order.index(f['obj']))
for f in tops:
    d.polygon([P(*p) for p in f['xy']],fill=cols[f['obj']],outline=(0,0,0))
for f in tops:
    cx=sum(p[0] for p in f['xy'])/len(f['xy']); cy=sum(p[1] for p in f['xy'])/len(f['xy'])
    d.text(P(cx,cy),'%.0f'%f['z'],fill=(0,0,0))
for f in r['faces']:
    if f['kind']=='wall' and f['n'][0]<-0.7 and len(f['xy'])>=2 and f['obj'].startswith('TL'):
        a,b=f['xy'][0],f['xy'][-1]
        d.line([P(*a),P(*b)],fill=(255,0,0),width=3)
for x in range(X0,X1+1,10): d.line([P(x,Y0),P(x,Y1)],fill=(200,200,200)); d.text(P(x,Y0+1),str(x),fill=(0,0,0))
for y in range(Y0,Y1+1,10): d.line([P(X0,y),P(X1,y)],fill=(200,200,200)); d.text(P(X0+0.5,y),str(y),fill=(0,0,0))
im.save('/workspace/nj-scenes/montclair-state/data/wa/plan_bohn.png')
