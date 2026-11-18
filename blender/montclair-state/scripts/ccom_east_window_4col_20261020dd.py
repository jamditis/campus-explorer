"""2026-10-20 session dd (~4:30 PM ET). CCOM east lounge curtain wall -> ~4 panes across (Joe 3:47 PM: "match the images";
his 3:17 PM interior photo shows an approx. 4x4 grid). Replaces al's 6-column verticals (CCOM_lounge_mull6_1..5) with 3 interior
verticals at L/4 spacing over the same opening, plus a middle transom (4 rows); edge frames mull6_0 / mull6_6, glass, rows, sill, head unchanged.
Reversible: hidden originals carry dd_hidden (+dd_orig_hr/hv); REVERT=1 restores and deletes the new verticals. Idempotent.
Run on MAIN: SAVE=1 blender -b montclair_state.blend --python scripts/ccom_east_window_4col_20261020dd.py
Column count from Joe's photo description (approx. 4) = UNVERIFIED +-0; positions = equal bays (UNVERIFIED)."""
import bpy, os
from mathutils import Vector, Matrix
A = Vector((23.45, -24.78, 0)); B = Vector((25.0, -18.76, 0)); T = (B - A).normalized(); L = (B - A).length
ob = bpy.data.objects
for o in [o for o in ob if (o.name.startswith('CCOM_lounge_mull4_') and o.name.endswith('_dd')) or o.name.startswith('CCOM_lounge_row_mid_dd')]: bpy.data.objects.remove(o, do_unlink=True)
for o in ob:
    if o.get('dd_hidden'):
        o.hide_render = bool(o['dd_orig_hr']); o.hide_viewport = bool(o['dd_orig_hv']); del o['dd_hidden']
if os.environ.get('REVERT') != '1':
    m6 = sorted([o for o in ob if o.name.startswith('CCOM_lounge_mull6_')], key=lambda o: o.name)
    ref = ob['CCOM_lounge_mull6_3_20261015al.001']
    def u(o): return (o.matrix_basis.translation - A).dot(T)   # basis: hidden objects are not depsgraph-evaluated (matrix_world = identity)
    u3 = u(ref); print('DD_WIN ref u', round(u3, 3), 'L', round(L, 3), 'old', [round(u(o), 2) for o in m6], flush=True)
    for o in m6:
        if not (o.name.startswith('CCOM_lounge_mull6_0_') or o.name.startswith('CCOM_lounge_mull6_6_')):
            o['dd_hidden'] = 1; o['dd_orig_hr'] = o.hide_render; o['dd_orig_hv'] = o.hide_viewport; o.hide_render = True; o.hide_viewport = True
    for k in (1, 2, 3):
        n = ref.copy(); n.name = 'CCOM_lounge_mull4_%d_dd' % k
        for c in ref.users_collection: c.objects.link(n)
        for k_ in ('dd_hidden', 'dd_orig_hr', 'dd_orig_hv'):
            if k_ in n: del n[k_]
        n.hide_render = False; n.hide_viewport = False
        n.matrix_basis = Matrix.Translation(T * (L * k / 4 - u3)) @ ref.matrix_basis
        print('DD_WIN new', n.name, round(u(n), 3), flush=True)
    # 4 rows (Joe: approx. 4x4): am left 2 transoms (136.76 / 140.64) = 3 uneven rows -> add a middle transom at their midpoint
    lo_, hi_ = ob['CCOM_lounge_row2_lo_20261015am'], ob['CCOM_lounge_row2_hi_20261015am']
    zc_ = lambda o: sum((o.matrix_basis @ v.co).z for v in o.data.vertices) / len(o.data.vertices)
    dz = (zc_(hi_) - zc_(lo_)) / 2
    n = lo_.copy(); n.name = 'CCOM_lounge_row_mid_dd'
    for c in lo_.users_collection: c.objects.link(n)
    n.hide_render = False; n.hide_viewport = False
    n.matrix_basis = Matrix.Translation((0, 0, dz)) @ lo_.matrix_basis
    print('DD_WIN mid transom z', round(zc_(lo_) + dz, 3), 'dz', round(dz, 3), flush=True)
    # 4a: verticals must not touch the room side walls
    for nm in ('CCOM_lounge_east_wallS_20261014jf', 'CCOM_lounge_east_wallN_20261014jf'):
        w = ob[nm]; ws = [ (w.matrix_world @ v.co - A).dot(T) for v in w.data.vertices]
        print('DD_WIN 4a wall', nm, 'u range', round(min(ws), 2), round(max(ws), 2), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DD_SAVED', bpy.data.filepath, flush=True)
