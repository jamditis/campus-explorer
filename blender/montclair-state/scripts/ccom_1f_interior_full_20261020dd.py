"""2026-10-20 session dd (~4:35 PM ET). CCOM 1st-floor lit interior along the full run east lounge -> entrance (Joe 3:47 PM ET:
"the first floor extends all the way to the entrance"; his photo 1 shows the lounge corridor ending at the glazed entrance doors).
Only what is visible through the glass: per facade run of r0 (1st-floor) windows a shallow corridor zone (<= 4 m deep, clipped by
ray casts against the CCOM wall shell) = terrazzo floor, white tile ceiling with 2 linear LED strips, white back wall with grey base,
maroon-framed frosted door units on the back wall, white end caps, sparse furniture near the glass (white tables + sage/grey shell
chairs, occasional blue / orange lounge chair). Runs: EAST (win 043-052, north of the dc lounge), SOUTH (058-080), WEST (082-090, to
the entrance). r0 instances on these runs are switched to a local 'lit' window variant without the asset room box / blind
(dd_orig_inst prop; restore on rerun/REVERT=1). Hidden area lights (camera/glossy/transmission invisible), sun/world/view untouched.
ALL sizes/positions UNVERIFIED (photo-description scaled). Materials reuse dc's (run after ccom_east_interior_joe_20261020dc.py).
Run on MAIN: SAVE=1 blender -b montclair_state.blend --python scripts/ccom_1f_interior_full_20261020dd.py"""
import bpy, bmesh, os, math
from mathutils import Vector, Matrix
CN = 'CCOM_1f_interior_full_dd'; ob = bpy.data.objects; sc = bpy.context.scene
old = bpy.data.collections.get(CN)
if old:
    for o in list(old.all_objects):
        d = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if d is not None and d.users == 0: (bpy.data.meshes if isinstance(d, bpy.types.Mesh) else bpy.data.lights).remove(d)
    bpy.data.collections.remove(old)
for o in ob:
    if o.get('dd_orig_inst'):
        o.instance_collection = bpy.data.collections[o['dd_orig_inst']]; del o['dd_orig_inst']
LIT = bpy.data.collections.get('CCOM_Win_Wing_A_lit_dd')
if os.environ.get('REVERT') == '1':
    if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile()
    raise SystemExit
col = bpy.data.collections.new(CN); sc.collection.children.link(col)
SRC = bpy.data.collections['CCOM_Win_Wing_A']
if LIT is None:
    LIT = bpy.data.collections.new('CCOM_Win_Wing_A_lit_dd'); LIT.instance_offset = SRC.instance_offset
    for o in SRC.all_objects:
        if any(o.name.endswith(s) for s in ('_reveal', '_sill', '_frame', '_glass')):
            n = bpy.data.objects.new(o.name + '_lit_dd', o.data); n.matrix_world = o.matrix_world.copy(); LIT.objects.link(n)
    LIT.use_fake_user = True
M = bpy.data.materials
def mm(n): return M[n]
M_white, M_base, M_tz, M_tile, M_led = mm('CCOM_dc_wall_white'), mm('CCOM_dc_base_grey'), mm('CCOM_dc_terrazzo'), mm('CCOM_dc_ceiling_tile'), mm('CCOM_dc_linear_led')
M_rug, M_tab, M_chr, M_blue, M_sage, M_grey, M_orng, M_wood = (mm(x) for x in ('CCOM_dc_rug_charcoal', 'CCOM_dc_table_white', 'CCOM_dc_chrome', 'CCOM_dc_shell_blue', 'CCOM_dc_shell_sage', 'CCOM_dc_shell_grey', 'CCOM_dc_lounge_orange', 'CCOM_dc_light_wood'))
M_mar = M.get('CCOM_maroon_frame_20261014jf') or mm('CCOM_dc_maroon'); M_frost = mm('CCOM_dc_frosted_glass'); M_slot = mm('CCOM_dc_slot_diffuser')
WALLS = ob['School of Communication and Media walls']
CLIP = [WALLS] + [ob[x] for x in ('CCOM_lounge_east_wallN_20261014jf', 'CCOM_lounge_east_wallS_20261014jf', 'CCOM_lounge_east_wallW_20261014jf', 'CCOM_lounge_east_glass_20261014jf') if x in ob]
def ray(origin, d):
    best = None
    for W_ in CLIP:
        mi = W_.matrix_world.inverted(); ok, loc, nor, i = W_.ray_cast(mi @ origin, (mi.to_3x3() @ d).normalized(), distance=60)
        if ok:
            dd = (W_.matrix_world @ loc - origin).length; best = dd if best is None else min(best, dd)
    return best
