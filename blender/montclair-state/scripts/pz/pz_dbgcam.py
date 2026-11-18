import bpy
from mathutils import Vector
N='ZZ_DBG_corner'; c=bpy.data.cameras.new(N); c.lens=50; o=bpy.data.objects.new(N,c); o.location=Vector((-178.6,162.0,153.6))
o.rotation_euler=(Vector((-176.65,159.75,152.85))-o.location).to_track_quat('-Z','Y').to_euler(); bpy.context.scene.collection.objects.link(o)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/pz_test.blend',copy=True)
