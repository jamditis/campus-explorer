# qj cameras for the NE seam WIPs. REVERT=1 removes them.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
NAMES=['QJ_CAM_oblique_NE_seam_from_SE','QJ_CAM_eye_NE_seam_from_east','QJ_CAM_eye_NE_seam_from_west','QJ_CAM_closeup_NE_seam']
for n in NAMES:
    o=bpy.data.objects.get(n)
    if o: cd=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(cd)
if not REV:
    dg=bpy.context.evaluated_depsgraph_get(); bt=BVHTree.FromObject(bpy.data.objects['Terrain_LiDAR_DTM_1m'],dg); bs=BVHTree.FromObject(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],dg)
    def g(x,y):
        h=bt.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] or bs.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; return h.z
    def cam(n,loc,tgt,lens):
        cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_end=6000; o=bpy.data.objects.new(n,cd); bpy.context.scene.collection.objects.link(o)
        o.location=loc; d=Vector(tgt)-Vector(loc); o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); o['qj']=1; return o
    cam(NAMES[0],(310,110,g(310,110)+85),(212,200,g(212,200)),30)
    cam(NAMES[1],(250,188,g(250,188)+1.7),(205,200,g(205,200)+1.5),28)
    cam(NAMES[2],(198,215,g(198,215)+1.7),(245,180,g(245,180)),28)
    cam(NAMES[3],(234,203,g(234,203)+3.0),(221,195,g(221,195)),35)
    print('QJ cams added')
