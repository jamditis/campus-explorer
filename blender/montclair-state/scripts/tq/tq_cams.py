# tq cameras (tagged tq_obj; tq_main REVERT removes them). Positions picked clear of the TL LiDAR tree crowns (data/tl/dorm_tree_tops.json).
import bpy, os, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); col=bpy.data.collections['TQ_Stone_fascia_UNVERIFIED']
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
def gz(x,y):
    best=None
    for n in GN:
        o=bpy.data.objects.get(n)
        if not o: continue
        e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
        r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z; best=z if best is None or z>best else best
    return best
C=json.loads(os.environ['TQCAMS'])
for name,(x,y,tx,ty,tz,lens) in C.items():
    old=bpy.data.objects.get(name)
    if old: bpy.data.objects.remove(old)
    z=gz(x,y); loc=Vector((x,y,z+1.65)); cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000
    o=bpy.data.objects.new(name,cd); col.objects.link(o); o['tq_obj']=1; o.location=loc
    o.rotation_euler=(Vector((tx,ty,z+tz))-loc).to_track_quat('-Z','Y').to_euler(); print('TQCAM',name,[round(v,2) for v in loc])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
