# ws190: objects + top-surface layering in the Lot 3 S ramp E-view foreground (modifiers off, no skirt)
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-318.0,-300.0,-247.0,-231.0
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith('Context_skirt'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if len(o.data.vertices)>2_000_000: print('BIG',o.name,len(o.data.vertices)); continue
    vis=not o.hide_render and o.visible_get() if o.name in bpy.context.view_layer.objects else False
    n=len(o.data.vertices); co=np.empty(n*3,dtype=np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); w=co@M[:3,:3].T+M[:3,3]
    k=(w[:,0]>X0)&(w[:,0]<X1)&(w[:,1]>Y0)&(w[:,1]<Y1)
    mat=o.active_material.name if o.active_material else '-'
    print('OBJ190',o.name,'vis',vis,'nv',n,'inreg',int(k.sum()),(f'z={w[k,2].min():.2f}..{w[k,2].max():.2f}' if k.any() else ''),'mat',mat,'mods',[m.type for m in o.modifiers],flush=True)
    if vis and k.any():
        me=o.data; vs=[o.matrix_world@v.co for v in me.vertices]; fs=[p.vertices[:] for p in me.polygons]
        objs.append((o.name,BVHTree.FromPolygons(vs,fs)))
print('GRID190 x y : hits(name z)')
for x in np.arange(X0,X1+0.01,0.5):
  for y in np.arange(Y0,Y1+0.01,0.5):
    hits=[]
    for nm,t in objs:
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0]: hits.append((round(h[0].z,3),nm,round(h[1].z,2)))
    hits.sort(reverse=True)
    print('G',round(x,2),round(y,2),hits[:4])
