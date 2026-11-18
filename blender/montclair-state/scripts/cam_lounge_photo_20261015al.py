import bpy, math, sys
from mathutils import Vector
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
n = 'CAM_eye_CCOM_lounge_photo_al'
o = bpy.data.objects.get(n)
if o is None:
    cd = bpy.data.cameras.new(n); o = bpy.data.objects.new(n, cd); bpy.context.scene.collection.objects.link(o)
o.data.lens = 22; o.data.clip_start = 0.1; o.data.clip_end = 40000
L = Vector((21.02, -18.2, 134.85 + 1.3)); a = math.radians(-34.5)
tgt = L + Vector((math.cos(a), math.sin(a), math.tan(math.radians(4))))
o.location = L; o.rotation_euler = (tgt - L).to_track_quat('-Z', 'Y').to_euler()
print('CAM', n, tuple(o.location))
if '--save' in ARGV: bpy.ops.wm.save_mainfile(); print('SAVED')
