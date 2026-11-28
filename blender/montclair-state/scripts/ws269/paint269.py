# ws269: white paint strokes + dark planted islands inside the ws268 College Ave / Lot 33 polygon, from the NJ 2020 WMS ortho
# (ortho269.png, 0.1 m/px, x -398..-302, y -68..-12). Paint = top-hat bright, thin elongated components -> PCA line segments.
import numpy as np, scipy.ndimage as nd, json
from PIL import Image, ImageDraw
im=np.asarray(Image.open('ortho269.png').convert('RGB')).astype(float)/255
H,W,_=im.shape; S=0.1; X0=-398; Y1=-12
def world(c,r): return X0+(c+0.5)*S, Y1-(r+0.5)*S
P=[(-336,-25.2),(-345,-23.0),(-355,-21.5),(-367,-20.6),(-378,-20.0),(-390,-19.5),(-390,-36),(-387,-39),(-376,-42),(-377,-46),
   (-327,-59),(-317,-61),(-315,-61),(-311,-48),(-318,-31),(-331,-27.2)]
from PIL import Image as _I
cc,rr=np.meshgrid(np.arange(W),np.arange(H)); wx,wy=world(cc,rr)
_m=_I.new('L',(W,H),0); ImageDraw.Draw(_m).polygon([((x-X0)/S-0.5,(Y1-y)/S-0.5) for x,y in P],fill=1); inp=np.asarray(_m).astype(bool)
inp=nd.binary_erosion(inp,iterations=6)   # 0.6 m inside the edge (curb / walk edge glare)
lum=im@[.2126,.7152,.0722]; sat=im.max(2)-im.min(2)
th=lum-nd.grey_opening(lum,size=(7,7))
m=inp&(th>0.10)&(lum>0.55)&(sat<0.18)
lab,n=nd.label(m); segs=[]
for i,sl in enumerate(nd.find_objects(lab),1):
    ys,xs=np.where(lab[sl]==i); ys=ys+sl[0].start; xs=xs+sl[1].start
    if len(xs)<6 or len(xs)>400: continue
    x,y=world(xs,ys); Q=np.c_[x,y]; c=Q.mean(0); u,s,vt=np.linalg.svd(Q-c,full_matrices=False)
    s=s/np.sqrt(len(xs))
    if s[0]<2.2*s[1] : continue           # blobs (car glare, arrows) skipped
    d=vt[0]; pr=(Q-c)@d; L=np.ptp(pr)
    if L<0.8: continue
    w=max(0.10,min(0.2,4*s[1]))
    segs.append([*(c+d*pr.min()),*(c+d*pr.max()),round(w,3)])
# dark planted island(s): low luminance, low saturation-ish, big component, not building shadow (inside polygon)
dk=inp&(lum<0.22)
dk=nd.binary_opening(dk,iterations=3); lab2,n2=nd.label(dk); isl=[]
for i,sl in enumerate(nd.find_objects(lab2),1):
    ys,xs=np.where(lab2[sl]==i); ys=ys+sl[0].start; xs=xs+sl[1].start
    if len(xs)<400: continue
    x,y=world(xs,ys); Q=np.c_[x,y]; c=Q.mean(0); u,s,vt=np.linalg.svd(Q-c,full_matrices=False); d=vt[0]
    pr=(Q-c)@d; pq=(Q-c)@np.array([-d[1],d[0]])
    isl.append(dict(c=c.round(2).tolist(),d=d.round(3).tolist(),L=[round(np.percentile(pr,1),2),round(np.percentile(pr,99),2)],
                    Wd=[round(np.percentile(pq,2),2),round(np.percentile(pq,98),2)],area=round(len(xs)*S*S,1)))
print('segs',len(segs),'total m',round(sum(np.hypot(a[2]-a[0],a[3]-a[1]) for a in segs),1)); print('islands',json.dumps(isl))
json.dump(dict(segs=segs,islands=isl),open('paint269.json','w'))
pv=Image.open('ortho269.png').convert('RGB'); dr=ImageDraw.Draw(pv)
px=lambda x,y:((x-X0)/S,(Y1-y)/S)
for a in segs: dr.line([px(a[0],a[1]),px(a[2],a[3])],fill=(255,0,0),width=2)
dr.polygon([px(*p) for p in P],outline=(0,255,255))
for k in isl:
    c=np.array(k['c']); d=np.array(k['d']); nrm=np.array([-d[1],d[0]])
    q=[c+d*k['L'][0]+nrm*k['Wd'][0],c+d*k['L'][1]+nrm*k['Wd'][0],c+d*k['L'][1]+nrm*k['Wd'][1],c+d*k['L'][0]+nrm*k['Wd'][1]]
    dr.polygon([px(*p) for p in q],outline=(0,255,0))
pv.save('paint269_prev.png')
