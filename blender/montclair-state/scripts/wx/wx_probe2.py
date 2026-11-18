import bpy, json, numpy as np, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
X0,X1,Y0,Y1=128,150,250,322
hit=[]
for o in O:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[b.x for b in bb]; ys=[b.y for b in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if (max(xs)-min(xs))*(max(ys)-min(ys))>200000: continue
    hit.append((o.name,len(o.data.vertices),round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1)))
for h in hit: print('OBJ',h,flush=True)
dg=bpy.context.evaluated_depsgraph_get()
B={}
for h in hit:
    o=O[h[0]]
    if h[1]>400000: continue
    m=o.data
    V=[o.matrix_world@v.co for v in m.vertices]; P=[tuple(p.vertices) for p in m.polygons]
    if P: B[o.name]=BVHTree.FromPolygons(V,P)
res={}
for x in np.arange(X0,X1,0.5):
  for y in np.arange(Y0,Y1,1.0):
    best=None
    for n,b in B.items():
      r=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
      if r[0] is not None and (best is None or r[0].z>best[1]): best=(n,round(r[0].z,3),round(r[1].z,2))
    if best: res[f'{x:.1f},{y:.1f}']=best
json.dump(res,open('/workspace/nj-scenes/montclair-state/data/wx/probe2.json','w'))
print('DONE',len(res),flush=True)
