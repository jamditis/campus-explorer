"""Session em (~2:45 AM ET Oct 22). MAIN, CCOM east lounge, Joe photos 01/04 (ea Next 5): along the chevron sofa the photos
show a row of small SQUARE white tables, each on ONE chrome column with a round chrome disc base, with a single chair on the
far side facing the sofa. dc had two 1.6 m long tables on twin pedestals perpendicular to the sofa. This hides them (prop
em3_hidden) and builds 4 square tables (0.76 m, 25 mm top, top z = dc top) in a row 0.10 m off the sofa front, and turns
the 4 visible dc side chairs to face the sofa across them (orig matrices in em3_orig_mw). Table size/count from photo 01
(~4 along the sofa); exact spacing APPROXIMATE. Run AFTER ccom_lounge_sofa_clearance_tufting_20261022em.py.
SAVE=1 saves; REVERT=1 restores."""
import bpy, bmesh, os, time, math, re
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'
CN = 'CCOM_square_tables_em'; O = bpy.data.objects
col = bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
for o in O:
    if 'em3_orig_mw' in o:
        o.matrix_world = Matrix([o['em3_orig_mw'][i*4:i*4+4] for i in range(4)]); del o['em3_orig_mw']
    if o.get('em3_hidden'):
        o.hide_render = o.hide_viewport = False; o.display_type = o.get('em3_disp', 'TEXTURED'); del o['em3_hidden']
        if 'em3_disp' in o: del o['em3_disp']
bpy.context.view_layer.update()
if REV:
    print('em tables: REVERTED')
