# test-only: low oblique from the NE over the floating NNE walk cells (not saved in main)
import bpy
from mathutils import Vector
d=bpy.data.cameras.new('OM_TEST_float_walk_NNE'); o=bpy.data.objects.new('OM_TEST_float_walk_NNE',d); bpy.context.scene.collection.objects.link(o)
o.location=Vector((75,215,142)); tgt=Vector((38,180,135)); o.rotation_euler=(tgt-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=24
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/om_test.blend',copy=True)
