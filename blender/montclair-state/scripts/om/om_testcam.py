# test-only: top-down cam over the small island (not saved in main)
import bpy
from mathutils import Vector
d=bpy.data.cameras.new('OM_TEST_top_small_island'); o=bpy.data.objects.new('OM_TEST_top_small_island',d); bpy.context.scene.collection.objects.link(o)
o.location=(21.6,136.5,175); o.rotation_euler=(0,0,0); d.lens=35
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/om_test.blend',copy=True)
