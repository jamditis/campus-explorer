# ql close-up camera on the CCIS east S junction (cover wall / QH / skin). REVERT=1 removes it.
import bpy, os
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; n='QL_CAM_closeup_ccis_east_S_junction'
o=bpy.data.objects.get(n)
if o: cd=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.cameras.remove(cd)
if not REV:
    cd=bpy.data.cameras.new(n); cd.lens=35; cd.clip_end=3000; o=bpy.data.objects.new(n,cd); bpy.context.scene.collection.objects.link(o)
    o.location=(44.0,196.0,143.5); d=Vector((29.3,206.0,147.0))-o.location; o.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); o['ql']=1
    print('QL cam added')
