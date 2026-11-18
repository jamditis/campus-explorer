import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
bs=[]
for n in ('WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','WJ_south_gully_LiDAR_patch_ext_UNVERIFIED','Context_skirt_3DEP_ortho_4km'):
    o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];bs.append(BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]));e.to_mesh_clear()
def gz(x,y): return max(h[0].z for h in [b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for b in bs] if h[0] is not None)
col=bpy.data.collections.get('WJ_south_gully_UNVERIFIED') or bpy.data.collections.new('WJ_south_gully_UNVERIFIED')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
E=bpy.data.objects['WJ_south_gully_LiDAR_patch_ext_UNVERIFIED']
def mk(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name);cd.lens=lens;cd.clip_end=30000
    o=bpy.data.objects.new(name,cd);col.objects.link(o);o.location=loc;d=Vector(tgt)-Vector(loc)
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2);o['wj_obj']=1
    print('CAM',name,[round(c,2) for c in loc],[round(c,2) for c in tgt])
x,y=252,310; z=gz(x,y)+1.7
mk('WJ_CAM_eye_south_gully_from_E',(x,y,z),(205,319,gz(205,319)+3),24)
mk('WJ_CAM_closeup_south_gully_oblique_SE',(300,255,185),(214,314,118),35)
bpy.ops.wm.save_mainfile()
