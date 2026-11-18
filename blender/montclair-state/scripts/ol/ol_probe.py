import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
C=Vector((10.6,141.1))
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; dg=bpy.context.evaluated_depsgraph_get()
bt=bmesh.new(); bt.from_mesh(ter.evaluated_get(dg).to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world)
for e in bm.edges:
    if not e.is_boundary: continue
    a,b=e.verts; m=(a.co+b.co)/2; d=(m.xy-C).length
    if d>90: continue
    z=tz(m.x,m.y)
    if z is None: continue
    fl=m.z-z
    if fl>0.12: print('FLOAT d=%.1f at (%.1f,%.1f) float %.2f len %.1f %s'%(d,m.x,m.y,fl,(a.co-b.co).length,'IN' if d<=24 else 'OUT'))
