import bpy,bmesh,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    bm=bmesh.new(); dg=bpy.context.evaluated_depsgraph_get(); oe=o.evaluated_get(dg); m=oe.to_mesh(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
O=bpy.data.objects
names=['Context_skirt_3DEP_ortho_4km','Terrain_LiDAR_DTM_1m','WS68_RHD_ground_northDTM','eu_rhd_ground_slab']
T={n:bvh(O[n]) for n in names if n in O}
print('S69 have',list(T))
def hit(t,x,y):
    h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)));return h[0].z if h[0] else None
out=[]
for x in range(-262,-234,2):
  for y in range(-30,14,2):
    r={n:hit(t,x,y) for n,t in T.items()}
    sk=r.get('Context_skirt_3DEP_ortho_4km'); others=[v for k,v in r.items() if k!='Context_skirt_3DEP_ortho_4km' and v is not None]
    if sk is not None and others and sk>min(others)-0.05: out.append((x,y,{k:(round(v,2) if v else None) for k,v in r.items()}))
print('S69 skirt-over count',len(out))
for o in out[:40]: print('S69',o)
ret=O.get('eu_rhd_north_retaining_wall')
if ret:
    import statistics
    zs=[(ret.matrix_world@v.co) for v in ret.data.vertices]
    print('S69 retwall bbox',min(v.x for v in zs),max(v.x for v in zs),min(v.y for v in zs),max(v.y for v in zs),min(v.z for v in zs),max(v.z for v in zs), 'loc',tuple(ret.location),'parent',ret.parent.name if ret.parent else None)
