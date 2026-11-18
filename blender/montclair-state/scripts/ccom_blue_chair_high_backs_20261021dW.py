"""2026-10-21 session dW (~11:39 AM ET). The 4 blue lounge chairs at the east window had 0.40 m backs (top at floor+0.78);
Joe's photo 02 and CCOM X 02 show high-back shells reaching ~1.0 m above the floor (photo-scaled from the 0.45 m seat, UNVERIFIED +/-0.08 m).
Each dc_blue_lounge_N_back is stretched in Z about its own bottom so the top sits at floor+1.02. Uses obj prop dW_back_orig
(orig scale.z, loc.z) for idempotency; REVERT=1 restores. SAVE=1 saves. Run after the one-level script (floor read from the lounge sill)."""
import bpy, os
from mathutils import Vector
fl = max((bpy.data.objects['CCOM_lounge_east_sill_20261014jf'].matrix_world @ Vector(c)).z for c in bpy.data.objects['CCOM_lounge_east_sill_20261014jf'].bound_box) - 0.09
for o in bpy.data.objects:
    if 'dW_back_orig' in o:
        o.scale.z, o.location.z = o['dW_back_orig']; del o['dW_back_orig']
bpy.context.view_layer.update()
if os.environ.get('REVERT') != '1':
    for i in range(4):
        o = bpy.data.objects['dc_blue_lounge_%d_back' % i]
        o['dW_back_orig'] = (o.scale.z, o.location.z)
        P = [o.matrix_world @ Vector(c) for c in o.bound_box]; z0 = min(p.z for p in P); z1 = max(p.z for p in P)
        k = (fl + 1.02 - z0) / (z1 - z0)
        # world z of origin stays relative: new_z(w) = z0 + (w - z0) * k  -> scale about z0
        o.scale.z *= k; o.location.z = z0 + (o.location.z - z0) * k
        print('DW4 back', i, 'z', round(z0, 2), round(z1, 2), '-> top', round(fl + 1.02, 2), 'k', round(k, 2), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DW4_SAVED', flush=True)
