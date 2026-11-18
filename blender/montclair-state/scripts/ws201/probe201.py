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
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=np.array(o.matrix_world)
    nv=len(me.vertices); co=np.empty(nv*3,np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)@mw[:3,:3].T+mw[:3,3]
    me.loop_triangles.foreach_get if False else None
    me.calc_loop_triangles(); nt=len(me.loop_triangles); tr=np.empty(nt*3,np.int32); me.loop_triangles.foreach_get('vertices',tr); tr=tr.reshape(-1,3)
    oe.to_mesh_clear()
    if nt==0: continue
    c=co[tr]; m=(c[:,:,0].max(1)>X0-1)&(c[:,:,0].min(1)<X1+1)&(c[:,:,1].max(1)>Y0-1)&(c[:,:,1].min(1)<Y1+1)
    tr=tr[m]
    if len(tr)==0: continue
    u,inv=np.unique(tr,return_inverse=True)
    objs.append((o.name,BVHTree.FromPolygons([Vector(p) for p in co[u]],inv.reshape(-1,3).tolist())))
    del co,c
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
