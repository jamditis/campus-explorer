import numpy as np, types, sys
src=open("/workspace/nj-scenes/montclair-state/scripts/ws210/fix210a.py").read().split("# Materials:")[0]
T=np.load('/workspace/nj-scenes/montclair-state/scripts/ws210/V_Terrain_LiDA.npy'); CO0=T[:,1:].copy()
class VS:
  def __len__(s): return len(CO0)
  def foreach_get(s,n,a): a[:]=CO0.ravel()
  def foreach_set(s,n,a): np.save('/tmp/nz.npy',np.asarray(a).reshape(-1,3))
class Me:
  vertices=VS()
  def update(s): pass
class M(list):
  def inverted(s): return np.eye(4)
class Ob: data=Me(); matrix_world=M(np.eye(4).tolist())
fake=types.ModuleType('bpy'); fake.data=types.SimpleNamespace(objects={'Terrain_LiDAR_DTM_1m':Ob()}); sys.modules['bpy']=fake
exec(src)
N=np.load('/tmp/nz.npy'); x,y,z=N.T
res=np.zeros(len(x))
for j in range(len(x)):
  d=np.hypot(x-x[j],y-y[j]); k=d<1.6
  A=np.c_[np.ones(k.sum()),x[k]-x[j],y[k]-y[j]]; c,*_=np.linalg.lstsq(A,z[k],rcond=None); res[j]=z[j]-c[0]
for yy in np.arange(-94,-116,-2):
  s=''
  for xx in np.arange(-219,-201,1):
    k=(np.abs(x-xx)<0.5)&(np.abs(y-yy)<1)
    s+= ' %4.0f'%(np.abs(res[k]).max()*100) if k.any() else '    .'
  print('%5d'%yy+s)
for yy in (-100,-105,-110):
  k=np.abs(y-yy)<0.35; o=np.argsort(x[k]); print(yy,[ (round(a,1),round(b-120,2)) for a,b in zip(x[k][o],z[k][o]) if -217<a<-203])
