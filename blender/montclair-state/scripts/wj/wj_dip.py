import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ng=bpy.data.node_groups['WJ_skirt_under_south_gully']
for n in ng.nodes:
    if n.type=='MATH' and n.operation=='SUBTRACT' and not n.inputs[1].is_linked and abs(n.inputs[1].default_value-0.08)<1e-6:
        n.inputs[1].default_value=0.30; print('DIP set 0.30')
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
bw=bvh('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED');be=bvh('WJ_south_gully_LiDAR_patch_ext_UNVERIFIED');bs=bvh('Context_skirt_3DEP_ortho_4km')
cnt=0;mx=0;where=[]
for y in np.arange(292.25,336,0.5):
    for x in np.arange(182.25,258,0.5):
        ps=[h[0].z for h in (bw.ray_cast(Vector((x,y,400)),Vector((0,0,-1))),be.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))) if h[0] is not None]
        s=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if ps and s is not None and s.z>max(ps)+0.03: cnt+=1; mx=max(mx,s.z-max(ps)); where.append((x,y))
print('RESID',cnt,round(mx,2),where[:10])
bpy.ops.wm.save_mainfile()
