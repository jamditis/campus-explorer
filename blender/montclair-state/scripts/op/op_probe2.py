import bpy, bmesh, statistics
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def tree(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); b=bmesh.new(); b.from_mesh(e.to_mesh()); b.transform(o.matrix_world); return BVHTree.FromBMesh(b)
tt=tree('Terrain_LiDAR_DTM_1m')
others={n:tree(n) for n in ('MID_streets_inner_20261015aj','MID_streets_20261015ae')}
for n in others: print(n,[m.name for m in bpy.data.objects[n].modifiers], bpy.data.objects[n].data.materials[:] and [m.name for m in bpy.data.objects[n].data.materials if m])
rd=bpy.data.objects['Roads_OSM']; mw=rd.matrix_world
stats={n:[] for n in others}; cover=0; tot=0
for i,v in enumerate(rd.data.vertices):
    p=mw@v.co
    if p.y<0 or i%3: continue
    h=tt.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
    if not h[0]: continue
    tot+=1
    for n,t in others.items():
        g=t.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
        if g[0]: stats[n].append(round(g[0].z-h[0].z,2))
print('north road verts sampled',tot)
for n,l in stats.items():
    if l: print(n,'hits',len(l),'med',statistics.median(l),'min',min(l),'max',max(l), 'within0.3',sum(1 for x in l if abs(x)<0.3))
    else: print(n,'no hits')
