# sb: close-up camera on the University Promenade by the Annex west end. REVERT=1 removes it.
import bpy, os
from mathutils import Vector
N='SB_CAM_closeup_promenade_annex_W'
o=bpy.data.objects.get(N)
if o: bpy.data.objects.remove(o,do_unlink=True)
if os.environ.get('REVERT')!='1':
    dg=bpy.context.evaluated_depsgraph_get()
    def gz(x,y):
        r=bpy.context.scene.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
        return r[1].z if r[0] else 140.0
    cd=bpy.data.cameras.new(N); cd.lens=35; cam=bpy.data.objects.new(N,cd)
    bpy.data.collections['SB_AnnexWest_promenade_walks_UNVERIFIED'].objects.link(cam)
    x,y=-128.0,272.0; z=gz(x,y); cam.location=(x,y,z+2.2)
    t=Vector((-110.0,292.0,gz(-110,292)+0.6)); cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler()
    print('SB cam',tuple(cam.location))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
