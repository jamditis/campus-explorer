import bpy, numpy as np, os, sys
sys.path.insert(0,'/workspace/nj-scenes/pylib_scipy')
B='/workspace/nj-scenes/montclair-state/scripts/ws100/'
f=np.load(B+'field100b.npz'); F=f['F']; FX,FY,FR=float(f['X0']),float(f['Y0']),float(f['R'])
def field(xy):
    fx=(xy[:,0]-FX)/FR; fy=(xy[:,1]-FY)/FR
    i0=np.clip(np.floor(fx).astype(int),0,F.shape[1]-2); j0=np.clip(np.floor(fy).astype(int),0,F.shape[0]-2)
    tx=np.clip(fx-i0,0,1); ty=np.clip(fy-j0,0,1)
    return (F[j0,i0]*(1-tx)*(1-ty)+F[j0,i0+1]*tx*(1-ty)+F[j0+1,i0]*(1-tx)*ty+F[j0+1,i0+1]*tx*ty)
def getW(o):
    me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); return co@M[:3,:3].T+M[:3,3], M
def setW(o,W,M):
    Mi=np.linalg.inv(M); L=W@Mi[:3,:3].T+Mi[:3,3]; o.data.vertices.foreach_set('co',L.ravel()); o.data.update()
pass
pass
C=np.load(B+'cap100.npz'); G=C['G']; CX,CY,CR=float(C['X0']),float(C['Y0']),float(C['R'])
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; W,M=getW(t)
i=((W[:,0]-CX)/CR).astype(int); j=((W[:,1]-CY)/CR).astype(int); ok=(i>=0)&(i<G.shape[1])&(j>=0)&(j<G.shape[0])
cap=np.full(len(W),np.inf); cap[ok]=G[j[ok],i[ok]]-0.05
m=W[:,2]>cap; W[m,2]=cap[m]; c=int(m.sum())
setW(t,W,M); print('F100 terrain capped',c)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('F100 SAVED')
