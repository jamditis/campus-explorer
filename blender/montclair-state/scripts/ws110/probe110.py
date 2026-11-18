import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
pts=[(-220,-281),(-200,-286),(-230,-262),(-210,-262),(-180,-293)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-235 or min(v.x for v in bb)>-175 or max(v.y for v in bb)<-295 or min(v.y for v in bb)>-255: continue
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free()
    hs=[]
    for p in pts:
        h=t.ray_cast(Vector((p[0],p[1],300)),Vector((0,0,-1)))[0]; hs.append(round(h.z,2) if h else None)
    if any(hs): print('PR110',o.name[:60],hs,[m.type for m in o.modifiers][:4])
