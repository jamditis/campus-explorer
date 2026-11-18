"""2026-10-21 session dW (~11:40 AM ET). CCOM 1st floor made ONE level at the entrance threshold (137.40) where the facade allows.
Joe's photos 04/05 show one flat terrazzo floor; the dd/dc floors sat at 133.85/134.85/135.40/135.59/136.00 vs the entrance 137.41.
Measured (data/dW/probe2_dW.log): south/west facade window sills (inside) SOUTH0 ~137.6, SOUTH1 ~137.45, WEST0 ~138.0; loading-dock
personnel door 137.55 -> SOUTH0, SOUTH1, WEST0 raised to 137.40 (+1.81/+2.00/+1.40) with ALL their dd_ objects (walls, ceilings, LEDs,
doors, furniture, rugs). Their dV skirts (gap under the old wall) are hidden (building wall now starts below the floor).
dc east lounge (+ dV round tables, al/am mullions + sill parts, jf glass/head/sill, lounge floor) raised +2.55 to 137.40 so its west
doors meet SOUTH0; east glass re-seated in the UPPER part of its opening (137.40-141.38; CCOM X 02 looks down over treetops); the dU
spandrel above is shortened to 141.38-142.62 and a new infill panel (same stucco) closes the opening below (134.55-137.40).
EAST0 is NOT raised: its east facade windows have sills at 135.8 (row 2 at 139.9), so a 137.4 floor would cut through them -> flag.
Idempotent via custom prop dW_dz; REVERT=1 undoes. SAVE=1 saves."""
import bpy, os
from mathutils import Vector
Z = 137.40
REV = os.environ.get('REVERT') == '1'
def unshift():
    n = 0
    for o in bpy.data.objects:
        if 'dW_dz' in o:
            o.location.z -= o['dW_dz']; del o['dW_dz']; n += 1
        if o.get('dW_hidden'):
            o.hide_render = False; o.hide_viewport = False; del o['dW_hidden']
    sp = bpy.data.objects.get('CCOM_east_window_spandrel_dU')
    if sp and 'CCOM_east_window_spandrel_dU_pre_dW' in bpy.data.meshes:
        cur = sp.data; sp.data = bpy.data.meshes['CCOM_east_window_spandrel_dU_pre_dW']
        if cur.users == 0: bpy.data.meshes.remove(cur)
    inf = bpy.data.objects.get('CCOM_east_window_infill_below_dW')
    if inf: me = inf.data; bpy.data.objects.remove(inf); bpy.data.meshes.remove(me)
    return n
print('DW1 unshift', unshift(), flush=True)
def roots(objs):
    S = set(objs); return [o for o in objs if not (o.parent and o.parent in S)]
def shift(objs, dz, tag):
    R = roots(objs)
    for o in R:
        o.location.z += dz; o['dW_dz'] = dz
    print('DW1 shift', tag, 'objs', len(objs), 'roots', len(R), 'dz', round(dz, 3), flush=True)
    return R
if not REV:
    dd = bpy.data.collections['CCOM_1f_interior_full_dd']
    floors = {o.name.split('_')[1]: o for o in dd.all_objects if o.name.endswith('_floor_terrazzo')}
    def ftop(o): return max((o.matrix_world @ Vector(c)).z for c in o.bound_box)
    for seg in ('SOUTH0', 'SOUTH1', 'WEST0'):
        dz = Z - ftop(floors[seg])
        objs = [o for o in bpy.data.objects if o.name.startswith('dd_%s_' % seg) and '_skirt_' not in o.name and o.library is None]
        shift(objs, dz, seg)
        for o in bpy.data.objects:
            if o.name.startswith('dd_%s_skirt_' % seg):
                o.hide_render = True; o.hide_viewport = True; o['dW_hidden'] = True
    lounge_floor = bpy.data.objects['CCOM_lounge_east_sill_20261014jf']
    dz = Z - 134.85
    L = list(bpy.data.collections['CCOM_east_interior_joe_20261020dc'].all_objects)
    L += list(bpy.data.collections['CCOM_lounge_photo_20261015al'].all_objects)
    L += list(bpy.data.collections['CCOM_east_window_tables_dV'].all_objects)
    L += [bpy.data.objects[n] for n in ('CCOM_lounge_east_glass_20261014jf', 'CCOM_lounge_east_head_20261014jf',
                                         'CCOM_lounge_east_sill_20261014jf', 'CCOM_lounge_east_floor_20261014jf')]
    L = [o for o in dict.fromkeys(L) if o.library is None]
    shift(L, dz, 'lounge')
    bpy.context.view_layer.update()
    hi = [(o.name, round(max((o.matrix_world @ Vector(c)).z for c in o.bound_box), 2)) for o in L if o.type == 'MESH' and not o.hide_render]
    over = [h for h in hi if h[1] > 142.70]
    print('DW1 lounge max z', max(h[1] for h in hi), 'over 142.70:', over[:10], flush=True)
    # spandrel shorten: map z 138.83..142.62 -> 141.38..142.62
    sp = bpy.data.objects['CCOM_east_window_spandrel_dU']
    src = sp.data; src.name = 'CCOM_east_window_spandrel_dU_pre_dW'; src.use_fake_user = True
    me = src.copy(); me.name = 'CCOM_east_window_spandrel_dU_dW'; sp.data = me
    mw = sp.matrix_world; mi = mw.inverted()
    ws = [mw @ v.co for v in src.vertices]; z0 = min(w.z for w in ws); z1 = max(w.z for w in ws)
    nz0 = z0 + dz
    for v, w in zip(me.vertices, ws):
        w2 = w.copy(); w2.z = nz0 + (w.z - z0) * (z1 - nz0) / (z1 - z0); v.co = mi @ w2
    me.update()
    # infill below: same footprint, z 134.55 .. Z
    me2 = src.copy(); me2.name = 'CCOM_east_window_infill_below_dW'
    for v, w in zip(me2.vertices, ws):
        w2 = w.copy(); w2.z = 134.55 + (w.z - z0) * (Z - 134.55) / (z1 - z0); v.co = mi @ w2
    inf = bpy.data.objects.new('CCOM_east_window_infill_below_dW', me2); inf.matrix_world = mw.copy()
    for c in sp.users_collection: c.objects.link(inf)
    inf['dW_note'] = 'dW: opening below the re-seated east lounge glass (lounge floor raised to 137.40); same stucco as the dU spandrel'
    print('DW1 spandrel', round(z0, 2), round(z1, 2), '->', round(nz0, 2), round(z1, 2), '; infill 134.55 ->', Z, flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DW1_SAVED', flush=True)
