# ws51: seat LiDAR terrain verts under Footpaths_OSM / Roads_OSM wherever terrain pokes through (corridor-wide). Idempotent.
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    ob=bpy.data.objects[n]; bm=bmesh.new(); bm.from_mesh(ob.evaluated_get(dg).to_mesh()); bm.transform(ob.matrix_world); return BVHTree.FromBMesh(bm)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; mi=mw.inverted()
P=[tree(n) for n in ('Footpaths_OSM','Roads_OSM') if n in bpy.data.objects]
n=0; mx=0
for v in t.data.vertices:
    w=mw@v.co
    if not (-200<w.x<140 and -130<w.y<130): continue
    best=None
    for b in P:
        for dx,dy in ((0,0),(0.5,0),(-0.5,0),(0,0.5),(0,-0.5)):
            r=b.ray_cast(Vector((w.x+dx,w.y+dy,w.z+3)),Vector((0,0,-1)),6)
            if r[0]: z=r[0].z-0.04; best=z if best is None else min(best,z)
    if best is not None and w.z>best and w.z-best<0.6:
        mx=max(mx,w.z-best); w.z=best; v.co=mi@w; n+=1
t.data.update(); print('S51 seated',n,'max',round(mx,2))
