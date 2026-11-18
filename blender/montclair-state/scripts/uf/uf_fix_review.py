"""Self-review fixes for uf: reframe soft-end cams; darken arch glass."""
import bpy, os
from mathutils import Vector

SAVE = os.environ.get('SAVE') == '1'
TAG = 'uf_obj'

def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()

def set_cam(name, loc, target, lens=None):
    o = bpy.data.objects.get(name)
    if not o:
        print('missing', name); return
    o.location = Vector(loc)
    aim(o, target)
    if lens is not None:
        o.data.lens = lens
    print('fixed', name, '->', tuple(round(x,2) for x in loc), 'look', target)

# Soft-end closeup: west tip of Normal Ave CR618 (~-275,-268 / -276,-270)
set_cam('UF_CAM_closeup_NormalAve_softend',
        (-262.0, -275.0, 119.2), (-275.5, -268.5, 117.35), lens=40)
# Eye along Normal Ave looking toward west soft end / asphalt ribbon
set_cam('UF_CAM_eye_NormalAve_from_N',
        (-180.0, -280.0, 119.5), (-240.0, -275.0, 117.5), lens=32)
# Arch closeup: pull slightly east/out and lower to hit GF arches
set_cam('UF_CAM_closeup_CollegeHall_east_arches',
        (-45.0, -118.0, 134.0), (-63.5, -116.0, 134.2), lens=40)
# Eye E: nudge to center on arched GF band
set_cam('UF_CAM_eye_CollegeHall_from_E',
        (-30.0, -115.0, 134.5), (-64.0, -115.0, 134.5), lens=35)

# Darken / clarify UF glass
m = bpy.data.materials.get('UF_Cole_arch_glass_clearer_UNVERIFIED')
if m and m.node_tree:
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.02, 0.025, 0.03, 1)
        b.inputs['Roughness'].default_value = 0.08
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 0.55
        print('darkened UF glass')

if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
print('UF fix-review DONE')
