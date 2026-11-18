import os
import numpy as np,json,sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_shapely313')
import shapely
from shapely.geometry import Polygon,box,Point,MultiPolygon
from shapely.ops import unary_union
from scipy import ndimage
D=json.load(open('scripts/ws98/dump98.json'))
def fp(n):
    V=D[n]['v']; P=[]
    for f in D[n]['f']:
        p=Polygon([(V[i][0],V[i][1]) for i in f]).buffer(0)
        if p.area>0: P.append(p)
    return unary_union(P)
ROAD=unary_union([fp('WS27_CollegeAve_carriageway_2020ortho'),fp('WS27_CollegeAve_curb_right_UNVERIFIED')])
CARR=fp('WS27_CollegeAve_carriageway_2020ortho')
LOT=unary_union([fp(n) for n in D if n.startswith(('WS75','WS76','WS79','WS80','WS96'))])
WS77=fp('WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020')
WS89=fp('WS89_CollegeAve_lot_median_CURB_concrete_UNVERIFIED')
# LiDAR fine ground grid (0.25 m) from ev98
g=np.load('scripts/ws98/gnd025.npy'); GX0,GY1,GR=-245,-55,0.25
nan=np.isnan(g); idx=ndimage.distance_transform_edt(nan,return_distances=False,return_indices=True); gf=g[tuple(idx)]
gs=ndimage.gaussian_filter(gf,2.0)  # ~0.5 m sigma
def L(x,y,arr=gs):
    fx=(x-GX0)/GR; fy=(GY1-y)/GR; j=int(fx); i=int(fy); tx=fx-j; ty=fy-i
    return float(arr[i,j]*(1-tx)*(1-ty)+arr[i,j+1]*tx*(1-ty)+arr[i+1,j]*(1-tx)*ty+arr[i+1,j+1]*tx*ty)
# island from residual mask
isl=json.load(open('scripts/ws98/island_pts.json'))['pts']
I=unary_union([box(x-0.26,y-0.26,x+0.26,y+0.26) for x,y in isl if -222.4<x<-203 and -81.5<y<-68.5])
I=I.buffer(0.4).buffer(-0.9).buffer(0.5)
I=I.difference(ROAD.buffer(0.05)).difference(WS89.buffer(0.02))
if I.geom_type=='MultiPolygon': I=max(I.geoms,key=lambda p:p.area)
I=I.simplify(0.12)
print('island area',round(I.area,1),I.bounds)
# pad (raised concrete walk head)
PAD=Polygon([(-216.4,-84.7),(-207.6,-84.7),(-206.8,-85.5),(-206.8,-87.6),(-207.6,-88.3),(-216.4,-88.3)])
PAD=PAD.difference(ROAD.buffer(0.05))
# aisle
A=box(-217.0,-84.7,-200,-68).difference(I).difference(CARR).difference(PAD)
A=A.difference(LOT.buffer(-0.35))
A=A.intersection(box(-217.0,-84.7,-200,-68))
if A.geom_type=='MultiPolygon':
    print('aisle parts',[round(p.area,1) for p in A.geoms]); A=max(A.geoms,key=lambda p:p.area)
print('aisle area',round(A.area,1))
# boundary z correction: lot sheet + carriageway verts near
ref=[]
NEWF=unary_union([A,PAD,I])
EV=json.load(open('scripts/ws98/teval98.json'))
for n in D:
    if n.startswith(('WS76','WS79','WS96','WS75','WS27_CollegeAve_carr','WS27_CollegeAve_curb_right')):
        for v in D[n]['v']:
            if -220<v[0]<-198 and -92<v[1]<-66 and NEWF.distance(Point(v[0],v[1]))<1.5:
                z=v[2]-(0.15 if 'curb' in n else 0.0)
                ref.append((v[0],v[1],z-L(v[0],v[1])))
PAV=unary_union([LOT,ROAD,NEWF,WS77])
for x,y,z in EV:
    p=Point(x,y)
    if not PAV.buffer(0.2).contains(p) and NEWF.distance(p)<1.6 and y<-84: ref.append((x,y,z-L(x,y)))
ref=np.array([r for r in ref if r[2]==r[2]]); print('ref verts',len(ref),'corr p10/50/90',np.round(np.percentile(ref[:,2],[10,50,90]),2))
def zA(x,y):
    d=np.hypot(ref[:,0]-x,ref[:,1]-y); k=np.argsort(d)[:10]
    w=1/(d[k]+0.4)**2; corr=(w*ref[k,2]).sum()/w.sum()
    return L(x,y)+corr
def tri(poly,zf,step=0.5):
    V=[];F=[];vm={}
    def vid(x,y):
        k=(round(x,4),round(y,4))
        if k not in vm: vm[k]=len(V); V.append((x,y,zf(x,y)))
        return vm[k]
    polys=getattr(poly,'geoms',[poly])
    for P in polys:
        # densify + interior grid points
        Pd=shapely.segmentize(P,step)
        mx0,my0,mx1,my1=P.bounds
        pts=[Point(x,y) for x in np.arange(np.floor(mx0),mx1,step) for y in np.arange(np.floor(my0),my1,step) if P.buffer(-0.1).contains(Point(x,y))]
        T=shapely.constrained_delaunay_triangles(Pd)
        # refine: simple — use delaunay of boundary+interior points clipped
        allp=shapely.MultiPoint(list(Pd.exterior.coords)+[c for r in Pd.interiors for c in r.coords]+[(p.x,p.y) for p in pts])
        T2=shapely.delaunay_triangles(allp)
        for t in T2.geoms:
            if not P.buffer(1e-3).contains(t.centroid) or not P.buffer(0.02).contains(t): continue
            c=list(t.exterior.coords)[:3]
            F.append([vid(*c[0]),vid(*c[1]),vid(*c[2])])
    return V,F
