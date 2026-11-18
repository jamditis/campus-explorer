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
B={'R':bvh(['Morehead Hall roof (LiDAR)']),'E':bvh(['Morehead Hall eave soffit + fascia + rafter tails','Morehead Hall barrel tile eave course']),'S':bvh(['WS18_Morehead_W_eave_tile_skirt_UNVERIFIED']),'W':bvh(['Morehead Hall walls'])}
y=-62.0
while y>=-75.0:
    row=''
    x=-46.0
    while x<=-30.0:
        c='.'
        for k in ('S','R','E','W'):
            h,_,_,_=B[k].ray_cast(Vector((x,y,160)),Vector((0,0,-1)),40)
            if h and h.z>143.0: c=k; break
        row+=c; x+=0.5
    print('G %6.1f %s'%(y,row)); y-=0.5
