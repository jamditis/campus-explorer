import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
S=bvh('Context_skirt_3DEP_ortho_4km'); A=bvh(next(o.name for o in bpy.data.objects if o.name.startswith('WS181_Lot36_asphalt_LiDAR2023int')))
for x in (-337,-335,-333,-331,-329):
    for y in (-233,-231,-229,-227):
        hs=S.ray_cast(Vector((x,y,160)),Vector((0,0,-1))); ha=A.ray_cast(Vector((x,y,160)),Vector((0,0,-1)))
        print('SKZ188',x,y,'skirt',round(hs[0].z,2) if hs[0] else None,'asph',round(ha[0].z,2) if ha[0] else None,flush=True)
