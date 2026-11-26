# ws248: raw Terrain_LiDAR_DTM_1m vertices vs LiDAR class-2 ground (2023, 2017 fallback; 1 m cells, 3x3 nan-median fill)
import bpy, os, sys, numpy as np
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws248a.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; M=np.array(T.matrix_world); me=T.data
co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); W=(co@M[:3,:3].T)+M[:3,3]
X0,Y0=-320.,-20.
G23=np.load('/workspace/nj-scenes/montclair-state/scripts/ws248/g1m_23.npy'); G17=np.load('/workspace/nj-scenes/montclair-state/scripts/ws248/g1m_17.npy')
G=np.where(np.isfinite(G23),G23,G17)
def fill(G):
    H=G.copy(); ny,nx=G.shape
    pad=np.pad(G,2,constant_values=np.nan)
    st=np.stack([pad[2+dy:2+dy+ny,2+dx:2+dx+nx] for dy in range(-2,3) for dx in range(-2,3)])
    med=np.nanmedian(st,axis=0); return np.where(np.isfinite(G),G,med)
import warnings; warnings.filterwarnings('ignore')
Gf=fill(G)
sel=np.where((W[:,0]>-318)&(W[:,0]<-142)&(W[:,1]>-18)&(W[:,1]<218))[0]
ix=(W[sel,0]-X0).astype(int); iy=(W[sel,1]-Y0).astype(int); L=Gf[iy,ix]; D=W[sel,2]-L
np.save('/workspace/nj-scenes/montclair-state/scripts/ws248/d248.npy',np.c_[sel,W[sel],L])
ok=np.isfinite(D); print('D248 verts',len(sel),'with lidar',ok.sum(),flush=True)
for thr in (0.3,0.6,1.0,1.5,2.0): print('D248 |d|>',thr,int((np.abs(D[ok])>thr).sum()),flush=True)
# 10 m block summary
for by in range(200,-20,-10):
    row=[]
    for bx in range(-310,-150,10):
        m=ok&(W[sel,0]>=bx)&(W[sel,0]<bx+10)&(W[sel,1]>=by)&(W[sel,1]<by+10)
        row.append('%5.1f'%np.median(D[m]) if m.sum()>5 else '   . ')
    print('D248 y%4d '%by+' '.join(row),flush=True)
sys.stdout.flush(); os._exit(0)
