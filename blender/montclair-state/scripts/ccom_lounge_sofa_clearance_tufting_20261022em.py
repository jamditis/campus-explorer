"""Session em (~2:35 AM ET Oct 22). MAIN, CCOM east lounge (follows el sofa):
(1) clearance: el's round window tables (dV_round_table_*) poked 0.15 m into the sofa back and the blue window lounge
chairs sat ~0.0-0.4 m behind it. Window group (dc_blue_lounge_*, dV_blue_chair_*, dV_round_table_*) moved +DW (0.20 m)
toward the glass (chair max stays 2 cm short of the sill ledge); the el sofa moved -DS (0.12 m) toward the white tables.
(2) detail: sofa back cushion split into 3 cushions (22 mm gaps) with 2x3 deep buttons each, seat split into 3 cushions,
wood end shells given rounded corners (bevel 5 cm, 5 segments). Original el parts hidden (prop em_hidden).
Positions/tufting APPROXIMATE (photos 01/04 show a tufted chevron banquette; exact button count UNVERIFIED).
Idempotent via em_orig_mw; SAVE=1 saves; REVERT=1 restores."""
import bpy, os, time
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'
DW = float(os.environ.get('DW', '0.20')); DS = float(os.environ.get('DS', '0.12'))
CN = 'CCOM_sofa_detail_em'; O = bpy.data.objects
col = bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
for o in O:
    if 'em_orig_mw' in o:
        o.matrix_world = Matrix([o['em_orig_mw'][i*4:i*4+4] for i in range(4)]); del o['em_orig_mw']
    if o.get('em_hidden'):
        o.hide_render = o.hide_viewport = False; del o['em_hidden']
    if o.name.startswith('el_sofa_woodshell_end') and 'em_bev' in o:
        md = o.modifiers.get('bev')
        if md: md.width, md.segments = o['em_bev']
        del o['em_bev']
if REV:
    print('em sofa: REVERTED')
else:
    def ctr(o): bb = [o.matrix_world @ Vector(v) for v in o.bound_box]; return sum(bb, Vector()) / 8
    a = ctr(O['dc_door0_frost']); b = ctr(O['dc_door1_frost'])
    d = Vector((b.x - a.x, b.y - a.y, 0)).normalized(); n = Vector((d.y, -d.x, 0))
    _tb = O['dc_table_0_top']; _tc = sum((_tb.matrix_world @ v.co for v in _tb.data.vertices), Vector()) / len(_tb.data.vertices)  # mesh data, not bound_box (zero when hidden)
    if n.dot(Vector((_tc.x - a.x, _tc.y - a.y, 0))) < 0: n = -n
    def move(o, v):
        o['em_orig_mw'] = [x for row in o.matrix_world for x in row]
        o.matrix_world = Matrix.Translation(v) @ o.matrix_world
    sel = [o for o in O if o.name.startswith(('dc_blue_lounge_', 'dV_blue_chair_', 'dV_round_table_'))]
    sel = [o for o in sel if not (o.parent and o.parent in sel)]
    for o in sel: move(o, n * DW)
    sofa = [o for o in O if o.name.startswith('el_sofa_') and not (o.parent and o.parent.name.startswith('el_sofa_'))]
    for o in sofa: move(o, -n * DS)
    bpy.context.view_layer.update()
    print('em sofa: moved %d window-group objs +%.2f, %d sofa objs -%.2f' % (len(sel), DW, len(sofa), DS))
    col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    btn = bpy.data.materials.get('em_sofa_button') or bpy.data.materials.new('em_sofa_button')
    btn.use_nodes = True; bs = btn.node_tree.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (0.035, 0.055, 0.11, 1); bs.inputs['Roughness'].default_value = 0.7
    def split(src, k, gap, buttons=False):
        lx = (max(v.co.x for v in src.data.vertices) - min(v.co.x for v in src.data.vertices))
        ly = (max(v.co.y for v in src.data.vertices) - min(v.co.y for v in src.data.vertices))
        lz = (max(v.co.z for v in src.data.vertices) - min(v.co.z for v in src.data.vertices))
        w = (lx - gap * (k - 1)) / k; out = []
        R = src.matrix_world.to_3x3().normalized()
        for i in range(k):
            o = src.copy(); o.data = src.data.copy(); o.name = src.name + '_em%d' % i
            for v in o.data.vertices: v.co.x *= w / lx
            off = -lx / 2 + w / 2 + i * (w + gap)
            o.matrix_world = Matrix.Translation(R @ Vector((off, 0, 0))) @ src.matrix_world
            md = o.modifiers.get('bev')
            if md: md.width = max(md.width, 0.045); md.segments = 4
            for c in o.users_collection: c.objects.unlink(o)
            col.objects.link(o); o['em_sofa_unverified'] = 1; out.append(o)
            if buttons:
                # front face = side facing the tables = -n in world; local y sign
                fy = (R.inverted() @ (-n)).y; sy = 1 if fy > 0 else -1
                for r in (0.30, 0.70):
                    for c3 in (0.2, 0.5, 0.8):
                        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.017)
                        s = bpy.context.active_object; s.name = 'em_sofa_button'
                        for cc in s.users_collection: cc.objects.unlink(s)
                        col.objects.link(s); s.data.materials.append(btn)
                        loc = Vector((off - w / 2 + w * c3, sy * (ly / 2 - 0.004), -lz / 2 + lz * r))
                        s.matrix_world = Matrix.Translation(src.matrix_world @ loc)
                        s.scale = (1, 1, 0.8)
        src.hide_render = src.hide_viewport = True; src['em_hidden'] = 1
        return out
    bc = split(O['el_sofa_backcushion'], 3, 0.022, buttons=True)
    sc = split(O['el_sofa_seat'], 3, 0.018)
    for nm in ('el_sofa_woodshell_endL', 'el_sofa_woodshell_endR'):
        o = O.get(nm)
        if o and o.modifiers.get('bev'):
            md = o.modifiers['bev']; o['em_bev'] = (md.width, md.segments); md.width = 0.05; md.segments = 5; md.limit_method = 'NONE'
    nb = sum(1 for o in col.objects if o.name.startswith('em_sofa_button'))
    print('em sofa: %d back + %d seat cushions, %d buttons' % (len(bc), len(sc), nb))
    # clearance report
    def ext(pre, hidden_ok=False):
        ss = []
        for o in O:
            if o.name.startswith(pre) and not o.hide_render:
                ss += [(o.matrix_world @ Vector(v) - a).dot(n) for v in o.bound_box]
        return (min(ss), max(ss)) if ss else None
    print('em sofa: s-extents sofa %s, cushions %s, chairs %s, round tables %s, sill ledge %s' % tuple(
        tuple(round(x, 2) for x in (ext(p) or (0, 0))) for p in ('el_sofa_', 'el_sofa_backcushion_em', 'dc_blue_lounge_', 'dV_round_table_', 'CCOM_lounge_sill_ledge')))
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('em sofa: SAVED', time.strftime('%H:%M:%S'))
