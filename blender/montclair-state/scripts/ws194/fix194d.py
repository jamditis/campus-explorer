# ws194 self-review fix: the AFTER close-up showed a small dark dent in the lawn ~0.5-1 m E of the ramp E edge (a coarse
# WS163_ground_patch vert pulled down by fix194 between higher neighbours). Two Laplacian passes on patch verts within
# 1.4 m E of the edge (y -237...-249), keeping the 1.5 cm drop below the asphalt for verts within 0.3 m of the edge.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
D=[o for o in bpy.data.objects if o.name.startswith('WS163_Lot3_aisle_S_drive')][0]; Md=D.matrix_world
DB=BVHTree.FromPolygons([Md@v.co for v in D.data.vertices],[p.vertices[:] for p in D.data.polygons])
En=lambda y: -305.45+0.0114*(y+236.0)
def ez(y):
    h=DB.ray_cast(Vector((En(y)-0.08,y,200)),Vector((0,0,-1))); return h[0].z if h[0] else None
L=[o for o in bpy.data.objects if o.name.startswith('WS163_ground_patch_W_of_WS110')][0]; ML=L.matrix_world; MLi=ML.inverted()
bm=bmesh.new(); bm.from_mesh(L.data); bm.verts.ensure_lookup_table()
P=[ML@v.co for v in bm.verts]
sel=[v.index for v in bm.verts if -249.0<P[v.index].y<-237.0 and 0.0<=P[v.index].x-En(P[v.index].y)<1.4]
for it in range(2):
    new={}
    for i in sel:
        ns=[e.other_vert(bm.verts[i]).index for e in bm.verts[i].link_edges]
        z=0.5*P[i].z+0.5*sum(P[n].z for n in ns)/len(ns)
        d=P[i].x-En(P[i].y); e=ez(P[i].y)
        if e is not None and d<0.3: z=min(z,e-0.015)
        new[i]=z
    for i,z in new.items(): P[i].z=z
for i in sel: bm.verts[i].co=MLi@P[i]
bm.to_mesh(L.data); L.data.update(); bm.free()
print('FIX194d smoothed',len(sel),flush=True)
