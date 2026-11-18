import json,sys,colorsys
from PIL import Image,ImageDraw
P=json.load(open(sys.argv[1])); orth=sys.argv[2]; out=sys.argv[3]
nx,ny=P['nx'],P['ny']; x0,x1,y0,y1=P['box']; d=P['d']
names=sorted(set(r[2] or '-' for r in d)); col={}
for i,n in enumerate(names):
    r,g,b=colorsys.hsv_to_rgb((i*0.618)%1,0.8,1); col[n]=(int(r*255),int(g*255),int(b*255))
S=1000; im=Image.open(orth).convert('RGB').resize((S,S)); lab=Image.new('RGB',(nx,ny))
for k,r in enumerate(d):
    i=k%nx; j=k//nx; lab.putpixel((i,ny-1-j),col[r[2] or '-'])
lab=lab.resize((S,S),Image.NEAREST); im=Image.blend(im,lab,0.45); dr=ImageDraw.Draw(im)
# boundaries
s=S/(x1-x0)
for x in range(int(x0),int(x1)+1,5):
    X=(x-x0)*s; dr.line([(X,0),(X,S)],fill=(255,255,255) if x%10==0 else (160,160,160)); dr.text((X+2,2),str(x),fill=(255,255,255))
for y in range(int(y0),int(y1)+1,5):
    Y=(y1-y)*s; dr.line([(0,Y),(S,Y)],fill=(255,255,255) if y%10==0 else (160,160,160)); dr.text((2,Y+2),str(y),fill=(255,255,255))
im.save(out)
cnt={n:sum(1 for r in d if (r[2] or '-')==n) for n in names}
for n in sorted(names,key=lambda n:-cnt[n]): print(col[n],cnt[n],n[:70])
