# Session my: procedural screen-content textures (no real logos/text), UNVERIFIED
import numpy as np, random
from PIL import Image, ImageDraw, ImageFilter
random.seed(31); np.random.seed(31)
W,H=1536,800
y=np.linspace(0,1,H)[:,None]; x=np.linspace(0,1,W)[None,:]
top=np.array([0.02,0.05,0.16]); bot=np.array([0.05,0.20,0.52])
g=top+(bot-top)*(y**1.3)[...,None]
r=np.sqrt(((x-0.62)*1.9)**2+((y-0.42)*1.0)**2)
g=g+np.clip(0.55-r,0,1)[...,None]*np.array([0.10,0.22,0.40])
img=Image.fromarray((np.clip(g,0,1)*255).astype('uint8'))
lay=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(lay)
# two depth layers of an abstract skyline (generic, not a real city)
for layer,(col,hmin,hmax,base) in enumerate((((70,120,200,110),60,220,H-150),((110,170,240,170),40,160,H-120))):
    xx=0
    while xx<W:
        w=random.randint(30,90); h=random.randint(hmin,hmax)
        d.rectangle([xx,base-h,xx+w-4,base],fill=col)
        if random.random()<0.25: d.rectangle([xx+w//2-3,base-h-random.randint(15,50),xx+w//2+1,base-h],fill=col)
        xx+=w
# water / ground band + light line
d.rectangle([0,H-150,W,H],fill=(10,30,80,200))
d.rectangle([0,H-152,W,H-147],fill=(160,210,255,230))
# soft diagonal light sweeps
for k in range(3):
    x0=200+k*420; d.polygon([(x0,0),(x0+120,0),(x0-180,H),(x0-300,H)],fill=(120,170,255,18))
img=Image.alpha_composite(img.convert('RGBA'),lay.filter(ImageFilter.GaussianBlur(1.2)))
# LED tile seams every ~0.5 m (6.4 m wide -> 12.8 tiles)
d=ImageDraw.Draw(img); step=W/12.8
for i in range(1,13): d.line([(i*step,0),(i*step,H)],fill=(10,22,50,255),width=1)
for j in range(1,7): d.line([(0,j*H/6.7),(W,j*H/6.7)],fill=(10,22,50,255),width=1)
img.convert('RGB').save('textures/my/my_videowall_abstract_skyline_UNVERIFIED.png')
# TV atlas: 7 tiles of generic broadcast-like content
TW,TH=320,180; A=Image.new('RGB',(TW*7,TH)); 
def tile(k):
    t=Image.new('RGB',(TW,TH)); d=ImageDraw.Draw(t)
    if k in (0,4):   # weather-map-like
        d.rectangle([0,0,TW,TH],fill=(20,50,120))
        for _ in range(9):
            cx,cy,rr=random.randint(0,TW),random.randint(0,TH),random.randint(20,60)
            d.ellipse([cx-rr,cy-rr*0.7,cx+rr,cy+rr*0.7],fill=random.choice([(60,170,80),(220,200,60),(60,150,70)]))
        t=t.filter(ImageFilter.GaussianBlur(6))
        d=ImageDraw.Draw(t); d.line([(30,40),(120,90),(200,70),(290,130)],fill=(230,230,240),width=3)
    elif k in (1,5): # presenter on blue set
        d.rectangle([0,0,TW,TH],fill=(25,60,140)); d.rectangle([0,120,TW,TH],fill=(200,205,215))
        d.ellipse([140,40,180,85],fill=(190,150,120)); d.rectangle([118,85,202,130],fill=(30,30,40))
    elif k==2:       # field footage, street scene
        d.rectangle([0,0,TW,TH],fill=(150,180,210)); d.rectangle([0,100,TW,TH],fill=(90,90,95))
        for i in range(6): d.rectangle([i*55,40+random.randint(0,30),i*55+45,100],fill=random.choice([(170,90,70),(200,190,170),(120,110,100)]))
    elif k==3:       # graphics / chart
        d.rectangle([0,0,TW,TH],fill=(15,25,55))
        for i in range(8): h=random.randint(20,120); d.rectangle([25+i*35,150-h,50+i*35,150],fill=(80,150,230))
    else:            # aerial / green
        d.rectangle([0,0,TW,TH],fill=(70,110,60)); d.polygon([(0,120),(TW,60),(TW,90),(0,150)],fill=(110,110,115))
    # generic lower-third bar (no text)
    d=ImageDraw.Draw(t); d.rectangle([0,TH-30,TW,TH-12],fill=(235,235,240)); d.rectangle([0,TH-30,70,TH-12],fill=(30,90,200))
    return t
for k in range(7): A.paste(tile(k),(k*TW,0))
A.save('textures/my/my_tv_atlas_generic_broadcast_UNVERIFIED.png')
# desk monitor screen: pale UI-like
M=Image.new('RGB',(256,160),(225,232,240)); d=ImageDraw.Draw(M)
d.rectangle([0,0,256,14],fill=(40,70,130)); d.rectangle([8,24,90,150],fill=(200,210,222))
for i in range(9): d.rectangle([100,26+i*14,100+random.randint(60,148),32+i*14],fill=(150,160,175))
M.save('textures/my/my_desk_monitor_screen_generic_UNVERIFIED.png')
print("ok")
