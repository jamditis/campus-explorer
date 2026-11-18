import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=tuple(os.environ['PF'].split('|'))
X0,X1,Y0,Y1,ST=map(float,os.environ['BOX'].split(','))
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
T={}
for o in b.objects:
    if o.type!='MESH': continue
    me=o.data; mw=o.matrix_world
    T[o.name]=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
    print('A207 obj',o.name,len(me.vertices),[s.material.name if s.material else None for s in o.material_slots][:3])
names=list(T)
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
xs=np.arange(X0,X1+1e-6,ST); ys=np.arange(Y0,Y1+1e-6,ST)
Z=np.full((len(ys),len(xs),len(names)),np.nan)
for j,y in enumerate(ys):
  for i,x in enumerate(xs):
    for k,n in enumerate(names):
      z=hz(T[n],x,y)
      if z is not None: Z[j,i,k]=z
np.save('/tmp/a207.npy',Z); import json; json.dump({'names':names,'xs':xs.tolist(),'ys':ys.tolist()},open('/tmp/a207.json','w'))
top=np.nanargmax(np.where(np.isnan(Z),-1e9,Z),axis=2); zt=np.nanmax(Z,axis=2)
# top-object changes: jump in z across neighbours
for ax,lab in ((0,'y'),(1,'x')):
  dz=np.abs(np.diff(zt,axis=ax)); ch=np.diff(top,axis=ax)!=0
  m=ch&(dz>0.01)
  print('A207 %s-neighbour top changes'%lab,int(ch.sum()),'with |dz|>1cm',int(m.sum()),'>3cm',int((ch&(dz>0.03)).sum()),'max %.3f'%np.nanmax(np.where(ch,dz,0)))
# overlap spread: where >=2 surfaces, top-second
cnt=(~np.isnan(Z)).sum(2)
S=np.sort(np.where(np.isnan(Z),-1e9,Z),axis=2)
sp=S[:,:,-1]-S[:,:,-2]; ov=cnt>=2
print('A207 overlap cells',int(ov.sum()),'spread<2mm',int((ov&(sp<0.002)).sum()),'2-10mm',int((ov&(sp>=0.002)&(sp<0.01)).sum()),'>1cm',int((ov&(sp>=0.01)).sum()))
for k,n in enumerate(names): print('A207',k,n[:40],'topcells',int((top==k).sum()))
