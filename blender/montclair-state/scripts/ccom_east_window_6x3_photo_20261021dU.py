"""2026-10-21 session dU (~9:35 AM ET). CCOM east lounge window -> 6 columns x 3 rows per Joe's own photo
refs/joe/ccom_interior_east_1f_joe_20261020_02.jpg (re-counted in dU: 6 equal columns edge to edge; 3 rows = short top
transom row ~0.21 H, tall middle ~0.465 H, lower ~0.325 H, measured on columns 4 and 6 of the photo, wide-angle lens -> +-0.03).
Undoes dd's 4x4 (which came from a text description, not the photo): dd verticals CCOM_lounge_mull4_* + mid transom
CCOM_lounge_row_mid_dd hidden; al's 6-column verticals CCOM_lounge_mull6_1..5 shown; am's two transoms moved to the photo ratios.
Opening (glass 0..6.21 m along the wall, ledge 135.366 -> head 142.53) unchanged. Reversible: dU_hidden/dU_orig_* props; REVERT=1.
Run on MAIN: SAVE=1 ../tools/blender_slot.sh -b montclair_state.blend --python scripts/ccom_east_window_6x3_photo_20261021dU.py"""
import bpy, os
from mathutils import Matrix
ob = bpy.data.objects
REV = os.environ.get('REVERT') == '1'
# restore anything touched before (idempotent)
for o in ob:
    if 'dU_orig_hr' in o:
        o.hide_render = bool(o['dU_orig_hr']); o.hide_viewport = bool(o['dU_orig_hv']); del o['dU_orig_hr']; del o['dU_orig_hv']
    if 'dU_orig_dz' in o:
        o.matrix_basis = Matrix.Translation((0, 0, -o['dU_orig_dz'])) @ o.matrix_basis; del o['dU_orig_dz']
def setvis(o, show):
    o['dU_orig_hr'] = o.hide_render; o['dU_orig_hv'] = o.hide_viewport
    o.hide_render = not show; o.hide_viewport = not show
if not REV:
    for o in ob:
        if o.name.startswith('CCOM_lounge_mull4_') and o.name.endswith('_dd'): setvis(o, False)
        if o.name == 'CCOM_lounge_row_mid_dd': setvis(o, False)
        if o.name.startswith('CCOM_lounge_mull6_') and o.name.endswith('_20261015al.001'): setvis(o, True)
    z0, z1 = 135.366, 142.53; H = z1 - z0
    zc = lambda o: sum((o.matrix_basis @ v.co).z for v in o.data.vertices) / len(o.data.vertices)
    for nm, zt in (('CCOM_lounge_row2_lo_20261015am', z0 + 0.325 * H), ('CCOM_lounge_row2_hi_20261015am', z1 - 0.21 * H)):
        o = ob[nm]; dz = zt - zc(o); o['dU_orig_dz'] = dz
        o.matrix_basis = Matrix.Translation((0, 0, dz)) @ o.matrix_basis
        print('DU_WIN transom', nm, 'z ->', round(zt, 3), 'dz', round(dz, 3), flush=True)
    vis = sorted(o.name for o in ob if o.name.startswith('CCOM_lounge_mull') and not o.hide_render)
    print('DU_WIN visible verticals', len(vis), vis, flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DU_SAVED', bpy.data.filepath, flush=True)
