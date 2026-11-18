import json,sys
from PIL import Image,ImageDraw
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
B=json.load(open('scripts/ws98/build98.json')); D=json.load(open('scripts/ws98/dump98.json'))
o=Image.open('data/ortho2020.png');S=o.size[0]/500
X0,X1,Y0,Y1=-226,-196,-96,-62; K=20
im=o.crop((int((X0+250)*S),int((250-Y1)*S),int((X1+250)*S),int((250-Y0)*S))).resize(((X1-X0)*K,(Y1-Y0)*K))
d=ImageDraw.Draw(im)
P=lambda x,y:((x-X0)*K,(Y1-y)*K)
for name,col in (('aisle',(255,255,0)),('pad',(0,255,255)),('island_mulch',(255,0,255)),('island_curb',(255,255,255))):
    V,F=B[name]
    for f in F:
        d.polygon([P(*V[i][:2]) for i in f],outline=col)
for n,col in (('WS27_CollegeAve_curb_right_UNVERIFIED',(255,128,0)),('WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges',(0,0,255))):
    V=D[n]['v']
    for f in D[n]['f'][::1]:
        d.polygon([P(*V[i][:2]) for i in f],outline=col)
for cx,cy in B['curb_cut_centroids']: d.ellipse([P(cx,cy)[0]-2,P(cx,cy)[1]-2,P(cx,cy)[0]+2,P(cx,cy)[1]+2],fill=(255,0,0))
for t in range(X0,X1,2): d.text(P(t,Y1-0.2),str(t),fill=(255,255,0))
for t in range(Y0,Y1,2): d.text(P(X0+0.1,t),str(t),fill=(255,255,0))
im.save('scripts/ws98/plan_overlay.png')
