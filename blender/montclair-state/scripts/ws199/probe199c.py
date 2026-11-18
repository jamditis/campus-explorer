import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-240,-236,-81.6,-78.8
objs=[]
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('Context_skirt','BD_farfield','T_','el roof','Roof_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    me=o.evaluated_get(dg).to_mesh(); mw=o.matrix_world
    objs.append((o.name[:12],BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])))
print('P199 objs',[n for n,_ in objs])
for y in np.arange(Y0,Y1,0.2):
  row=[]
  for x in np.arange(X0,X1,0.4):
    hs=[]
    for n,T in objs:
      h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
      if h[0]: hs.append((h[0].z,n,h[1].z))
    hs.sort(reverse=True)
    row.append('%s%.3f/%.2f'%(hs[0][1][2:5],hs[0][0]-126,hs[0][2]) if hs else '-')
  print('P199 y%.1f '%y+' '.join(row),flush=True)
