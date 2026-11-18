import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; e=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; b=len(V)
        V.extend(M@v.co for v in e.vertices); F.extend([b+i for i in p.vertices] for p in e.polygons); o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(V,F,all_triangles=False)
BC=bvh(['Morehead Hall barrel tile eave course']); FS=bvh(['Morehead Hall eave soffit + fascia + rafter tails']); SK=bvh(['WS18_Morehead_W_eave_tile_skirt_UNVERIFIED'])
OUT=Vector((-0.97,0.24,0)).normalized(); AL=Vector((0.24,0.97,0)).normalized(); P0=Vector((-40.03,-56.5,0))
for a in (-10.0,-10.1,-10.25,0.0,0.12,8.0):
    base=P0+AL*a; s=[]
    t=0.0
    while t<1.3:
        o=base+OUT*t
        def z(B):
            h,_,_,_=B.ray_cast(Vector((o.x,o.y,160)),Vector((0,0,-1)),40); return '%.2f'%h.z if h else '-'
        s.append('%.2f B%s F%s S%s'%(t,z(BC),z(FS),z(SK))); t+=0.1
    print('P',a,' | '.join(s))