RUNS = {'EAST': range(43, 53), 'SOUTH': range(60, 81), 'WEST': range(82, 91)}   # 058 sits at the dc lounge SW corner -> excluded
NOBJ = 0
def lbox(nm, F, cu, cv, du, dv, z0, z1, m):
    global NOBJ
    o_, t, n = F
    me = bpy.data.meshes.new(nm); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((du, dv, z1 - z0, 1))); bm.to_mesh(me); bm.free()
    me.materials.append(m); o = bpy.data.objects.new(nm, me); col.objects.link(o)
    p = o_ + t * cu - n * cv
    o.matrix_world = Matrix.Translation((p.x, p.y, (z0 + z1) / 2)) @ Matrix.Rotation(math.atan2(t.y, t.x), 4, 'Z'); NOBJ += 1; return o
def area(nm, F, cu, cv, z, sx, sy, P):
    o_, t, n = F
    ld = bpy.data.lights.new(nm, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = sx; ld.size_y = sy; ld.energy = P; ld.color = (1.0, 0.96, 0.90)
    o = bpy.data.objects.new(nm, ld); col.objects.link(o); p = o_ + t * cu - n * cv
    o.matrix_world = Matrix.Translation((p.x, p.y, z)) @ Matrix.Rotation(math.atan2(t.y, t.x), 4, 'Z')
    o.visible_camera = False; o.visible_glossy = False; o.visible_transmission = False; return o
def chair(nm, F, cu, cv, z0, m, back_side=1):
    lbox(nm + '_seat', F, cu, cv, 0.48, 0.46, z0 + 0.42, z0 + 0.47, m)
    lbox(nm + '_back', F, cu, cv + back_side * 0.22, 0.46, 0.05, z0 + 0.47, z0 + 0.85, m)
    for a in (-0.18, 0.18):
        for b in (-0.17, 0.17): lbox(nm + '_leg', F, cu + a, cv + b, 0.03, 0.03, z0, z0 + 0.42, M_wood)
LP = float(os.environ.get('LP', '240')); seq = 0; report = []   # dd final used 240 W per window (140 read too dim behind daylight reflections)
SUB = []
for run, ids in RUNS.items():
    ws = [ob.get('CCOM_win_%03d_r0' % i) for i in ids]; ws = [w for w in ws if w and w.matrix_world.translation.length > 1]
    n = (ws[0].matrix_world.to_3x3() @ Vector((0, 1, 0))); n.z = 0; n.normalize(); o0 = ws[0].matrix_world.translation
    grp = {}
    for w in ws: grp.setdefault(round((w.matrix_world.translation - o0).dot(n) / 0.5), []).append(w)
    for k, g in enumerate(sorted(grp.values(), key=lambda g: g[0].name)): SUB.append(('%s%d' % (run, k), g))
for run, ws in SUB:
    n = (ws[0].matrix_world.to_3x3() @ Vector((0, 1, 0))); n.z = 0; n.normalize()
    cen = Vector((0, 8, 0)); 
    if (ws[0].matrix_world.translation - cen).dot(n) < 0: n = -n   # outward
    t = Vector((-n.y, n.x, 0)); o_ = ws[0].matrix_world.translation.copy(); o_.z = 0
    us = sorted(((w.matrix_world.translation - o_).dot(t), w) for w in ws)
    zc = sum(w.matrix_world.translation.z for w in ws) / len(ws)
    Z0 = zc - 1.3 - 0.62; ZC = zc + 1.3 + 0.38          # floor ~0.62 m below the sill, ceiling 0.38 m above the head (UNVERIFIED)
    # depth / end clipping by ray casts against the wall shell
    deps = []
    for u, w in us:
        p = w.matrix_world.translation.copy(); p.z = zc
        d = ray(p - n * 0.2, -n); deps.append(d if d else 99)
    D = max(1.6, min(4.0, min(deps) + 0.2 - 0.25))
    pin = o_ - n * 1.0; pin.z = zc
    ua = us[0][0] - 1.25; ub = us[-1][0] + 1.25
    ra = ray(pin + t * us[0][0], -t); rb = ray(pin + t * us[-1][0], t)
    if ra: ua = max(ua, us[0][0] - ra + 0.12)
    if rb: ub = min(ub, us[-1][0] + rb - 0.12)
    F = (o_, t, n); L = ub - ua; cu = (ua + ub) / 2
    report.append('%s n=%s wins=%d z0=%.2f zc=%.2f D=%.2f u=[%.2f,%.2f] deps=%s' % (run, tuple(round(c, 2) for c in n), len(ws), Z0, ZC, D, ua, ub, [round(x, 1) for x in deps]))
    for _, w in us:
        if w.instance_collection and w.instance_collection.name == 'CCOM_Win_Wing_A':
            w['dd_orig_inst'] = 'CCOM_Win_Wing_A'; w.instance_collection = LIT
    pre = 'dd_%s_' % run
    lbox(pre + 'floor_terrazzo', F, cu, 0.05 + D / 2, L, D, Z0 - 0.1, Z0, M_tz)
    lbox(pre + 'ceiling_tile', F, cu, 0.05 + D / 2, L, D, ZC, ZC + 0.08, M_tile)
    lbox(pre + 'back_wall', F, cu, D + 0.05 + 0.06, L, 0.12, Z0 - 0.1, ZC + 0.08, M_white)
    lbox(pre + 'back_base', F, cu, D + 0.05 - 0.01, L - 0.02, 0.04, Z0, Z0 + 0.10, M_base)
    for e, ue in (('a', ua - 0.06), ('b', ub + 0.06)):
        lbox(pre + 'endcap_' + e, F, ue, 0.05 + D / 2, 0.12, D, Z0 - 0.1, ZC + 0.08, M_white)
    for k, vv in enumerate((D * 0.32, D * 0.72)):
        lbox(pre + 'led_strip_%d' % k, F, cu, vv, L - 0.6, 0.07, ZC - 0.015, ZC + 0.01, M_led)
    lbox(pre + 'slot_diffuser', F, cu, D * 0.52, L - 0.8, 0.04, ZC - 0.005, ZC + 0.01, M_slot)
    # back-wall maroon frosted door units, between windows (every 2nd gap)
    for j in range(len(us) - 1):
        if j % 2: continue
        ug = (us[j][0] + us[j + 1][0]) / 2; vb = D + 0.05 - 0.04
        lbox(pre + 'door_%d_frost' % j, F, ug, vb, 1.5, 0.03, Z0, Z0 + 2.2, M_frost)
        for a in (-0.78, -0.08, 0.78): lbox(pre + 'door_%d_jamb' % j, F, ug + a, vb - 0.02, 0.06, 0.06, Z0, Z0 + 2.25, M_mar)
        lbox(pre + 'door_%d_head' % j, F, ug, vb - 0.02, 1.62, 0.06, Z0 + 2.2, Z0 + 2.28, M_mar)
        lbox(pre + 'door_%d_pull' % j, F, ug - 0.2, vb - 0.07, 0.025, 0.025, Z0 + 0.8, Z0 + 1.4, M_chr)
    # sparse furniture near the glass + one hidden area light per window
    for j, (u, w) in enumerate(us):
        seq += 1
        area(pre + 'area_%d' % j, F, u, D * 0.5, ZC - 0.05, 2.6, max(1.0, D - 0.6), LP)
        if j % 3 == 0:
            vt = 1.35
            lbox(pre + 'rug_%d' % j, F, u, vt, 2.4, 1.8, Z0, Z0 + 0.012, M_rug)
            lbox(pre + 'table_%d' % j, F, u, vt, 1.4, 0.7, Z0 + 0.72, Z0 + 0.75, M_tab)
            for a in (-0.4, 0.4): lbox(pre + 'tped_%d' % j, F, u + a, vt, 0.06, 0.06, Z0 + 0.012, Z0 + 0.72, M_chr)
            for a in (-0.35, 0.35):
                chair(pre + 'ch_%d_%s_f' % (j, a), F, u + a, vt - 0.62, Z0 + 0.012, M_sage if a < 0 else M_grey, back_side=-1)
                chair(pre + 'ch_%d_%s_b' % (j, a), F, u + a, vt + 0.62, Z0 + 0.012, M_grey if a < 0 else M_sage, back_side=1)
        elif j % 3 == 1 and D > 2.4:
            m = M_blue if (seq % 2) else M_orng
            lbox(pre + 'lounge_%d_seat' % j, F, u + 0.6, 0.85, 0.75, 0.7, Z0 + 0.25, Z0 + 0.42, m)
            lbox(pre + 'lounge_%d_back' % j, F, u + 0.6, 1.17, 0.75, 0.1, Z0 + 0.42, Z0 + 0.82, m)
            lbox(pre + 'lounge_%d_base' % j, F, u + 0.6, 0.85, 0.4, 0.4, Z0, Z0 + 0.25, M_chr)
print('DD_INT objects', NOBJ, flush=True)
for r in report: print('DD_RUN', r, flush=True)
# rule 4a: no dd face coplanar with the CCOM wall shell (sample face centres; plane distance < 2 cm and parallel)
wm = WALLS.matrix_world; planes = [((wm @ f.center), (wm.to_3x3() @ f.normal).normalized()) for f in WALLS.data.polygons]
bad = 0
for o in col.objects:
    if o.type != 'MESH': continue
    for f in o.data.polygons:
        c = o.matrix_world @ f.center; nn = (o.matrix_world.to_3x3() @ f.normal).normalized()
        for pc, pn in planes:
            if abs(nn.dot(pn)) > 0.999 and abs((c - pc).dot(pn)) < 0.02 and (c - pc).length < 8: bad += 1; break
print('DD_4A coplanar faces', bad, flush=True)
# stray scan: other visible meshes whose bbox overlaps a dd floor..ceiling zone
zones = []
for o in col.objects:
    if o.name.endswith('floor_terrazzo'):
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; zones.append((o.name, [min(v[i] for v in bb) for i in range(3)], [max(v[i] for v in bb) + (3.6 if i == 2 else 0) for i in range(3)]))
for o in bpy.context.scene.objects:
    if o.type != 'MESH' or o.hide_render or o.name in col.objects or o is WALLS or o.name.startswith('CCOM_win'): continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; lo = [min(v[i] for v in bb) for i in range(3)]; hi = [max(v[i] for v in bb) for i in range(3)]
    for zn, zl, zh in zones:
        if all(lo[i] < zh[i] - 0.05 and hi[i] > zl[i] + 0.05 for i in range(3)) and (hi[0]-lo[0]) < 80: print('DD_STRAY', zn, o.name, [round(x, 2) for x in lo], [round(x, 2) for x in hi], flush=True)
dg = bpy.context.evaluated_depsgraph_get()
for xy in [(-34, -20), (-32, -14), (-30, -8), (-28, -24), (-10, -32), (0, -32), (-5, -30)]:
    hit, loc, nor, i, o, m = sc.ray_cast(dg, Vector((xy[0], xy[1], 200)), Vector((0, 0, -1)))
    print('DD_GROUND', xy, round(loc.z, 2) if hit else None, o.name if hit else None, flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DD_SAVED', bpy.data.filepath, flush=True)
