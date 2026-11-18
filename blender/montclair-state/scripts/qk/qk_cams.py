# qk cameras for the WIPs. REVERT=1 removes them.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
NAMES=['QK_CAM_oblique_NE_ccis_from_SE','QK_CAM_eye_NE_road_ends_from_west','QK_CAM_eye_ccis_east_bay','QK_CAM_closeup_NE_road_end']
for n in NAMES:
    o=bpy.data.objects.get(n)
    if o: cd=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(cd)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); bt=BVHTree.FromObject(bpy.data.objects['Terrain_LiDAR_DTM_1m'],dg); bs=BVHTree.FromObject(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],dg)
    bf=BVHTree.FromObject(bpy.data.objects['QJ_NE_seam_fill_UNVERIFIED'],dg)
    def g(x,y):
        for b in (bt,bf,bs):
            h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
            if h is not None: return h.z
    def cam(n,loc,tgt,lens):
        cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_end=6000; o=bpy.data.objects.new(n,cd); bpy.context.scene.collection.objects.link(o)
        o.location=loc; d=Vector(tgt)-Vector(loc); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); o['qk']=1; return o
    cam(NAMES[0],(290,95,g(290,95)+95),(160,205,g(160,205)),28)
    cam(NAMES[1],(198,215,g(198,215)+1.7),(245,190,g(245,190)+0.5),28)
    q=bpy.data.objects['QE_CAM_eye_ccis_east']; c=cam(NAMES[2],(0,0,0),(1,0,0),q.data.lens); c.matrix_world=q.matrix_world.copy(); [setattr(c.data,a,getattr(q.data,a)) for a in ('shift_x','shift_y','sensor_width','sensor_fit','clip_start','clip_end')]
    cam(NAMES[3],(233,215,g(233,215)+2.2),(222,205,g(222,205)),35)
    print('QK cams added')
