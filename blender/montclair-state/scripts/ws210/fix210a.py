# ws210 W30: Kasser steps foreground (W of College Ave, x -216..curb, y -114..-97.4) - lawn bank under the PinOak/RedMaple canopy.
# Evidence: base Terrain here deviates -0.4..-1.4 m from the raw NJ LiDAR DTM (data/dtm_1m.npy) with local-plane residuals 10-56 cm
# (vs 1-5 cm on undisturbed lawn W of x -214) = old seating/regrade lumps, and stops ~40 cm below the College Ave W curb top (gap).
# Raw DTM shows one smooth bank rising to a flat road-level shoulder at the curb; 2020 ortho: canopy-shaded lawn, no walk W of the curb.
# Regrade: target = zW(y) + (zE(y)-zW(y))*s, s = smoothed DTM profile normalised between x=-215.5 (toe, current terrain kept) and the
# curb back (zE = curb top - 3 cm). Feathered at W/N/S edges; nothing E of the curb back line is touched.
import bpy, numpy as np
dtm=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy').astype(float)
def gz(x,y):
    fx=x+249.5; fy=y+249.5; j=np.floor(fx).astype(int); i=np.floor(fy).astype(int); a=fx-j; b=fy-i
    return dtm[i,j]*(1-a)*(1-b)+dtm[i,j+1]*a*(1-b)+dtm[i+1,j]*(1-a)*b+dtm[i+1,j+1]*a*b
def gzs(x,y,s=0.8):
    o=np.array([-1,0,1])*s; acc=0; ww=0
    for dx in o:
        for dy in o:
            w=np.exp(-(dx*dx+dy*dy)/(2*(s*0.8)**2)); acc=acc+w*gz(x+dx,y+dy); ww+=w
    return acc/ww
xcw=lambda y: -202.92+(y+96)*0.2322          # W (back) face of WS27 curb right
zct=lambda y: 128.34+(y+96)*0.0444           # curb top
XW=-215.5
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; mw=T.matrix_world; mi=mw.inverted()
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
W=np.c_[co,np.ones(len(co))]@np.array(mw).T; x,y,z=W[:,0],W[:,1],W[:,2]
# Footpaths_OSM base-mesh S edge (walk climbs the real bank 125.1 -> 128.1): terrain meets it flush (-3 cm), never above it
WEX=np.array([-216.2,-213.55,-212.21,-210.87,-209.53,-208.19,-206.85,-205.51,-204.29,-203.0])
WEY=np.array([-97.48,-98.02,-97.47,-96.91,-96.36,-95.80,-95.25,-94.69,-94.87,-95.05])
WEZ=np.array([125.10,126.02,126.72,127.44,127.95,128.06,128.14,128.14,128.18,128.18])
ywe=lambda xq: np.interp(xq,WEX,WEY); zwe=lambda xq: np.interp(xq,WEX,WEZ)
box=(y>-114.2)&(y<ywe(x)-0.05)&(x>-216.2)&(x<xcw(y)+0.05)
# toe height zW(y): current terrain near x=XW, smoothed along y
k0=(np.abs(x-XW)<0.8)&(y>-118)&(y<-94)
def zW(yq):
    w=np.exp(-((y[k0][None,:]-np.atleast_1d(yq)[:,None])**2)/(2*1.2**2)); return (w*z[k0]).sum(1)/w.sum(1)
xb,yb=x[box],y[box]
xe=xcw(yb)-0.3
dW=gzs(np.full_like(xb,XW),yb); dE=gzs(xe,yb); dP=gzs(np.minimum(np.maximum(xb,XW),xe),yb)
s=np.clip((dP-dW)/np.maximum(dE-dW,0.3),0,1)
zw=zW(yb); ze=zct(yb)-0.03
tgt=zw+(ze-zw)*s
ramp=lambda v,a,b: np.clip((v-a)/(b-a),0,1)
wx=ramp(xb,-216.2,-214.6)
wy=ramp(yb,-114.2,-112.2)
w=wx*wy
# within 0.35 m of the curb back: force flush (no gap under curb) where wy allows
dn=ywe(xb)-yb; t=np.clip((dn-0.4)/1.6,0,1); t=t*t*(3-2*t)
tgt=(zwe(xb)-0.03)*(1-t)+tgt*t
nz=z[box]+w*(tgt-z[box])
dz=nz-z[box]
print('F210a verts',box.sum(),'dz min/max %.3f %.3f'%(dz.min(),dz.max()),'mean|dz| %.3f'%np.abs(dz).mean(),flush=True)
W[box,2]=nz
L=W@np.array(mi).T; me.vertices.foreach_set('co',L[:,:3].ravel()); me.update()
# Materials: the bank band carried an ortho-draped 'Ground_ortho_grass' swath (mat 0) edged by scattered sliver faces set to
# 'WS3_Concrete_panels_sawcut' (mat 3; bs_orig_mat=0) - no OSM path, no paving visible in the 2020 ortho (uniform canopy-shaded
# lawn; the only walk is Footpaths_OSM to the N) -> artefacts. Unify to the surrounding lawn (mat 2 COLE_lawn_post2020_bs).
pc=np.zeros(len(me.polygons)*3); me.polygons.foreach_get('center',pc); pc=pc.reshape(-1,3)
PW=np.c_[pc,np.ones(len(pc))]@np.array(mw).T; px,py=PW[:,0],PW[:,1]
mi_=np.zeros(len(me.polygons),dtype=np.int32); me.polygons.foreach_get('material_index',mi_)
sel=(px>-221)&(px<xcw(py)-0.1)&(py>-115)&(py<ywe(px)-0.2)&((mi_==0)|(mi_==3))
print('F210a mat->2: from0',int((sel&(mi_==0)).sum()),'from3',int((sel&(mi_==3)).sum()),flush=True)
mi_[sel]=2; me.polygons.foreach_set('material_index',mi_); me.update()
