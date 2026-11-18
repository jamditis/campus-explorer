import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
X0,X1,Y0,Y1=-262,-250,-58,-44
with bpy.data.libraries.load(F) as (a,b):
    b.objects=list(a.objects)
T=[]
for o in b.objects:
    if not o or o.type!='MESH' or o.name.startswith(('Terrain','Context')): continue
    me=o.data
    if len(me.vertices)>400000 or not len(me.polygons): continue
    V=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',V); V=V.reshape(-1,3)
    M=np.array(o.matrix_world); W=V@M[:3,:3].T+M[:3,3]
    sel=(W[:,0]>X0)&(W[:,0]<X1)&(W[:,1]>Y0)&(W[:,1]<Y1)&(W[:,2]<128)
    if sel.sum()<1: continue
    T.append((o.name[:44],BVHTree.FromPolygons([Vector(w) for w in W],[p.vertices[:] for p in me.polygons]),[m.name[:18] for m in me.materials if m][:1]))
print('P216 objs',[t[0] for t in T])
for y in [-49+(-0.5*i) for i in range(15)]:
    for x in [-260+0.5*i for i in range(17)]:
        H=[]
        for n,t,m in T:
            h=t.ray_cast(Vector((x,y,128)),Vector((0,0,-1)),10)
            if h[0] is not None: H.append((round(h[0].z,3),n[:30]))
        H.sort(reverse=True)
        print('P216',x,y,H[:3])
