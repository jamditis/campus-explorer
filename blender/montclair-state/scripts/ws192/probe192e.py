import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
objs=[o for o in bpy.data.objects if o.type=='MESH' and len(o.data.polygons)>0]
cand=[]
for o in objs:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)>-309 and min(xs)<-298 and max(ys)>-241 and min(ys)<-234 and min(zs)<120 and max(zs)>116 and not o.hide_render and not o.name.startswith(('Context_skirt','BD_farfield','WS165_tree')): cand.append(o)
print('P192B cands',[o.name[:45] for o in cand])
T=[(o.name[:28],bvh(o)) for o in cand]
for o in cand: print('P192B obj',o.name,'hide_render',o.hide_render,'hide_vp',o.hide_viewport,'vis',o.visible_get() if hasattr(o,'visible_get') else '')
for y in [-234.2,-234.6,-235.0,-235.4,-235.8,-236.2,-236.6,-237.0]:
  row=[]
  for x in np.arange(-306.0,-303.4,0.25):
    hs=[(n,h[0].z) for n,t in T for h in [t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))] if h[0]]
    hs.sort(key=lambda a:-a[1])
    row.append('%.1f:%s%.2f'%(x,hs[0][0][:14] if hs else '-',hs[0][1]-118 if hs else 0) + ('/%s%.2f'%(hs[1][0][:14],hs[1][1]-118) if len(hs)>1 else ''))
  print('P192E y%.1f'%y,' '.join(row))
