import json,numpy as np
from PIL import Image,ImageDraw
D=json.load(open('scripts/ws100/dump100.json'))
o=Image.open('data/ortho2020.png');S=o.size[0]/500
X0,X1,Y0,Y1=-216,-178,-110,-62; K=24
im=o.crop((int((X0+250)*S),int((250-Y1)*S),int((X1+250)*S),int((250-Y0)*S))).resize(((X1-X0)*K,(Y1-Y0)*K))
im2=im.copy()
d=ImageDraw.Draw(im)
P=lambda x,y:((x-X0)*K,(Y1-y)*K)
cols={'WS27_CollegeAve_carriageway':(255,255,0),'WS27_CollegeAve_curb':(255,128,0),'WS35_Kasser_terrace':(255,0,0),'WS35_Kasser_steps_cheek':(255,0,128),'WS40_CollegeAve_east':(0,255,255),'WS40_Cole_deck':(0,128,255),'COLE_plaza_deck':(0,255,0),'WS89_Kasser':(255,0,255),'WS73':(128,255,128)}
for n,fs in D.items():
    c=next((v for k,v in cols.items() if n.startswith(k)),None)
    if not c: continue
    for f in fs: d.polygon([P(q[0],q[1]) for q in f],outline=c)
z=np.load('data/pts_crop.npz'); x,y,h,cl=z['x'],z['y'],z['z'],z['c']
m=(x>X0)&(x<X1)&(y>Y0)&(y<Y1)&(cl==6)
for a,b in zip(x[m][::2],y[m][::2]): px,py=P(a,b); d.point((px,py),fill=(255,255,255))
for t in range(X0,X1,2): d.text(P(t,Y1-0.3),str(t),fill=(255,255,0))
for t in range(Y0,Y1,2): d.text(P(X0+0.1,t),str(t),fill=(255,255,0))
im.save('scripts/ws100/ov100.png'); im2.save('scripts/ws100/ortho100.png')
# LiDAR ground slope/z grid
g=(x>X0)&(x<X1)&(y>Y0)&(y<Y1)&(cl==2)
import scipy.stats as ss
st=ss.binned_statistic_2d(x[g],y[g],h[g],'median',bins=[(X1-X0)*2,(Y1-Y0)*2],range=[[X0,X1],[Y0,Y1]])
Z=st.statistic.T[::-1]
gy,gx=np.gradient(np.nan_to_num(Z,nan=np.nanmedian(Z)),0.5)
sl=np.hypot(gx,gy); img=(np.clip(sl/0.8,0,1)*255).astype(np.uint8)
Image.fromarray(img).resize(((X1-X0)*K,(Y1-Y0)*K),0).save('scripts/ws100/slope100.png')
for yy in range(-108,-62,4):
    r=Z[int((Y1-yy)*2)-1]; print('y',yy,' '.join('%5.1f'%v if not np.isnan(v) else '  .  ' for v in r[::4]))
print('x cols',list(range(X0,X1,2)))
