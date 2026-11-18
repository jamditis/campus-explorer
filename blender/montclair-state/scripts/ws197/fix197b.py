# ws197b: Terrain_LiDAR_DTM_1m vertex 114867 at (-224.50,-76.50) stood +0.30 m above the WS76 accessible-lot asphalt
# (east end of the lot between the two rows, beside row A stall 8 / the aisle) -> a light grass pyramid poking through the paving.
# Lower it to 5 cm under the top-most asphalt (same rule as earlier terrain poke-up fixes). Only vertices with dz>+0.1 in the box.
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
    if -232<w.x<-212 and -92<w.y<-70:
        za=zatb(w.x,w.y)
        if za is not None and w.z>za+0.1: fixed.append((v.index,round(w.z-za,3))); w.z=za-0.05; v.co=mi@w
Tn.data.update(); print('F197b terrain lowered',fixed,flush=True)
