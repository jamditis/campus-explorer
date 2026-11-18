import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
B={n:BVHTree.FromObject(bpy.data.objects[n],dg) for n in ('Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','Footpaths_OSM')}
for y in (183.0,187.0,190.0,194.7):
    row=[]
    for x in [214+0.5*i for i in range(18)]:
        r=[]
        for n,b in B.items():
            h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; r.append('-' if h is None else '%.2f'%h.z)
        row.append((x,r))
    print('y',y); [print('  ',x,r) for x,r in row]