else:
    def ctr(o): bb = [o.matrix_world @ Vector(v) for v in o.bound_box]; return sum(bb, Vector()) / 8
    a = ctr(O['dc_door0_frost']); b = ctr(O['dc_door1_frost'])
    d = Vector((b.x - a.x, b.y - a.y, 0)).normalized(); n = Vector((d.y, -d.x, 0))
    _tb = O['dc_table_0_top']; _tc = sum((_tb.matrix_world @ v.co for v in _tb.data.vertices), Vector()) / len(_tb.data.vertices)  # mesh data, not bound_box (zero when hidden)
    if n.dot(Vector((_tc.x - a.x, _tc.y - a.y, 0))) < 0: n = -n
    def P(t, s, z): return Vector((a.x + d.x * t + n.x * s, a.y + d.y * t + n.y * s, z))
    def S(o): return [(o.matrix_world @ Vector(v) - a).dot(n) for v in o.bound_box]
    def T(o): return [(o.matrix_world @ Vector(v) - a).dot(d) for v in o.bound_box]
    top0 = O['dc_table_0_top']; ztop = max((top0.matrix_world @ v.co).z for v in top0.data.vertices)
    zfl = max((O['dc_rug_0'].matrix_world @ Vector(v)).z for v in O['dc_rug_0'].bound_box)
    sofa = [o for o in O if o.name.startswith(('el_sofa_', 'el_sofa_backcushion_em', 'el_sofa_seat_em')) and not o.hide_render]
    sf = min(min(S(o)) for o in sofa); t0 = min(min(T(o)) for o in sofa); t1 = max(max(T(o)) for o in sofa)
    hid = 0
    for o in O:
        if o.name.startswith('dc_table_') and not o.hide_render:
            # hide_render only (+ bounds display): hide_viewport zeroes bound_box in background runs and broke the el/em sofa
            # scripts' table-side check on rerun
            o['em3_disp'] = o.display_type; o.hide_render = True; o.display_type = 'BOUNDS'; o['em3_hidden'] = 1; hid += 1
    col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    Mw = top0.active_material; Mc = bpy.data.materials.get('CCOM_dc_chrome')
    ang = math.atan2(d.y, d.x)
    def add(name, me, loc, mat, rot=ang):
        ob = bpy.data.objects.new(name, me); col.objects.link(ob); ob.location = loc; ob.rotation_euler = (0, 0, rot)
        me.materials.append(mat); ob['em_square_table_approx'] = 1
        for p in me.polygons: p.use_smooth = True
        return ob
    def box(name, lx, ly, lz, loc, mat, bev=0.0):
        me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(lx, ly, lz), verts=bm.verts); bm.to_mesh(me); bm.free()
        ob = add(name, me, loc, mat)
        if bev:
            m = ob.modifiers.new('bev', 'BEVEL'); m.width = bev; m.segments = 2
        return ob
    def cyl(name, r, h, loc, mat, seg=32, bev=0.0):
        me = bpy.data.meshes.new(name); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h); bm.to_mesh(me); bm.free()
        ob = add(name, me, loc, mat)
        if bev:
            m = ob.modifiers.new('bev', 'BEVEL'); m.width = bev; m.segments = 3; m.limit_method = 'ANGLE'
        return ob
    W = 0.76; NT = 4; L = t1 - t0; gap = (L - NT * W) / (NT - 1) if NT > 1 else 0
    gap = max(0.08, min(gap, 0.25)); span = NT * W + (NT - 1) * gap; ts0 = (t0 + t1) / 2 - span / 2
    sc = sf - 0.10 - W / 2; tcs = []
    for i in range(NT):
        tc = ts0 + W / 2 + i * (W + gap); tcs.append(tc)
        box('em_sqtable_%d_top' % i, W, W, 0.025, P(tc, sc, ztop - 0.0125), Mw, 0.004)
        box('em_sqtable_%d_spider' % i, 0.34, 0.34, 0.02, P(tc, sc, ztop - 0.035), Mc)
        hcol = ztop - 0.045 - (zfl + 0.02)
        cyl('em_sqtable_%d_column' % i, 0.035, hcol, P(tc, sc, zfl + 0.02 + hcol / 2), Mc)
        cyl('em_sqtable_%d_disc' % i, 0.25, 0.02, P(tc, sc, zfl + 0.01), Mc, 48, 0.006)
    print('em tables: hid %d dc table parts; %d square tables W %.2f gap %.2f, centre s %.2f (sofa front %.2f), t %s, top z %.3f floor %.3f'
          % (hid, NT, W, gap, sc, sf, [round(x, 2) for x in tcs], ztop, zfl))
    # turn the 4 visible side chairs to face the sofa, one per table, on the far side
    groups = {}
    for o in O:
        m = re.match(r'(dc_side_chair_\d+_\d+)_', o.name)
        if m and not o.hide_render: groups.setdefault(m.group(1), []).append(o)
    gk = sorted(groups, key=lambda k: sum(T(o)[0] for o in groups[k]) / len(groups[k]))
    sch = sc - W / 2 - 0.22
    for k, tc in zip(gk, tcs):
        parts = groups[k]; seat = next(o for o in parts if o.name.endswith('_seat')); back = next(o for o in parts if o.name.endswith('_back'))
        c0 = ctr(seat); bdir = (ctr(back) - c0); bdir.z = 0; bdir.normalize()
        want = -n; rot = math.atan2(want.y, want.x) - math.atan2(bdir.y, bdir.x)
        target = P(tc, sch, c0.z)
        Mx = Matrix.Translation(Vector((target.x, target.y, 0))) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Translation(Vector((-c0.x, -c0.y, 0)))
        for o in parts:
            o['em3_orig_mw'] = [x for row in o.matrix_world for x in row]; o.matrix_world = Mx @ o.matrix_world
    bpy.context.view_layer.update()
    # clearance report
    def ext(pre):
        ss = []
        for o in O:
            if o.name.startswith(pre) and not o.hide_render: ss += S(o)
        return (round(min(ss), 2), round(max(ss), 2)) if ss else None
    print('em tables: s-extents tables %s, chairs %s, sofa %s, grey/orange lounge %s/%s' % (ext('em_sqtable_'), ext('dc_side_chair_'), ext('el_sofa_'), ext('dc_grey_lounge'), ext('dc_orange_lounge')))
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('em tables: SAVED', time.strftime('%H:%M:%S'))
