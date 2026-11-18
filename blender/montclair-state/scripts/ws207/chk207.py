# after CHAIN: re-run the an207 overlap/step stats on the in-memory objects
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
PF=('WS76_accessible_lot_asphalt','WS75_sprague_lot_asphalt','WS79_lot_E_patch','WS96_lot_E_edge','WS94_lot_slit')
T={o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons]) for o in bpy.data.objects if o.name.startswith(PF)}
import os; X0,X1,Y0,Y1=map(float,os.environ.get("CB","-224,-213,-89,-79").split(",")); xs=np.arange(X0,X1+1e-6,0.1); ys=np.arange(Y0,Y1+1e-6,0.1); names=list(T)
Z=np.full((len(ys),len(xs),len(names)),np.nan)
for j,y in enumerate(ys):
  for i,x in enumerate(xs):
    for k,n in enumerate(names):
      h=T[n].ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80)
      if h[0] is not None: Z[j,i,k]=h[0].z
top=np.argmax(np.where(np.isnan(Z),-1e9,Z),axis=2); zt=np.nanmax(Z,axis=2)
for ax,lab in ((0,'y'),(1,'x')):
  dz=np.abs(np.diff(zt,axis=ax)); ch=np.diff(top,axis=ax)!=0
  print('C207 %s top changes'%lab,int(ch.sum()),'>1cm',int((ch&(dz>0.01)).sum()),'>3cm',int((ch&(dz>0.03)).sum()),'max %.3f'%np.nanmax(np.where(ch,dz,0)))
cnt=(~np.isnan(Z)).sum(2); S=np.sort(np.where(np.isnan(Z),-1e9,Z),axis=2); sp=S[:,:,-1]-S[:,:,-2]; ov=cnt>=2
print('C207 overlap',int(ov.sum()),'<4mm',int((ov&(sp<0.004)).sum()),'>1cm',int((ov&(sp>=0.01)).sum()))
dz=np.abs(np.diff(zt,axis=0)); ch=np.diff(top,axis=0)!=0; jj,ii=np.where(ch&(dz>0.01))
from collections import Counter
print('C207 locs',Counter([(round(xs[i]),round(ys[j])) for j,i in zip(jj,ii)]).most_common(12))
jj,ii=np.where(ov&(sp>=0.01)); print('C207 ovlocs',Counter([(round(xs[i]),round(ys[j])) for j,i in zip(jj,ii)]).most_common(12))
