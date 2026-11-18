import bpy, mathutils
x0,x1,y0,y1=-186,-126,73,164
from collections import Counter
cnt=Counter(); ex={}
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
    if x0<cx<x1 and y0<cy<y1:
        k=tuple(c.name for c in o.users_collection)[0] if o.users_collection else '-'
        cnt[k]+=1; ex.setdefault(k,o.name)
for k,v in cnt.most_common(): print('COLL',v,k,'|',ex[k][:60])
