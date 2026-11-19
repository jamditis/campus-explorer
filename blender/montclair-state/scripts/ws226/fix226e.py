# W53 part 2: after fix226a the eye views still showed a long dark ribbon a few metres over the east lawn. Cause (probe226l):
# fans of 0.2-0.5 m wide sliver triangles in the base Terrain_LiDAR_DTM_1m mesh, up to 284 m long, radiating from a few
# apex vertices (e.g. (216.4, 248.5, 122.9), ~12 m above the 3DEP ground there); where they are not hidden they stand as
# ribbons over the LiDAR patches. Fix: delete every base face that uses a fan apex (vertex with >= 20 faces of max edge
# > 20 m) AND is fully covered by the QG/QH/QI LiDAR patches (40 barycentric samples per face, all must hit a patch).
# The patches are the surface there; faces not fully covered are kept (no new holes). No vertex moved.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
P=[bpy.data.objects[n] for n in ('QG_north_strip_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QI_east_edge_LiDAR_terrain_patch')]
V=[];F=[]
for o in P:
    b=len(V); M=o.matrix_world; V+= [M@v.co for v in o.data.vertices]; F+=[[i+b for i in p.vertices] for p in o.data.polygons]
BP=BVHTree.FromPolygons(V,F)
co=[v.co for v in me.vertices]
def maxe(p):
    vs=[co[i] for i in p.vertices]; return max((vs[i]-vs[i-1]).length for i in range(len(vs)))
inc={}
for p in me.polygons:
    if maxe(p)>20:
        for i in p.vertices: inc[i]=inc.get(i,0)+1
apex=[i for i,c in inc.items() if c>=20]
print('F226E fan apexes',[(i,tuple(round(c,1) for c in co[i]),inc[i]) for i in apex],flush=True)
A=set(apex); dele=[]; kept=0
for p in me.polygons:
    if not A.intersection(p.vertices) or maxe(p)<=20: continue
    vs=[co[i] for i in p.vertices]
    tris=[(vs[0],vs[k],vs[k+1]) for k in range(1,len(vs)-1)]
    ok=True
    for a,b,c in tris:
        for i in range(8):
            for j in range(8-i):
                u=(i+0.33)/8.0; v=(j+0.33)/8.0
                if u+v>1: continue
                q=a+(b-a)*u+(c-a)*v
                if BP.ray_cast(Vector((q.x,q.y,400)),Vector((0,0,-1)))[0] is None: ok=False; break
            if not ok: break
        if not ok: break
    if ok: dele.append(p.index)
    else: kept+=1
print('F226E delete fan faces fully under patches',len(dele),'kept (not fully covered)',kept,flush=True)
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[bm.faces[i] for i in dele],context='FACES_ONLY'); bm.to_mesh(me); bm.free(); me.update()
