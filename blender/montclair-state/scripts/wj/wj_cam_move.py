import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
bs=[]
for n in ('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WJ_south_gully_LiDAR_patch_ext_UNVERIFIED','Context_skirt_3DEP_ortho_4km'):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];bs.append(BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]));e.to_mesh_clear()
def gz(x,y): return max(h[0].z for h in [b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for b in bs] if h[0] is not None)
T=[]
for o in bpy.data.objects:
    if o.name.startswith(('TL_tree_','WJ_gully_tree_')) and o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; r=max(max(v.x for v in bb)-min(v.x for v in bb),max(v.y for v in bb)-min(v.y for v in bb))/2
        T.append((o.matrix_world.translation.x,o.matrix_world.translation.y,r))
best=None
for x in range(256,290):
    for y in range(292,322):
        # clearance relative to crown radius
        c=min(math.hypot(x-tx,y-ty)-tr*0.6 for tx,ty,tr in T)
        if best is None or c>best[0]: best=(c,x,y)
print('BEST',best)
c,x,y=best
cam=bpy.data.objects['WJ_CAM_eye_south_gully_from_E']; z=gz(x,y)+1.7
tgt=Vector((215,312,gz(215,312)+4)); cam.location=(x,y,z); d=tgt-Vector((x,y,z))
cam.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2)
print('CAMNEW',x,y,round(z,2))
bpy.ops.wm.save_mainfile()
