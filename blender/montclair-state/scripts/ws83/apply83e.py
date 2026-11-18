import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LN=bpy.data.objects['WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges']
b=bmesh.new(); b.from_mesh(LN.data); b.transform(LN.matrix_world); LB=BVHTree.FromBMesh(b); b.free()
o=bpy.data.objects['WS83_lane_gutter_skin_asphalt_UNVERIFIED']; n=0; dz=[]
ymin=min(v.co.y for v in o.data.vertices)
for v in o.data.vertices:
    h=LB.ray_cast(Vector((v.co.x,v.co.y,300)),Vector((0,0,-1)))[0]
    if h:
        nz=h.z+0.003; dz.append(v.co.z-nz); v.co.z=nz; n+=1
    if v.co.y<ymin+0.01: v.co.z-=0.006   # tuck the south edge row under the lane
o.data.update()
print('WS83e reseated',n,'of',len(o.data.vertices),'max drop %.3f'%max(dz),flush=True)
bpy.ops.wm.save_mainfile(); print('WS83e SAVED',flush=True)
