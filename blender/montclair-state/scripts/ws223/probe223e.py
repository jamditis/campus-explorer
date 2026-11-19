import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world
V=[M@v.co for v in L.data.vertices]; T=BVHTree.FromPolygons(V,[p.vertices[:] for p in L.data.polygons])
for x,y in ((-249.1,-53.2),(-249.0,-53.2),(-248.95,-53.2),(-249.0,-53.0),(-249.0,-53.4),(-249.2,-53.4),(-249.0,-52.9)):
    z=130; out=[]
    while True:
        h=T.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
        if not h[0]: break
        p=L.data.polygons[h[2]]; out.append('f%d z%.3f nz%.2f %s'%(h[2],h[0].z,h[1].z,list(p.vertices))); z=h[0].z-1e-4
    print('P223 (%.2f,%.2f) '%(x,y)+' | '.join(out))
