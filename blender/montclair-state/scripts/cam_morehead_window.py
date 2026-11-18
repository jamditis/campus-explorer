"""Add CAM_closeup_Morehead_window aimed at a west-face modelled window, plus CAM_eye_Morehead_south if missing.
blender -b montclair_state.blend --python scripts/cam_morehead_window.py -- --save
"""
import bpy, sys
from mathutils import Vector
sc = bpy.context.scene
# prefer a west-face ground-floor window (normal ~ westward = n.x ~ -1)
wins = [o for o in bpy.data.objects if o.name.startswith('MH_win_') and o.instance_type == 'COLLECTION']
west = [o for o in wins if o.matrix_world[0][1] < -0.7 and o.get('row') == 0]  # Y axis of instance = outward; matrix col1
# matrix_world columns: X=along, Y=outward, Z=up; outward.x = matrix[0][1]
west = sorted([o for o in wins if o.matrix_world[0][1] < -0.5], key=lambda o: (o.get('row', 9), abs(o.matrix_world.translation.y + 42)))
if not west:
    west = sorted(wins, key=lambda o: o.get('row', 9))
target = west[0] if west else None
print('closeup target', target.name if target else None, 'of', len(wins))
def ensure_cam(name, loc, look_at, lens=35):
    cam_data = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cam = bpy.data.objects.get(name) or bpy.data.objects.new(name, cam_data)
    if cam.name not in sc.collection.objects: sc.collection.objects.link(cam)
    cam.location = Vector(loc); direction = Vector(look_at) - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam_data.lens = lens; cam_data.clip_end = 6000
    return cam
if target:
    p = target.matrix_world.translation
    n = Vector((target.matrix_world[0][1], target.matrix_world[1][1], 0)).normalized()  # outward
    # stand 4.5 m out, eye height ~1.6 m above sill mid
    loc = p + n * 7.0 + Vector((0, 0, 0.75))
    look = p + Vector((0, 0, 1.25))
    c = ensure_cam('CAM_closeup_Morehead_window', loc, look, lens=40)
    print('CAM_closeup_Morehead_window', tuple(round(x, 2) for x in c.location), '->', target.name)
# eye-level on south/east side of Morehead (existing CAM_eye_south_Morehead may suffice; add east if useful)
mh = next((o for o in bpy.data.objects if o.get('osm_id') == '312933183' and o.name.endswith('walls')), None)
if mh:
    vs = [mh.matrix_world @ v.co for v in mh.data.vertices]
    cx = sum(v.x for v in vs) / len(vs); cy = sum(v.y for v in vs) / len(vs); cz = min(v.z for v in vs)
    # south-east eye looking toward Morehead
    c2 = ensure_cam('CAM_eye_Morehead_SE', (cx + 28, cy - 35, cz + 1.7), (cx - 5, cy - 10, cz + 4.5), lens=32)
    print('CAM_eye_Morehead_SE', tuple(round(x, 2) for x in c2.location))
if '--save' in sys.argv:
    bpy.ops.wm.save_mainfile(); print('SAVED')
