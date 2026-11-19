import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(n): return [o for o in bpy.data.objects if o.name.startswith(n)][0]
def tree(o):
    M=o.matrix_world; R=M.to_3x3()
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons if (R@p.normal).z>0.3])
A=ob('WS72_Kasser_SW_RHD_core_sidewalk_landing'); C=ob('WS71_Kasser_S_sidewalk')
TA,TC=tree(A),tree(C)
for o,T,lab in ((A,TC,'WS72 v'),(C,TA,'WS71 v')):
    M=o.matrix_world
    for v in o.data.vertices:
        w=M@v.co
        if abs(w.x+243.0)<0.06 and w.z>125.5:
            h=T.ray_cast(Vector((w.x+(0.03 if lab[3]=='2' else -0.03),w.y,130)),Vector((0,0,-1)))
            print('P224 %s%d (%.3f,%.3f,%.3f) other side 3cm %s'%(lab,v.index,w.x,w.y,w.z,'%.3f'%h[0].z if h[0] else '-'))