OUT={}
OUT['aisle']=tri(A,lambda x,y:zA(x,y)-0.004)
# island: top = LiDAR (mulch ~ curb top), curb ring 0.15 wide
ring=I.difference(I.buffer(-0.15)); inner=I.buffer(-0.15)
def zI(x,y): return zA(x,y)+0.15
OUT['island_mulch']=tri(inner,lambda x,y:zI(x,y)-0.03)
OUT['island_curb']=tri(ring,lambda x,y:zA(x,y)+0.15,step=0.4)
Vp,Fp=tri(PAD,lambda x,y:zA(x,y)+0.13)
P3=np.array(Vp); Ap=np.c_[P3[:,0],P3[:,1],np.ones(len(P3))]; pc,*_=np.linalg.lstsq(Ap,P3[:,2],rcond=None)
print('pad plane slope x %.3f y %.3f'%(pc[0],pc[1]))
zP=lambda x,y: float(pc[0]*x+pc[1]*y+pc[2])
OUT['pad']=([(x,y,zP(x,y)) for x,y,_ in Vp],Fp)
OUT['outlines']={'island':list(I.exterior.coords),'pad':list(PAD.exterior.coords) if PAD.geom_type=='Polygon' else []}
# curb faces to delete (curb cut at aisle mouth): curb_right faces within 0.6 m of aisle polygon
C=D['WS27_CollegeAve_curb_right_UNVERIFIED']; cut=[]
for fi,f in enumerate(C['f']):
    V=C['v']; cx=np.mean([V[i][0] for i in f]); cy=np.mean([V[i][1] for i in f])
    if A.buffer(0.6).contains(Point(cx,cy)) and not I.buffer(0.3).contains(Point(cx,cy)) and -85.0<cy<-79.6: cut.append([round(cx,3),round(cy,3)])
print('curb faces to cut',len(cut))
OUT['curb_cut_centroids']=cut
# terrain
T=D['Terrain_LiDAR_DTM_1m']; NEW=unary_union([A,I,PAD]); PAVED=unary_union([NEW,LOT,ROAD,WS77,WS89])
tl=[];tr=[]
W=box(-222,-92,-203,-66)
for k,(x,y,z) in enumerate(T['v']):
    p=Point(x,y)
    if not W.contains(p): continue
    if NEW.buffer(0.25).contains(p):
        zs = zA(x,y)-0.06
        if z>zs: tl.append((T['idx'][k],round(zs-z,3)))
        continue
    if PAVED.buffer(0.15).contains(p): continue
    d=PAVED.distance(p)
    if d>2.0: continue
    zt=L(x,y,gf)-0.012  # LiDAR ground (fine, unsmoothed-filled)
    dz=zt-z
    if 0.01<dz<0.45: tr.append((T['idx'][k],round(dz,3)))
SV=[]
for n in D:
    if n.startswith(('WS76','WS79','WS96','WS75','WS80','WS77')): SV+= [v for v in D[n]['v'] if -222<v[0]<-203 and -94<v[1]<-82]
SV=np.array(SV)
LB=unary_union([LOT,WS77]).boundary; PB=PAD.boundary
done={i for i,_ in tl}; tr=[]
W2=box(-222,-94,-204,-83.5)
for k,(x,y,z) in enumerate(T['v']):
    p=Point(x,y); ii=T['idx'][k]
    if ii in done or not W2.contains(p) or PAVED.buffer(0.1).contains(p): continue
    dp=PB.distance(p); dl=LB.distance(p)
    if min(dp,dl)>2.5: continue
    if dp<=dl:
        q=PB.interpolate(PB.project(p)); ze=zP(q.x,q.y)-0.02; d=dp
    else:
        q=LB.interpolate(LB.project(p)); dd=np.hypot(SV[:,0]-q.x,SV[:,1]-q.y); kk=np.argsort(dd)[:4]; ze=float(np.median(SV[kk,2]))-0.03; d=dl
    tgt=ze-0.12*d; dz=tgt-z
    if 0.01<dz<1.2: tr.append((ii,round(dz,3)))
print('terrain lower',len(tl),'raise',len(tr),'max raise',max([d for _,d in tr],default=0))
OUT['terrain_lower']=tl; OUT['terrain_raise']=tr
for k in ('aisle','island_mulch','island_curb','pad'): print(k,len(OUT[k][0]),'v',len(OUT[k][1]),'f', 'z',round(min(v[2] for v in OUT[k][0]),2),round(max(v[2] for v in OUT[k][0]),2))
json.dump(OUT,open('scripts/ws98/build98.json','w'))
if os.environ.get('DBG'):
    for k,(x,y,z) in enumerate(T['v']):
        if -220<x<-215.5 and -92.5<y<-87.5:
            p=Point(x,y); print('DBG',round(x,2),round(y,2),round(z,2),'paved' if PAVED.buffer(0.1).contains(p) else '', 'lot' if LOT.contains(p) else '', 'ws77' if WS77.contains(p) else '', round(LB.distance(p),2))
