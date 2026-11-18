import bpy, math
from mathutils import Vector
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=TZ.matrix_world; nm=mw.to_3x3()
mats=[s.material.name if s.material else None for s in TZ.material_slots]; print('MATS',mats)
a=math.radians(-13.5); u=Vector((math.cos(a),math.sin(a),0)); v=Vector((-math.sin(a),math.cos(a),0))
from collections import defaultdict
agg=defaultdict(lambda:[1e9,-1e9,1e9,-1e9,1e9,-1e9,0,0.0])
for f in TZ.data.polygons:
  n=(nm@f.normal).normalized()
  if n.dot(v)<0.8: continue
  key=mats[f.material_index]
  for i in f.vertices:
    p=mw@TZ.data.vertices[i].co; A=agg[key]
    pu=p.dot(u); pv=p.dot(v)
    A[0]=min(A[0],pu);A[1]=max(A[1],pu);A[2]=min(A[2],p.z);A[3]=max(A[3],p.z);A[4]=min(A[4],pv);A[5]=max(A[5],pv)
  agg[key][6]+=1; agg[key][7]+=f.area
for k,A in agg.items(): print('NF',k,[round(x,2) for x in A])
