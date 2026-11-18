import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
W=bvh(O['WV_stone_west_LiDAR_patch_UNVERIFIED']); S=bvh(O['QS_footway_546643369_UNVERIFIED'])
s=O['QS_footway_546643369_UNVERIFIED']; t=O['QT_soil_edge_546643369_UNVERIFIED']
print('slab thick? verts z range', min(v.co.z for v in s.data.vertices), max(v.co.z for v in s.data.vertices), 'faces',len(s.data.polygons), 'nz<0',sum(1 for p in s.data.polygons if p.normal.z<-.5),'side',sum(1 for p in s.data.polygons if abs(p.normal.z)<.5))
def wz(x,y):
    h=W.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return None if h[0] is None else h[0].z
rows=[]
for p in t.data.polygons:
    vs=[t.matrix_world@t.data.vertices[i].co for i in p.vertices]
    d=[S.find_nearest(v)[3] for v in vs]
    idx=np.argsort(d); inn=[vs[i] for i in idx[:2]]; out=[vs[i] for i in idx[2:]]
    gi=[wz(v.x,v.y) for v in inn]; go=[wz(v.x,v.y) for v in out]
    if None in gi+go: continue
    rows.append((np.mean([v.y for v in vs]),np.mean([a.z-g for a,g in zip(inn,gi)])*100,np.mean([a.z-g for a,g in zip(out,go)])*100,np.mean(sorted(d)[:2]),np.mean(sorted(d)[2:])))
rows=np.array(rows); print('quads over WV',len(rows))
print('inner dz vs WV pct',np.percentile(rows[:,1],[0,25,50,75,100]).round(1))
print('outer dz vs WV pct',np.percentile(rows[:,2],[0,25,50,75,100]).round(1))
print('inner dist',rows[:,3].mean().round(3),'outer dist',rows[:,4].mean().round(3))
# slab top vs WV at slab-edge: verts of slab on boundary
