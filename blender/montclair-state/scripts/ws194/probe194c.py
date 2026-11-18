import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=[o for o in bpy.data.objects if o.name.startswith('WS163_Lot3_aisle_S_drive')][0]
M=D.matrix_world; me=D.data
W=np.array([tuple(M@v.co) for v in me.vertices])
bm=bmesh.new(); bm.from_mesh(me)
bidx=sorted({v.index for e in bm.edges if e.is_boundary for v in e.verts}); bm.free()
B=W[bidx]; Nn=B[B[:,1]>-235.4]; Nn=Nn[np.argsort(Nn[:,0])]
X0,X1,Y0,Y1=-314,-300,-237,-230
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o==D or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if len(o.data.polygons)>400000 or o.name.startswith('Context'): continue
    Mo=o.matrix_world
    objs.append((o.name,BVHTree.FromPolygons([Mo@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
print('NEIGH',[n for n,_ in objs])
def hits(x,y):
    r=[]
    for n,t in objs:
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0]: r.append((n[:26],round(h[0].z,3)))
    return sorted(r,key=lambda a:-a[1])[:3]
for x,y,z in Nn: print('N %.2f %.2f %.3f'%(x,y,z),'| y+0.15',hits(x,y+0.15),'| y+0.5',hits(x,y+0.5))
