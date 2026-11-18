"""wp review: reframe closeup onto the ravine-head woodland floor (first cam showed
mostly the Stone Hall lawn plateau with the hollow as a thin brown strip at the top)."""
import bpy, math, json
from mathutils import Vector
R = '/workspace/nj-scenes/montclair-state'
cam = bpy.data.objects['WP_CAM_closeup_gully_head_floor']
# closer to the wood edge, longer lens, still on the lawn plateau SW of the hollow
# so we see lawn → woodland-floor transition + the hollow under the trees
loc = Vector((164.0, 308.0, 148.0))
tgt = Vector((174.0, 318.0, 132.0))
cam.location = loc
d = tgt - loc
cam.rotation_euler = (
    math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)),
    0,
    math.atan2(d.y, d.x) - math.pi / 2,
)
cam.data.lens = 55
cam['UNVERIFIED'] = (
    'wp: closeup of ravine-head woodland floor from the SW lawn plateau '
    '(164,308,148) -> (174,318,132), 55 mm (review: first cam at 158,302,152 / 35 mm '
    'was too far back and read as lawn with only a thin brown strip at the tree line)'
)
rep = {'loc': list(loc), 'tgt': list(tgt), 'lens': 55, 'objs': len(bpy.data.objects)}
json.dump(rep, open(f'{R}/data/wp/cam2.json', 'w'), indent=1)
print('CAM2', rep)
bpy.ops.wm.save_mainfile()
print('SAVED')
