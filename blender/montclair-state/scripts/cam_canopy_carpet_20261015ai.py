import bpy, sys
from mathutils import Vector
n="CAM_closeup_canopy_carpet_ai"
o=bpy.data.objects.get(n)
if o is None:
    cd=bpy.data.cameras.new(n); o=bpy.data.objects.new(n,cd); bpy.context.scene.collection.objects.link(o)
o.location=Vector((1290.0,-690.0,150.0)); tgt=Vector((1000.0,-960.0,66.0))
o.rotation_euler=(tgt-o.location).to_track_quat('-Z','Y').to_euler(); o.data.lens=35; o.data.clip_end=20000
print("CAM",tuple(o.location)); bpy.ops.wm.save_mainfile(); print("SAVED")
