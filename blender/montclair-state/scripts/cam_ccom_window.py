"""Add CAM_closeup_CCOM_window: oblique close-up of the modelled ground-floor wing window nearest the main entrance (west face, south of it)."""
import bpy, sys
from mathutils import Vector
cam_e = bpy.data.objects['CAM_eye_CCOM_entrance']
E = [o for o in bpy.data.objects if o.name.startswith('CCOM_win_') and o.get('row') == 0]
pa, pb = bpy.data.objects['CCOM entrance pier +1'], bpy.data.objects['CCOM entrance pier -1']
ent = (pa.matrix_world.translation + pb.matrix_world.translation) / 2
ent = sum((pa.matrix_world @ v.co for v in pa.data.vertices), Vector()) / len(pa.data.vertices) * 0.5 + sum((pb.matrix_world @ v.co for v in pb.data.vertices), Vector()) / len(pb.data.vertices) * 0.5
def outward(e): return Vector((e.matrix_world[0][1], e.matrix_world[1][1], 0))
vis = [e for e in E if outward(e).dot((cam_e.location - e.matrix_world.translation).normalized()) > 0.3]
w = min(vis, key=lambda e: (e.matrix_world.translation.xy - ent.xy).length)
p = w.matrix_world.translation; n = outward(w); t = Vector((w.matrix_world[0][0], w.matrix_world[1][0], 0))
tgt = p + Vector((0, 0, 1.3)) - n * 0.2
c = bpy.data.objects.get('CAM_closeup_CCOM_window')
if c is None:
    c = bpy.data.objects.new('CAM_closeup_CCOM_window', bpy.data.cameras.new('CAM_closeup_CCOM_window')); cam_e.users_collection[0].objects.link(c)
c.data.lens = 30; c.location = p + n * 4.2 + t * 1.9 + Vector((0, 0, 1.25)); c.rotation_euler = (tgt - c.location).to_track_quat('-Z', 'Y').to_euler()
print('CLOSEUP on', w.name, tuple(round(v, 2) for v in p))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
