# sd: close-up camera on the RED HAWK "A"/"W" letters (west wall of the Annex). REVERT=1 removes it.
import bpy, os
from mathutils import Vector
N='SD_CAM_closeup_mural_HAWK_letters'
if os.environ.get('REVERT')=='1':
    o=bpy.data.objects.get(N)
    if o: d=o.data; bpy.data.objects.remove(o); bpy.data.cameras.remove(d)
else:
    o=bpy.data.objects.get(N)
    if not o:
        cd=bpy.data.cameras.new(N); o=bpy.data.objects.new(N,cd); bpy.context.scene.collection.objects.link(o)
    o.data.lens=float(os.environ.get('LENS','35'))
    loc=Vector((-100.5, 317.0, 141.6)); tgt=Vector((-91.6, 320.0, 141.9))
    sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
    h,l,*_=sc.ray_cast(dg,Vector((loc.x,loc.y,250)),Vector((0,0,-1))); loc.z=(l.z if h else 140)+float(os.environ.get('EH','1.6'))
    o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); o.data.clip_end=3000; o['UNVERIFIED_sd']='sd camera'
    bpy.context.view_layer.update(); print('SD cam',tuple(round(v,2) for v in loc),'ground',round(l.z,2) if h else None)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile()
