# ws197c: light wedge at the E end of row B (cut view from the W aisle) = Terrain_LiDAR_DTM_1m lawn faces poking 2-8 cm
# through the WS94 slit filler / WS75-WS76 seam at y~-80.1, x -228 (probe197e ray hits). Push terrain verts under paving to 7 cm below.
# through the WS94 slit filler / WS75-WS76 seam at y~-80.1, x -228 (probe197e ray hits). Push terrain verts under paving to 7 cm below.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
L=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and 'asphalt' in o.name and o.name.startswith(('WS7','WS8','WS9'))]
TRb=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]) for o in L]
def zatb(x,y):
    b=None
    for T in TRb:
        h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] and (b is None or h[0].z>b): b=h[0].z
    return b
Tn=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=Tn.matrix_world; mi=mw.inverted(); fixed=[]
for v in Tn.data.vertices:
    w=mw@v.co
    if -232<w.x<-223 and -82.5<w.y<-77.5:
        za=zatb(w.x,w.y)
        if za is not None and w.z>za-0.05: fixed.append((v.index,round(w.z-za,3))); w.z=za-0.07; v.co=mi@w
Tn.data.update(); print('F197c terrain lowered',fixed,flush=True)
