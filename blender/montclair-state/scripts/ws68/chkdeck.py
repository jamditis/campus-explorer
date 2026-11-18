import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
P=bvh([o for o in bpy.data.objects if o.name.startswith('WS68_RHD')][0]); S=bvh(bpy.data.objects['eu_rhd_ground_slab'])
bad=0;n=0;mx=0
for y in range(-43,27,2):
    for x in range(-333,-249,2):
        s=S.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
        # first hit from the slab level downward excluding: patch from above
        p=P.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
        if s and p:
            n+=1
            if p.z>s.z-0.05: bad+=1; mx=max(mx,p.z-s.z)
print('CD68 inside slab',n,'patch above slab',bad,'max',round(mx,2))
