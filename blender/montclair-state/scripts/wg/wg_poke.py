import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh()
    t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return t
g=lambda t,x,y:(lambda h:h[0].z if h[0] else None)(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))))
bp=bvh(bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']); bs=bvh(bpy.data.objects['Context_skirt_3DEP_ortho_4km'])
out=[]
for x in np.arange(209,216.2,0.25):
    for y in np.arange(399,412,0.25):
        if 213.85<=x<=216.15 and 402.85<=y<=408.35: continue
        a=g(bp,x,y); b=g(bs,x,y)
        if a and b and b-a>0.02: out.append((round(b-a,3),x,y))
out.sort(reverse=True); print('POKES',len(out),out[:12])
