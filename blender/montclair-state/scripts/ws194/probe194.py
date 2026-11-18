import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=[o for o in bpy.data.objects if o.name.startswith('WS163_Lot3_aisle_S_drive')][0]
M=D.matrix_world; me=D.data
W=np.array([tuple(M@v.co) for v in me.vertices])
bm=bmesh.new(); bm.from_mesh(me)
bidx=sorted({v.index for e in bm.edges if e.is_boundary for v in e.verts}); bm.free()
B=W[bidx]
E=B[(B[:,0]>-306.6)&(B[:,0]<-302.5)]; E=E[np.argsort(-E[:,1])]
# candidate neighbours
X0,X1,Y0,Y1=-308,-298,-254,-232
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o==D or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if len(o.data.polygons)>400000: print('SKIPBIG',o.name); continue
    Mo=o.matrix_world
    objs.append((o.name,BVHTree.FromPolygons([Mo@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
print('NEIGH',[n for n,_ in objs])
def hits(x,y):
    r=[]
    for n,t in objs:
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0]: r.append((n[:28],round(h[0].z,3)))
    return sorted(r,key=lambda a:-a[1])[:3]
for x,y,z in E:
    print('E %.2f %.2f %.3f'%(x,y,z),'| +0.15',hits(x+0.15,y),'| +0.6',hits(x+0.6,y))
