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
EAVE=bvh(['Morehead Hall eave soffit + fascia + rafter tails','Morehead Hall barrel tile eave course'])
ROOF=bvh(['Morehead Hall roof (LiDAR)'])
SK=bvh(['WS18_Morehead_W_eave_tile_skirt_UNVERIFIED'])
OUT=Vector((-0.97,0.24,0)).normalized(); AL=Vector((0.24,0.97,0)).normalized(); P0=Vector((-40.03,-56.5,0))
a=-19.0
while a<=-9.0:
    base=P0+AL*a; s=[]
    for t in (-1.0,-0.6,-0.3,0.0,0.3,0.6,0.9,1.2):
        o=base+OUT*t
        r,_,_,_=ROOF.ray_cast(Vector((o.x,o.y,160)),Vector((0,0,-1)),30)
        e,_,_,_=EAVE.ray_cast(Vector((o.x,o.y,160)),Vector((0,0,-1)),30)
        k,_,_,_=SK.ray_cast(Vector((o.x,o.y,160)),Vector((0,0,-1)),30)
        s.append('%.1f:R%s E%s S%s'%(t,round(r.z,2) if r else '-',round(e.z,2) if e else '-',round(k.z,2) if k else '-'))
    print('A',a,[round(v,2) for v in base.xy],' | '.join(s)); a+=0.5
