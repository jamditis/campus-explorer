"""2026-10-21 session dW (~11:40 AM ET). After the one-level raise (ccom_one_level_1f_20261021dW.py) the raised SOUTH0/SOUTH1/WEST0
ceilings (floor+3.7 = ~141.1) sat ABOVE the floors of the 2nd-storey window room boxes (CCOM_Win_Wing_A_floor at 140.6-140.8),
so dark room boxes showed inside the corridor (data/dW/test/t2). Ceiling items (tile, LED strips, slot diffusers, anything whose
bottom is within 0.15 m of the ceiling tile) are lowered to a 140.45 ceiling (3.05 m clear; photos 04/05 read ~3 m).
Idempotent via prop dW2_dz; REVERT=1 undoes. SAVE=1 saves. Run AFTER the one-level script."""
import bpy, os
from mathutils import Vector
CEIL = 140.45
for o in bpy.data.objects:
    if 'dW2_dz' in o: o.location.z -= o['dW2_dz']; del o['dW2_dz']
bpy.context.view_layer.update()
def bbz(o):
    P = [(o.matrix_world @ Vector(c)).z for c in o.bound_box]; return min(P), max(P)
if os.environ.get('REVERT') != '1':
    for seg in ('SOUTH0', 'SOUTH1', 'WEST0'):
        ct = bpy.data.objects['dd_%s_ceiling_tile' % seg]
        cb = bbz(ct)[0]; dz = CEIL - cb
        objs = [o for o in bpy.data.objects if o.name.startswith('dd_%s_' % seg) and o.library is None
                and not any(k in o.name for k in ('back_wall', 'endcap', 'skirt')) and bbz(o)[0] >= cb - 0.15]
        S = set(objs); R = [o for o in objs if not (o.parent and o.parent in S)]
        for o in R: o.location.z += dz; o['dW2_dz'] = dz
        print('DW2', seg, 'ceil', round(cb, 2), '->', CEIL, 'objs', len(R), sorted({o.name.split('_')[2] for o in R}), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DW2_SAVED', flush=True)
