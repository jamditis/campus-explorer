# ws210 W30b: lawn strip N of the Footpaths_OSM walk climbing the bank (x -214.5..-206, between the walk and the WS98 pad / WS205 apron).
# Base Terrain sat up to ~0.8 m below the walk's N edge (walk read as a raised arch with an exposed dark side). Regrade: flush with
# the walk N edge (-3 cm) within 0.4 m, then blend over 2 m into the raw-DTM shape offset to stay continuous. Base mesh only.
import bpy, numpy as np
dtm=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy').astype(float)
def gz(x,y):
    fx=x+249.5; fy=y+249.5; j=np.floor(fx).astype(int); i=np.floor(fy).astype(int); a=fx-j; b=fy-i
    return dtm[i,j]*(1-a)*(1-b)+dtm[i,j+1]*a*(1-b)+dtm[i+1,j]*(1-a)*b+dtm[i+1,j+1]*a*b
def gzs(x,y,s=0.8):
    acc=0; ww=0
    for dx in (-s,0,s):
        for dy in (-s,0,s):
            w=np.exp(-(dx*dx+dy*dy)/(2*(s*0.8)**2)); acc=acc+w*gz(x+dx,y+dy); ww+=w
    return acc/ww
NX=np.array([-216.0,-214.0,-212.63,-211.26,-209.89,-208.52,-207.15,-205.5])
NY=np.array([-95.53,-94.96,-94.39,-93.83,-93.26,-92.69,-92.13,-91.6])
NZ=np.array([125.31,126.17,126.99,127.68,127.88,127.97,128.10,128.14])
ywn=lambda q: np.interp(q,NX,NY); zwn=lambda q: np.interp(q,NX,NZ)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; mw=T.matrix_world; mi=mw.inverted()
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
W=np.c_[co,np.ones(len(co))]@np.array(mw).T; x,y,z=W[:,0],W[:,1],W[:,2]
dn=y-ywn(x)
box=(x>-214.6)&(x<-205.9)&(dn>0.05)&(dn<4.0)
xb,yb=x[box],y[box]; d=dn[box]
off=zwn(xb)-0.03-gzs(xb,ywn(xb))
far=gzs(xb,yb)+off
t=np.clip((d-0.4)/2.0,0,1); t=t*t*(3-2*t)
tgt=(zwn(xb)-0.03)*(1-t)+far*t
ramp=lambda v,a,b: np.clip((v-a)/(b-a),0,1)
w=np.minimum(ramp(xb,-214.6,-213.6),ramp(-xb,205.9,206.8))*np.minimum(1,ramp(-d,-4.0,-3.0))
nz=z[box]+w*(tgt-z[box]); dz=nz-z[box]
print('F210b verts',box.sum(),'dz min/max %.3f %.3f'%(dz.min(),dz.max()),flush=True)
W[box,2]=nz; L=W@np.array(mi).T; me.vertices.foreach_set('co',L[:,:3].ravel()); me.update()
