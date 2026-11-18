"""2026-10-15 ax rev3: closeup = same viewpoint as CAM_oblique_CCOM_east_jf (known open air), lens x2.4, aimed at the mixed
tree group on the right/left of that frame. Earlier auto placements landed inside closed volumes (black frames)."""
import bpy, math, os
from mathutils import Vector
U, V = float(os.environ.get('U', '0.70')), float(os.environ.get('V', '0.58'))
sc = bpy.context.scene
ob = bpy.data.objects['CAM_oblique_CCOM_east_jf']; cd = ob.data
sw = cd.sensor_width; sh = sw * 720 / 1280
d = Vector(((U - 0.5) * sw / cd.lens, (0.5 - V) * sh / cd.lens, -1.0))
dw = (ob.matrix_world.to_quaternion() @ d).normalized()
co = bpy.data.objects['CAM_closeup_trees_variety_ax']
co.location = ob.location.copy(); co.rotation_euler = dw.to_track_quat('-Z', 'Y').to_euler()
co.data.lens = cd.lens * 2.4; co.data.sensor_width = sw; co.data.clip_end = 30000
print('CAMFIX2', tuple(round(x, 1) for x in co.location), 'lens', round(co.data.lens, 1))
bpy.ops.wm.save_mainfile(); print('SAVED')
