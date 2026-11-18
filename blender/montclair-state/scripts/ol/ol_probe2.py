import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
C=Vector((10.6,141.1))
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get()
bt=bmesh.new(); bt.from_mesh(ter.evaluated_get(dg).to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world)
print('verts',len(bm.verts),'faces',len(bm.faces))
be=[e for e in bm.edges if e.is_boundary]; seen=set(); loops=[]
for e in be:
    if e.index in seen: continue
    loop=[]; cur=e; v=e.verts[0]
    while cur and cur.index not in seen:
        seen.add(cur.index); loop.append(v); v=cur.other_vert(v)
        nxt=[x for x in v.link_edges if x.is_boundary and x.index not in seen]; cur=nxt[0] if nxt else None
    loops.append(loop)
for L in loops:
    xs=[v.co.x for v in L]; ys=[v.co.y for v in L]; c=Vector((sum(xs)/len(xs),sum(ys)/len(ys)))
    if (c-C).length>40: continue
    a=0.5*abs(sum(L[i].co.x*L[(i+1)%len(L)].co.y-L[(i+1)%len(L)].co.x*L[i].co.y for i in range(len(L))))
    fl=[v.co.z-(tz(v.co.x,v.co.y) or v.co.z) for v in L]
    print('LOOP n=%d c=(%.1f,%.1f) d=%.1f area=%.1f float max %.2f min %.2f z %.2f'%(len(L),c.x,c.y,(c-C).length,a,max(fl),min(fl),sum(v.co.z for v in L)/len(L)))
