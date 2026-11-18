import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
lots=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and 'asphalt' in o.name and o.name.startswith(('WS7','WS8','WS9'))]
TR=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]) for o in lots]
def zat(x,y):
    b=None
    for T in TR:
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] and (b is None or h[0].z>b): b=h[0].z
    return b
t=np.array((0.969,-0.249));t/=np.linalg.norm(t);u=np.array((-t[1],t[0]));o0=np.array((-247.80,-69.47))
for nm in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km'):
    o=bpy.data.objects[nm]; mw=o.matrix_world
    for v in o.data.vertices:
        w=mw@v.co; q=np.array((w.x,w.y))-o0; s=q@t; d=q@u
        if 24<s<40 and -14<d<-1:
            za=zat(w.x,w.y)
            if za is not None and w.z>za-0.03: print('P197d',nm[:12],v.index,'s %.1f d %.1f xy %.2f %.2f z %.3f asph %.3f dz %+.3f'%(s,d,w.x,w.y,w.z,za,w.z-za),flush=True)
