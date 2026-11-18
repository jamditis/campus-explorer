import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); T={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('Context_ground_beyond','WS165_tree')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-322 or min(v.x for v in bb)>-306 or max(v.y for v in bb)<-244 or min(v.y for v in bb)>-226: continue
    bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); T[o.name]=BVHTree.FromBMesh(bm); bm.free()
def hits(x,y):
    r=[]
    for n,t in T.items():
        z=200.0
        while True:
            h=t.ray_cast(Vector((x,y,z)),Vector((0,0,-1)),200)
            if h[0] is None: break
            r.append((round(h[0].z,2),n[:22])); z=h[0].z-0.002
    return sorted(r,reverse=True)[:4]
for y in (-228.0,-229.0,-230.0,-231.0,-232.0):
    for x in [-317+0.5*k for k in range(14)]:
        print('PB',(round(x,2),y),hits(x,y),flush=True)
