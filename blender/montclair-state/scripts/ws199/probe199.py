import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=[float(a) for a in os.environ.get('BOX','-248,-226,-87,-73').split(',')]
ST=float(os.environ.get('STEP','0.2'))
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if o.name.startswith(('Context_skirt','BD_farfield','T_','el roof','Roof_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    V=[mw@v.co for v in me.vertices]; F=[tuple(p.vertices) for p in me.polygons]
    if not F: continue
    objs.append((o.name,BVHTree.FromPolygons(V,F),len(V),[m.name for m in o.modifiers]))
print('P199 objs',[(n,nv,len(m)) for n,_,nv,m in objs],flush=True)
xs=np.arange(X0,X1,ST); ys=np.arange(Y0,Y1,ST)
Z=np.full((len(xs),len(ys)),np.nan); O=np.full((len(xs),len(ys)),-1)
for i,x in enumerate(xs):
  for j,y in enumerate(ys):
    best=None
    for k,(n,T,_,_) in enumerate(objs):
      h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
      if h[0] and (best is None or h[0].z>best[0]): best=(h[0].z,k,h[1].z)
    if best: Z[i,j]=best[0]; O[i,j]=best[1]
np.savez(os.environ['OUT'],Z=Z,O=O,xs=xs,ys=ys,names=np.array([o[0] for o in objs]))
out=[]
for i in range(len(xs)-1):
  for j in range(len(ys)-1):
    for di,dj in ((1,0),(0,1)):
      d=Z[i+di,j+dj]-Z[i,j]
      if abs(d)>0.03: out.append((round(float(abs(d)),3),round(float(xs[i]),1),round(float(ys[j]),2),objs[O[i,j]][0][:30],objs[O[i+di,j+dj]][0][:30]))
out.sort(reverse=True); print('P199 steps',len(out),flush=True)
for r in out[:60]: print('P199',r,flush=True)
