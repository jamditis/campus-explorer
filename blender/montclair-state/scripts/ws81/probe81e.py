import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); oe.to_mesh_clear(); return t
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m']); G=bvh([o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]); D=bvh(bpy.data.objects['WS78_lot_pocket_DTM_target'])
A=bvh(bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt'])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; return h.z if h else None
f=lambda z:'  .   ' if z is None else '%6.2f'%z
for y in range(-110,-144,-2):
    print('ROW',y,' | '.join('%s/%s/%s/%s'%(f(hz(T,x,y)),f(hz(G,x,y)),f(hz(A,x,y)),f(hz(D,x,y))) for x in range(-256,-224,3)),flush=True)
