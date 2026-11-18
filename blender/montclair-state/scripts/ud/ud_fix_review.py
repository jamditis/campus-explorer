"""Session ud self-review fixes: darken UD asphalt further; retarget cams.
Does not add new objects beyond adjusting existing ud_obj cams / ud_mat.
REVERT of ud_main still restores everything (mat deleted on revert after slot restore;
cams removed as ud_obj).
"""
import bpy, os
from mathutils import Vector

SAVE = os.environ.get('SAVE') == '1'
UD_MAT = 'UD_asphalt_worn_NormalAve_UNVERIFIED'
# Darker + warmer (still UNVERIFIED visual)
RAMP_LO = (0.018, 0.016, 0.014, 1.0)
RAMP_HI = (0.055, 0.048, 0.040, 1.0)

m = bpy.data.materials.get(UD_MAT)
if not m:
    raise SystemExit('missing UD mat')
for n in m.node_tree.nodes:
    if n.type == 'VALTORGB':
        n.color_ramp.elements[0].color = RAMP_LO
        n.color_ramp.elements[-1].color = RAMP_HI
        n.color_ramp.elements[0].position = 0.35
        n.color_ramp.elements[-1].position = 0.78
        print('UD mat darkened', RAMP_LO[:3], '->', RAMP_HI[:3])

def aim(o, loc, target, lens=None):
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if lens is not None:
        o.data.lens = lens
    print('cam', o.name, 'loc', tuple(round(c,2) for c in loc), '->', target)

# Close-up: above Normal Ave near mid ribbon, looking down at asphalt
# Ribbon bbox ~ x -276..-59, y -330..-263, z 114..122
o = bpy.data.objects.get('UD_CAM_closeup_NormalAve_asphalt')
if o:
    aim(o, (-170.0, -290.0, 123.5), (-170.0, -300.0, 117.8), lens=45)

# Oblique overview of Normal Ave edge from SW (was aimed at campus core)
o = bpy.data.objects.get('UD_CAM_oblique_day9_polish_from_SW')
if o:
    aim(o, (-280.0, -380.0, 175.0), (-160.0, -290.0, 120.0), lens=32)

# Walk-edge close-up (ensure usable as alternate detail)
o = bpy.data.objects.get('UD_CAM_closeup_Partridge_walk_edge')
if o:
    aim(o, (-112.0, 250.0, 142.5), (-100.5, 249.5, 139.7), lens=40)

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
print('UD fix_review DONE')
