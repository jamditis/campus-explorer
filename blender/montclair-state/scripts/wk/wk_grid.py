# tj parallel: 1 m DSM/DTM grid round Bohn Hall (x 190..290, y 330..430 local) from the B23 + B17 tiles (same frame as north/scripts/prep_lidar.py). Read-only.
# run: PYTHONPATH=/workspace/nj-scenes/pylib_las:/workspace/nj-scenes/blender_pylib_proj python3 scripts/tj/tj_bohn_grid.py
import laspy, numpy as np, glob, json
from pyproj import Transformer
OE,ON=575880.0,738340.0; F=1200/3937; X0,X1,Y0,Y1=140.,310.,285.,420.
nx,ny=int(X1-X0),int(Y1-Y0)
files=sorted(glob.glob('north/data/USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_*.laz'))
res={}
for fn in files:
    try: rd=laspy.open(fn)
    except Exception as e: print('skip',fn,e); continue
    crs=rd.header.parse_crs(); name=crs.name if crs else '?'
    tr=None
    if crs is not None and crs.to_epsg()!=6527 and 'New Jersey (ftUS)' not in name:
        tr=Transformer.from_crs(crs.sub_crs_list[0] if crs.is_compound else crs,6527,always_xy=True)
    vf=0.3048006096 if ('ftUS' in name.split('+')[-1] or 'foot' in name.split('+')[-1].lower()) else 1.0
    gs=np.zeros((ny,nx)); gc=np.zeros((ny,nx)); dsm=np.full((ny,nx),np.nan); n=0
    for ch in rd.chunk_iterator(3_000_000):
        ex,ey=np.asarray(ch.x),np.asarray(ch.y)
        if tr is not None: ex,ey=tr.transform(ex,ey)
        x=(ex-OE)*F; y=(ey-ON)*F; m=(x>=X0)&(x<X1)&(y>=Y0)&(y<Y1)
        if not m.any(): continue
        z=np.asarray(ch.z)[m]*vf; c=np.asarray(ch.classification)[m]; ix=(x[m]-X0).astype(int); iy=(y[m]-Y0).astype(int); n+=int(m.sum())
        s=c==2; np.add.at(gs,(iy[s],ix[s]),z[s]); np.add.at(gc,(iy[s],ix[s]),1)
        s=c!=7; np.fmax.at(dsm,(iy[s],ix[s]),z[s])
    print(fn.split('/')[-1],name[:60],'pts',n,flush=True)
    if n: res[fn.split('/')[-1]]=dict(dtm=np.where(gc>0,gs/np.maximum(gc,1),np.nan),dsm=dsm)
np.savez_compressed('data/wk/chm_grid_1m.npz',**{k+'__'+a:v[a] for k,v in res.items() for a in ('dtm','dsm')},extent=np.array([X0,X1,Y0,Y1,1.0]))
print('saved')
