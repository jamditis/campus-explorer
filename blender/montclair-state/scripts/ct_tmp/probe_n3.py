import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
L=Vector((-222.0,-128.0,162.0));T=Vector((-186.0,-74.0,130.0)); q=(T-L).normalized().to_track_quat('-Z','Y'); fx=36/30; fy=fx*720/1280
from collections import Counter
cnt=Counter(); ex={}
for py in range(440,620,3):
  for px in range(540,740,3):
    r=(q@Vector(((px/1280-0.5)*fx,(0.5-py/720)*fy,-1))).normalized()
    h,l,nn,i,o,m=sc.ray_cast(dg,L,r)
    if h and o:
      cnt[o.name]+=1; ex.setdefault(o.name,(px,py,tuple(round(c,2) for c in l)))
for k,v in cnt.most_common(): print('HIT',v,k[:70],ex[k],flush=True)
