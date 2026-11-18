import bpy, numpy as np
from mathutils import Vector
img=bpy.data.images['WJ_verge_mask']; W,H=img.size; print('SZ',W,H,img.packed_file is not None, img.source)
px=np.array(img.pixels[:]).reshape(H,W,4); print('SUM',px[...,0].sum(), px[...,0].max(), (px[...,0]>0.5).sum()*0.01)
for x,y in [(142.5,292.9),(143.2,295.7),(135,275),(130,265)]:
    i=int((x-116)/0.1); j=int((y-246)/0.1); print('PX',x,y,px[j,i,:2])
O=bpy.data.objects
from mathutils.bvhtree import BVHTree
def flat(n):
    o=O[n]; m=o.matrix_world
    return BVHTree.FromPolygons([Vector(((m@v.co).x,(m@v.co).y,0)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
for n in ['QS_footway_546643369_UNVERIFIED','QT_soil_edge_546643369_UNVERIFIED','QS_service_546643370_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','QW_service_546643370_ext_UNVERIFIED']:
    b=flat(n)
    for x,y in [(142.5,292.9),(135,275)]:
        r=b.find_nearest(Vector((x,y,0))); print('NN',n[:22],x,y, r[0] and (round(r[0].x,2),round(r[0].y,2)), r[3] and round(r[3],2))
