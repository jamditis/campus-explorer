import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G={n:bvh(O[n]) for n in ['QW_DTM_north_edge_ramp_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WT_richardson_west_LiDAR_patch_UNVERIFIED','WU_richardson_reid_LiDAR_patch_UNVERIFIED']}
for nm,B in [('w428',(28,52,250,325)),('e436',(66,100,290,310))]:
    zf=0;holes=0;n=0
    for x in np.arange(B[0],B[1],0.2):
        for y in np.arange(B[2],B[3],0.2):
            zs=sorted([h[0].z for b in G.values() for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None],reverse=True)
            n+=1
            if not zs: holes+=1
            elif len(zs)>1 and zs[0]-zs[1]<0.004: zf+=1
    print('ZF',nm,n,'zfight',zf,'holes',holes,flush=True)
