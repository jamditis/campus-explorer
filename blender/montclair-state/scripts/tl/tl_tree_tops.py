# tl parallel (read-only): tree tops round the east dorms (Stone/Blanton/Bohn/Webster lawn), x 50..300, y 320..520 local,
# from 2017 B17 + 2023 LiDAR vegetation returns (class 3/4/5, plus class 1 >2.5 m above ground outside OSM buildings).
# Output data/tl/dorm_tree_tops.json: [x,y,ground_z,height,crown_radius,src] for the next session's tree placement.
# run: PYTHONPATH=/workspace/nj-scenes/pylib_las:/workspace/nj-scenes/blender_pylib_proj python3 scripts/tl/tl_tree_tops.py
import laspy, numpy as np, glob, json
from pyproj import Transformer
from shapely.geometry import Polygon; from shapely import contains_xy; from shapely.ops import unary_union
OE,ON=575880.0,738340.0; F=1200/3937; X0,X1,Y0,Y1=50.,300.,320.,520.
nx,ny=int(X1-X0),int(Y1-Y0)
files=['data/lpc_2023_J5D6.laz']+sorted(glob.glob('north/data/USGS_LPC_NJ_NE6County_B23_*.laz'))+sorted(glob.glob('north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_*.laz'))
gs=np.zeros((ny,nx)); gc=np.zeros((ny,nx)); veg=np.full((ny,nx),np.nan); unc=np.full((ny,nx),np.nan); srcs=[]
for fn in files:
    try: rd=laspy.open(fn)
    except Exception as e: print('skip',fn,e); continue
    crs=rd.header.parse_crs(); name=crs.name if crs else '?'; tr=None
    if crs is not None and crs.to_epsg()!=6527 and 'New Jersey (ftUS)' not in name:
        tr=Transformer.from_crs(crs.sub_crs_list[0] if crs.is_compound else crs,6527,always_xy=True)
    vf=0.3048006096 if ('ftUS' in name.split('+')[-1] or 'foot' in name.split('+')[-1].lower()) else 1.0
    n=0
    for ch in rd.chunk_iterator(2_000_000):
        ex,ey=np.asarray(ch.x),np.asarray(ch.y)
        if tr is not None: ex,ey=tr.transform(ex,ey)
        x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
        if not m.any(): continue
        z=np.asarray(ch.z)[m]*vf; c=np.asarray(ch.classification)[m]; ix=(x[m]-X0).astype(int); iy=(y[m]-Y0).astype(int); n+=int(m.sum())
        s=c==2; np.add.at(gs,(iy[s],ix[s]),z[s]); np.add.at(gc,(iy[s],ix[s]),1)
        s=(c>=3)&(c<=5); np.fmax.at(veg,(iy[s],ix[s]),z[s])
        s=c==1; np.fmax.at(unc,(iy[s],ix[s]),z[s])
    print(fn.split('/')[-1],'pts',n,flush=True)
    if n: srcs.append(fn.split('/')[-1])
dtm=np.where(gc>0,gs/np.maximum(gc,1),np.nan)
# fill dtm holes with nearest-ish (iterative mean of neighbours)
for it in range(30):
    h=~np.isfinite(dtm)
    if not h.any(): break
    p=np.pad(dtm,1,constant_values=np.nan); st=np.stack([p[1:-1,:-2],p[1:-1,2:],p[:-2,1:-1],p[2:,1:-1]]); mn=np.nanmean(np.where(np.isfinite(st),st,np.nan),axis=0)
    dtm[h]=mn[h]
W=json.load(open('data/td/east_osm.json'))['ways']
blds=[Polygon(v['pts']).buffer(1.5) for k,v in W.items() if v.get('tags',{}).get('building') or v.get('building')]
B=unary_union(blds) if blds else None
ys,xs=np.mgrid[0:ny,0:nx]; CX,CY=xs+X0+.5,ys+Y0+.5
inb=contains_xy(B,CX,CY) if B is not None else np.zeros_like(CX,bool)
top=np.fmax(veg,np.where(inb,np.nan,unc)); chm=top-dtm; chm[~np.isfinite(chm)]=0; chm[inb]=np.minimum(chm[inb],0)
# smooth 3x3 then local maxima in a 5x5 window, height >= 4 m
p=np.pad(chm,1,mode='edge'); sm=sum(p[1+dy:1+dy+ny,1+dx:1+dx+nx] for dy in (-1,0,1) for dx in (-1,0,1))/9
p=np.pad(sm,2,mode='constant'); mx=np.max(np.stack([p[2+dy:2+dy+ny,2+dx:2+dx+nx] for dy in range(-2,3) for dx in range(-2,3)]),axis=0)
pk=(sm>=mx-1e-6)&(sm>=4.0)
T=[]
for j,i in zip(*np.nonzero(pk)):
    h=float(chm[j,i]); 
    # crown radius: distance to where chm drops below half the peak, 8 directions
    rs=[]
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)):
        r=0
        for k in range(1,12):
            jj,ii=j+dy*k,i+dx*k
            if not(0<=jj<ny and 0<=ii<nx) or chm[jj,ii]<h*0.5: break
            r=k*(1.414 if dx and dy else 1)
        rs.append(r)
    T.append([round(float(CX[j,i]),1),round(float(CY[j,i]),1),round(float(dtm[j,i]),2),round(h,1),round(max(1.5,float(np.median(rs))+0.5),1)])
json.dump({'extent':[X0,X1,Y0,Y1],'sources':srcs,'note':'local maxima of 1 m CHM (veg classes 3-5 + unclassified outside OSM bldg+1.5 m), smoothed 3x3, >=4 m; crown r = half-height radius median+0.5','trees':T},open('data/tl/dorm_tree_tops.json','w'))
print('trees',len(T),'h p50',np.median([t[3] for t in T]) if T else None)
