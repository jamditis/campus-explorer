# Session mz: generic prompter text-line texture + viewfinder image (no real text/logos), UNVERIFIED
import numpy as np, random
from PIL import Image, ImageDraw, ImageFilter
random.seed(53)
# prompter: white "text lines" (blocks of word-like bars) on black, centred cue arrow at left, 4:3
W,H=640,480; im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im)
y=40
while y<H-40:
    x=70; xe=random.randint(420,580)
    while x<xe:
        w=random.randint(18,70); d.rectangle([x,y,x+w,y+26],fill=(235,235,235)); x+=w+12
    y+=48
d.polygon([(18,H//2-16),(46,H//2),(18,H//2+16)],fill=(230,40,40))
im=im.filter(ImageFilter.GaussianBlur(0.6)); im.save('textures/mz/mz_prompter_text_lines_generic_UNVERIFIED.png')
# viewfinder: soft blurry studio shot (desk + blue wall), generic
W,H=320,240; a=np.zeros((H,W,3)); yy=np.linspace(0,1,H)[:,None]
a[:]=np.array([0.05,0.18,0.45])*(1-0.4*yy)[...,None]
a[int(H*0.62):,:]=[0.85,0.85,0.86]
a[int(H*0.30):int(H*0.62),int(W*0.38):int(W*0.62)]=[0.25,0.2,0.22]
a[int(H*0.18):int(H*0.32),int(W*0.45):int(W*0.55)]=[0.75,0.58,0.48]
im=Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3))
d=ImageDraw.Draw(im); d.rectangle([8,8,W-9,H-9],outline=(230,230,230)); d.rectangle([W-30,12,W-14,22],fill=(220,30,30))
im.save('textures/mz/mz_viewfinder_generic_UNVERIFIED.png'); print('ok')
