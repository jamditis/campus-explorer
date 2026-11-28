# ws272 probe (no save): wider WS68 base grid + the ground objects S of its S edge (apron / WS86 target) along y -135...-137.
import bpy, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
A=[o for o in OB if o.name.startswith('WS68_RHD_ground_northDTM')][0]
V=np.array([tuple(v.co) for v in A.data.vertices])
sel=(V[:,0]>-281)&(V[:,0]<-247)&(V[:,1]>-136)&(V[:,1]<-117); S=V[sel]
xs=np.arange(-280,-248,1.0)
print('P272B x   ',' '.join(f'{x:6.0f}' for x in xs))
for y in np.arange(-118,-136,-1.0):
    r=[]
    for x in xs:
        m=S[(np.abs(S[:,0]-x)<0.01)&(np.abs(S[:,1]-y)<0.01)]
        r.append(f'{m[0,2]:6.1f}' if len(m) else '     -')
    print(f'P272B {y:5.0f}',' '.join(r),flush=True)
for o in OB:
    if o.type=='MESH' and any(s in o.name for s in ('WS60_terrain_edge_apron','WS86_grandstand_DTM_target')):
        me=o.data; mw=o.matrix_world
        T=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
        for y in (-135.0,-135.5,-136.5,-138.5):
            r=[]
            for x in xs:
                h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); r.append(f'{h[0].z:6.1f}' if h[0] else '     -')
            print(f'P272B {o.name[:12]} {y}',' '.join(r),flush=True)
os._exit(0)
