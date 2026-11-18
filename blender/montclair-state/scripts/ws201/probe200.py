import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=[float(a) for a in os.environ.get('BOX','-342,-310,-246,-220').split(',')]
ST=float(os.environ.get('STEP','0.25'))
objs=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if 'tree' in o.name.lower() and os.environ.get('NOTREE'): continue
    if o.name.startswith(('Context_skirt','BD_farfield','T_','el roof','Roof_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    V=[mw@v.co for v in me.vertices]; F=[tuple(p.vertices) for p in me.polygons]
    if not F: continue
    objs.append((o.name,BVHTree.FromPolygons(V,F)))
xs=np.arange(X0,X1,ST); ys=np.arange(Y0,Y1,ST)
Z=np.full((len(xs),len(ys)),np.nan); O=np.full((len(xs),len(ys)),-1); Z2=np.full((len(xs),len(ys)),np.nan)
for i,x in enumerate(xs):
  for j,y in enumerate(ys):
    hs=[]
    for k,(n,T) in enumerate(objs):
      h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
      if h[0]: hs.append((h[0].z,k))
    hs.sort(reverse=True)
    if hs: Z[i,j]=hs[0][0]; O[i,j]=hs[0][1]; Z2[i,j]=hs[1][0] if len(hs)>1 else np.nan
names=[o[0] for o in objs]
np.savez(os.environ['OUT'],Z=Z,O=O,Z2=Z2,xs=xs,ys=ys,names=np.array(names))
print('P200 saved',len(names),flush=True)
for n in names:
    if n.startswith('WS169c'):
        o=bpy.data.objects[n]; mw=o.matrix_world
        P=np.array([tuple(mw@v.co) for v in o.data.vertices]); np.save(os.environ['OUT']+'_ws169c.npy',P)
        print('P200 WS169c verts',len(P),P.min(0),P.max(0),[m.name for m in o.modifiers],flush=True)
