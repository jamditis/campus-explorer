"""Session fa (~4:25 PM ET Oct 22). MAIN, CCOM east lounge. Dispatcher pinned note 3:55 PM: lounge layout CLOSED, sofa stays
along the maroon-door wall; restore the two long white tables in the middle of the room (Joe photos 01/02 show both the
sofa row with small square tables AND two long white tables with grey shell chairs on both long sides, long axis parallel
to the door wall). em hid dc's two 0.8 x 1.6 m long tables (em3_hidden). This unhides them, turns them 90 deg so their long
axis runs parallel to the door wall, centres them in the free carpet band between the door-side lounge chairs (s<=1.76)
and the square-table chairs (s>=3.80), and seats 2 en shell chairs per long side (8 copies of the visible
dc_side_chair_0_1 en parts, sharing mesh data). Positions APPROXIMATE (photo-scaled), sizes kept from dc.
Run AFTER ccom_lounge_square_tables_20261022em.py and the en side-chair script. SAVE=1 saves; REVERT=1 restores."""
import bpy, os, time, math
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'
CN = 'CCOM_long_tables_fa'; O = bpy.data.objects
col = bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
for o in O:
    if 'fa_orig_mw' in o:
        o.matrix_world = Matrix([o['fa_orig_mw'][i*4:i*4+4] for i in range(4)]); del o['fa_orig_mw']
    if o.get('fa_rug_hidden'):
        o.hide_render = False; del o['fa_rug_hidden']
    if o.get('fa_unhid'):
        o.hide_render = True; o.display_type = 'BOUNDS'; del o['fa_unhid']
bpy.context.view_layer.update()
if REV:
    print('fa long tables: REVERTED')
else:
    def mv(o): return [o.matrix_world @ v.co for v in o.data.vertices] if o.type == 'MESH' and len(o.data.vertices) else [o.matrix_world @ Vector(v) for v in o.bound_box]
    def ctr(objs):
        vs = []; [vs.extend(mv(o)) for o in objs]; return sum(vs, Vector()) / len(vs)
    def ctr1(o): bb = [o.matrix_world @ Vector(v) for v in o.bound_box]; return sum(bb, Vector()) / 8
    a = ctr1(O['dc_door0_frost']); b = ctr1(O['dc_door1_frost'])
    d = Vector((b.x - a.x, b.y - a.y, 0)).normalized(); n = Vector((d.y, -d.x, 0))
    tc0 = ctr([O['dc_table_0_top']])
    if n.dot(Vector((tc0.x - a.x, tc0.y - a.y, 0))) < 0: n = -n
    def P(t, s, z): return Vector((a.x + d.x * t + n.x * s, a.y + d.y * t + n.y * s, z))
    S_TAB = 2.60; T_TAB = (0.80, 3.00); HALF_D = 0.40; CH_OFF = 0.25; CH_T = (-0.42, 0.42)
    for k, tt in enumerate(T_TAB):
        parts = [o for o in O if o.name.startswith('dc_table_%d_' % k)]
        c = ctr(parts); tgt = P(tt, S_TAB, 0)
        Mx = Matrix.Translation(Vector((tgt.x, tgt.y, 0))) @ Matrix.Rotation(math.pi / 2, 4, 'Z') @ Matrix.Translation(Vector((-c.x, -c.y, 0)))
        for o in parts:
            o['fa_orig_mw'] = [x for row in o.matrix_world for x in row]; o.matrix_world = Mx @ o.matrix_world
            if o.hide_render: o.hide_render = False; o.display_type = 'TEXTURED'; o['fa_unhid'] = 1
    bpy.context.view_layer.update()
    src = [o for o in O if o.name.startswith('dc_side_chair_0_1_') and not o.hide_render]
    seat = next(o for o in src if 'seat' in o.name); back = next(o for o in src if 'back' in o.name)
    c0 = ctr([seat]); bdir = ctr([back]) - c0; bdir.z = 0; bdir.normalize()
    col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    nch = 0
    for k, tt in enumerate(T_TAB):
        for side in (-1, 1):
            want = n * side  # back points away from the table
            rot = math.atan2(want.y, want.x) - math.atan2(bdir.y, bdir.x)
            for dt in CH_T:
                tg = P(tt + dt, S_TAB + side * (HALF_D + CH_OFF), 0)
                Mx = Matrix.Translation(Vector((tg.x, tg.y, 0))) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Translation(Vector((-c0.x, -c0.y, 0)))
                for o in src:
                    cp = o.copy(); cp.name = 'fa_chair_t%d_%s%d_%s' % (k, 'D' if side < 0 else 'F', 0 if dt < 0 else 1, o.name.replace('dc_side_chair_0_1_', ''))
                    for c_ in list(cp.users_collection): c_.objects.unlink(cp)
                    col.objects.link(cp); cp.matrix_world = Mx @ o.matrix_world; cp['fa_long_table_chair_approx'] = 1
                nch += 1
    # one charcoal carpet field under the sofa row AND the long tables (photo 01: dark carpet over the whole middle,
    # terrazzo border); replaces dc's two 1.9 x 2.6 rugs (hidden, prop fa_rug_hidden). Extents APPROXIMATE.
    import bmesh
    M_rug = O['dc_rug_0'].active_material
    for o in O:
        if o.name.startswith('dc_rug_') and not o.hide_render: o.hide_render = True; o['fa_rug_hidden'] = 1
    T0, T1, S0, S1, Z0 = -1.00, 3.95, 1.65, 5.60, 137.400
    me = bpy.data.meshes.new('fa_carpet_field'); bm = bmesh.new()
    vs = [bm.verts.new(P(t, s_, Z0 + z)) for z in (0.0, 0.012) for (t, s_) in ((T0, S0), (T1, S0), (T1, S1), (T0, S1))]
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
    bm.to_mesh(me); bm.free(); me.materials.append(M_rug)
    cp = bpy.data.objects.new('fa_carpet_field', me); col.objects.link(cp); cp['fa_carpet_approx'] = 1
    bpy.context.view_layer.update()
    def ext(objs):
        vs = []; [vs.extend(mv(o)) for o in objs]
        S = [(v - a).dot(n) for v in vs]; T = [(v - a).dot(d) for v in vs]
        return 't %.2f..%.2f s %.2f..%.2f' % (min(T), max(T), min(S), max(S))
    print('fa long tables: chair src parts %s' % [o.name for o in src])
    for k in range(2): print('fa table %d %s' % (k, ext([o for o in O if o.name.startswith('dc_table_%d_' % k)])))
    print('fa chairs %d %s' % (nch, ext(list(col.objects))))
    print('fa neighbours: sq chairs %s; grey %s; orange %s' % (ext([o for o in O if o.name.startswith('dc_side_chair_') and not o.hide_render]),
          ext([o for o in O if o.name.startswith('dc_grey_lounge') and not o.hide_render]), ext([o for o in O if o.name.startswith('dc_orange_lounge') and not o.hide_render])))
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('fa long tables: SAVED', time.strftime('%H:%M:%S'))
