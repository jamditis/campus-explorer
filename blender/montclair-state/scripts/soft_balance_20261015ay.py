"""2026-10-15 ay: soft-light white-facade exposure balance (both Montclair blends).

After ax soft light (sun 3.5°, energy ×0.82, world ×1.3, AgX Base Contrast), white
precast (esp. Student Center plaza) went flat/high-key. This pass does NOT undo sun
angle/energy or Base Contrast.

Exact numbers (UNVERIFIED artistic):
  - World Background Strength: was ×1.3 vs pre-ax → now ×1.15 vs pre-ax
    i.e. multiply current Background Strength by (1.15/1.3) ≈ 0.884615 once.
  - White-heavy cams get custom prop ay_exposure_delta = -0.2 (render hint;
    north base EXPOSURE is already -1.0, so plaza WIP uses -1.2).
  - Sun angle/energy, view look: untouched.

Idempotent via world['ay_soft_balance'] / cam['ay_soft_balance'].
Args after --: [--save]
"""
import bpy, sys, math
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAVE = '--save' in argv
WORLD_FACTOR = 1.15 / 1.3  # ×1.3 -> ×1.15 vs pre-ax baseline
WHITE_CAMS = (
    'CAM_eye_student_center_plaza',
    'CAM_eye_student_center_glass',
    'CAM_oblique_student_center',
    'CAM_closeup_student_center_entry',
)
sc = bpy.context.scene
w = sc.world
if w and w.use_nodes and not w.get('ay_soft_balance'):
    for n in w.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeBackground':
            old = n.inputs['Strength'].default_value
            n.inputs['Strength'].default_value = old * WORLD_FACTOR
            print('WORLD', n.name, round(old, 4), '->', round(n.inputs['Strength'].default_value, 4),
                  'factor', round(WORLD_FACTOR, 6))
    w['ay_soft_balance'] = 1
    w['ay_world_vs_preax'] = 1.15
    print('WORLD_FLAG ay_soft_balance=1 (×1.15 vs pre-ax)')
elif w and w.get('ay_soft_balance'):
    print('WORLD already ay_soft_balance; skip')
else:
    print('WORLD missing or no nodes')

# Do not touch sun
for o in bpy.data.objects:
    if o.type == 'LIGHT' and o.data.type == 'SUN':
        print('SUN_KEEP', o.name, 'E', round(o.data.energy, 3),
              'A', round(math.degrees(o.data.angle), 2), 'ax_soft', o.get('ax_soft'))

print('LOOK_KEEP', sc.view_settings.look, 'scene_exposure', sc.view_settings.exposure)

for nm in WHITE_CAMS:
    o = bpy.data.objects.get(nm)
    if not o:
        continue
    if o.get('ay_soft_balance'):
        print('CAM_SKIP', nm, 'delta', o.get('ay_exposure_delta'))
        continue
    o['ay_exposure_delta'] = -0.2
    o['ay_soft_balance'] = 1
    print('CAM_WHITE', nm, 'ay_exposure_delta=-0.2')

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
