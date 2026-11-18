# qm cameras (CELS hero swap + CCIS podium edge). Eye heights from a terrain raycast. REVERT=1 removes.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
dg=bpy.context.evaluated_depsgraph_get(); bt=BVHTree.FromObject(bpy.data.objects['Terrain_LiDAR_DTM_1m'],dg)
def g(x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; return h.z if h is not None else 137.5
CAMS={'QM_CAM_oblique_cels_ccis_from_SE':((205.0,95.0,g(205,95)+70),(95.0,195.0,150.0),30),
      'QM_CAM_eye_cels_from_east':((152.0,176.0,g(152,176)+1.7),(118.0,186.0,g(118,186)+6.0),26),
      'QM_CAM_eye_cels_from_west':((40.0,168.0,g(40,168)+1.7),(75.0,182.0,g(75,182)+6.0),26),
      'QM_CAM_closeup_cels_SE_base_terrace':((128.0,158.0,g(128,158)+2.0),(113.0,170.0,g(113,170)+2.5),30),
      'QM_CAM_closeup_ccis_podium_edge_east':((48.0,212.0,146.0),(29.5,214.0,143.5),35)}
for n,(loc,tgt,lens) in CAMS.items():
    o=bpy.data.objects.get(n)
    if o: cd=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(cd)
    if REV: continue
    cd=bpy.data.cameras.new(n); cd.lens=lens; cd.clip_end=3000; o=bpy.data.objects.new(n,cd); bpy.context.scene.collection.objects.link(o)
    o.location=loc; d=Vector(tgt)-o.location; o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); o['qm']=1
print('QM cams', 'removed' if REV else 'added')
