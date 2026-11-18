"""2026-10-21 session dU (~9:40 AM ET). CCOM east lounge window HEIGHT + ceiling per Joe's photo 02
(refs/joe/ccom_interior_east_1f_joe_20261020_02.jpg). Scale from the door in the same wall plane (~2.13 m, UNVERIFIED):
sill ~0.4-0.5 m (kept 0.48 m), glass ~3.5 m (+-0.4), the room ceiling (tile grid + slot diffuser) meets the window head at ~4.1 m.
The jf/al/dd model had 7.2 m of glass to 142.62 and a double-height room with a balcony on the back wall (dc, from a text
description of photo 03) -> photo 02 shows a single ~4.1 m ceiling over the window bay and the table lounge behind it.
Changes (all reversible, props dU_*; REVERT=1): glass + 7 verticals scaled to 134.85..138.83; head frame moved to 138.74..138.83;
transoms re-set to the photo ratios (bottom 0.325 H, top row 0.21 H); plain precast spandrel panel 138.83..142.62 in the opening
(exterior above the window UNVERIFIED: no exterior photo of this bay); dc ceiling tiles / linear LEDs / slot diffusers / LED lights
lowered 142.5 -> 138.95; dc balcony + interior window (now above the ceiling) hidden. Run AFTER ccom_east_window_6x3_photo_20261021dU.py.
Run on MAIN: SAVE=1 ../tools/blender_slot.sh -b montclair_state.blend --python scripts/ccom_east_window_height_photo_20261021dU.py"""
import bpy, bmesh, os
from mathutils import Vector, Matrix
ob = bpy.data.objects; REV = os.environ.get('REVERT') == '1'
PN = 'CCOM_east_window_spandrel_dU'
if PN in ob:
    me = ob[PN].data; bpy.data.objects.remove(ob[PN], do_unlink=True); bpy.data.meshes.remove(me)
for o in ob:
    if 'dUh_orig_mb' in o:
        o.matrix_basis = Matrix([list(o['dUh_orig_mb'][i*4:(i+1)*4]) for i in range(4)]); del o['dUh_orig_mb']
    if 'dUh_hidden' in o:
        o.hide_render = bool(o['dUh_hr']); o.hide_viewport = bool(o['dUh_hv']); del o['dUh_hidden']; del o['dUh_hr']; del o['dUh_hv']
def keep(o):
    if 'dUh_orig_mb' not in o: o['dUh_orig_mb'] = [c for row in o.matrix_basis for c in row]
def pre(o, M): keep(o); o.matrix_basis = M @ o.matrix_basis
Z0, ZT_OLD, ZT = 134.85, 142.62, 138.83; k = (ZT - Z0) / (ZT_OLD - Z0)
LEDGE = 135.366; HEAD0 = ZT - 0.09; H = HEAD0 - LEDGE
if not REV:
    S = Matrix.Translation((0, 0, Z0)) @ Matrix.Diagonal((1, 1, k, 1)) @ Matrix.Translation((0, 0, -Z0))
    tgt = ['CCOM_lounge_east_glass_20261014jf'] + [o.name for o in ob if o.name.startswith('CCOM_lounge_mull6_')] \
        + [o.name for o in ob if o.name.startswith('CCOM_lounge_mull4_') and o.name.endswith('_dd')]
    for nm in tgt: pre(ob[nm], S)
    pre(ob['CCOM_lounge_east_head_20261014jf'], Matrix.Translation((0, 0, HEAD0 - 142.53)))
    zc = lambda o: sum((o.matrix_basis @ v.co).z for v in o.data.vertices) / len(o.data.vertices)
    for nm, zt in (('CCOM_lounge_row2_lo_20261015am', LEDGE + 0.325 * H), ('CCOM_lounge_row2_hi_20261015am', HEAD0 - 0.21 * H)):
        o = ob[nm]; pre(o, Matrix.Translation((0, 0, zt - zc(o)))); print('DUH transom', nm, round(zt, 3), flush=True)
    # spandrel infill above the window (inside the opening only)
    A = Vector((23.45, -24.78, 0)); B = Vector((25.0, -18.76, 0)); D = (B - A).normalized(); NI = Vector((-D.y, D.x, 0))
    if NI.x > 0: NI = -NI
    u0, u1, v0, v1 = 0.02, 6.19, -0.05, 0.30
    me = bpy.data.meshes.new(PN); bm = bmesh.new()
    vs = [bm.verts.new(A + D * u + NI * v + Vector((0, 0, z))) for z in (ZT, ZT_OLD - 0.005) for (u, v) in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    me.materials.append(bpy.data.materials['Wall_SCM_precast'])
    p = bpy.data.objects.new(PN, me); ob['CCOM_lounge_east_head_20261014jf'].users_collection[0].objects.link(p)
    p['note'] = 'dU: plain infill above the 3.5 m east lounge window (Joe photo 02); exterior treatment UNVERIFIED'
    # interior ceiling down to ~4.1 m
    dc = bpy.data.collections['CCOM_east_interior_joe_20261020dc']
    for o in dc.all_objects:
        n = o.name
        if n.startswith('dc_balcony_') and n != 'dc_balcony_area' or n.startswith('dc_int_window_'):
            o['dUh_hidden'] = 1; o['dUh_hr'] = o.hide_render; o['dUh_hv'] = o.hide_viewport; o.hide_render = True; o.hide_viewport = True
        elif n in ('dc_ceiling_tiles', 'dc_linear_led_0', 'dc_linear_led_1', 'dc_linear_led_2', 'dc_slot_diffuser_0', 'dc_slot_diffuser_1',
                   'dc_led_area_0', 'dc_led_area_1', 'dc_led_area_2'):
            pre(o, Matrix.Translation((0, 0, 138.95 - 142.50)))
    print('DUH done k', round(k, 4), 'head', HEAD0, 'H', round(H, 3), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DUH_SAVED', bpy.data.filepath, flush=True)
