"""Session el (~1:35 AM ET Oct 22). MAIN: blue chevron sofa in the CCOM east lounge (dispatcher 9:56 PM Oct 21, from Joe's photos 01/04):
runs along (parallel to) the wall with the maroon-framed frosted doors, facing the row of white tables, on their far side from that wall.
Placement APPROXIMATE / UNVERIFIED. Hides (not deletes) the old short dc_chevron_bench parts and the far-side side chairs the sofa replaces.
SAVE=1 saves; REVERT=1 removes the sofa and unhides."""
import bpy, os, time, math
from mathutils import Vector, Matrix
rev = os.environ.get('REVERT') == '1'
CN = 'CCOM_chevron_sofa_el'
col = bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
for o in bpy.data.objects:
    if o.get('el_hidden'):
        o.hide_render = o.hide_viewport = False; del o['el_hidden']
if rev:
    if col: bpy.data.collections.remove(col)
    print('el sofa: REVERTED')
else:
    O = bpy.data.objects
    def ctr(n):
        o = O[n]; bb = [o.matrix_world @ Vector(v) for v in o.bound_box]; return sum(bb, Vector()) / 8
    # door wall line from the two dc door frost panels
    a = ctr('dc_door0_frost'); b = ctr('dc_door1_frost')
    d = Vector((b.x - a.x, b.y - a.y, 0)).normalized()
    n = Vector((d.y, -d.x, 0))
    if n.dot(Vector((ctr('dc_table_0_top').x - a.x, ctr('dc_table_0_top').y - a.y, 0))) < 0: n = -n
    def uv(p): q = Vector((p.x - a.x, p.y - a.y, 0)); return q.dot(d), q.dot(n)
    # tables' far edge (offset from the wall) and along-wall span
    offs = []; ts = []
    for tn in ('dc_table_0_top', 'dc_table_1_top'):
        o = O[tn]
        for v in o.data.vertices:
            p = o.matrix_world @ v.co; t, s = uv(p); offs.append(s); ts.append(t)
    far = max(offs); tc = [uv(ctr(x))[1] for x in ('dc_table_0_top', 'dc_table_1_top')]
    t0, t1 = min(ts) - 0.45, max(ts) + 0.45
    print('el sofa: table far edge %.2f m from door wall, span t %.2f..%.2f (%.2f m)' % (far, t0, t1, t1 - t0))
    # hide old short bench + chairs on the far side of the tables
    hid = []
    for o in O:
        nm = o.name
        if nm.startswith('dc_chevron_bench_') or (nm.startswith('dc_side_chair_') and uv(ctr(nm))[1] > sum(tc) / 2 + 0.2):
            o.hide_render = o.hide_viewport = True; o['el_hidden'] = 1; hid.append(nm)
    # also hide chair legs belonging to hidden chairs (same name prefix)
    pre = set(h.rsplit('_', 1)[0] for h in hid if h.startswith('dc_side_chair_'))
    for o in O:
        if o.name.startswith('dc_side_chair_') and o.name.rsplit('_', 1)[0] in pre and not o.get('el_hidden'):
            o.hide_render = o.hide_viewport = True; o['el_hidden'] = 1; hid.append(o.name)
    print('el sofa: hid', len(hid), sorted(hid))
    col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    M_chev = O['dc_chevron_bench_seat'].active_material
    M_wood = O['dc_chevron_bench_woodback'].active_material
    M_chr = bpy.data.materials.get('dd_chrome') or bpy.data.materials.get('dc_chrome') or next((m for m in bpy.data.materials if 'chrom' in m.name.lower()), None)
    Z0 = O['dc_rug_0'].matrix_world.translation.z if False else max((O['dc_rug_0'].matrix_world @ Vector(v)).z for v in O['dc_rug_0'].bound_box)
    s_front = far + 0.28; DEP = 0.80; L = t1 - t0
    ang = math.atan2(d.y, d.x)
    def box(name, t, s, z, lx, ly, lz, mat, bev=0.0):
        import bmesh
        me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(lx, ly, lz), verts=bm.verts); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(name, me); col.objects.link(ob)
        p = a + d * t + n * s; ob.location = (p.x, p.y, z); ob.rotation_euler = (0, 0, ang)
        if mat: me.materials.append(mat)
        if bev:
            m = ob.modifiers.new('bev', 'BEVEL'); m.width = bev; m.segments = 3; m.limit_method = 'ANGLE'
        for poly in me.polygons: poly.use_smooth = True
        ob['el_sofa_unverified'] = 1; return ob
    tm = (t0 + t1) / 2
    # y-axis local = wall normal (rotation by ang maps local x -> d, local y -> d rotated +90; fix sign)
    sgn = 1 if Vector((-d.y, d.x, 0)).dot(n) > 0 else -1
    def S(s): return s  # offsets measured along n
    def B(name, t, s, z, lx, ldep, lz, mat, bev=0.0):
        return box(name, t, s, z, lx, ldep, lz, mat, bev)
    B('el_sofa_seat', tm, s_front + 0.30, Z0 + 0.36, L, 0.60, 0.16, M_chev, 0.03)
    B('el_sofa_base', tm, s_front + 0.34, Z0 + 0.20, L - 0.10, 0.56, 0.16, M_chev, 0.02)
    B('el_sofa_backcushion', tm, s_front + 0.67, Z0 + 0.68, L - 0.04, 0.22, 0.48, M_chev, 0.04)
    B('el_sofa_woodshell_back', tm, s_front + DEP - 0.015, Z0 + 0.34, L + 0.02, 0.025, 0.56, M_wood, 0.008)
    B('el_sofa_woodshell_endL', t0 - 0.01, s_front + 0.40, Z0 + 0.48, 0.025, 0.80, 0.80, M_wood, 0.008)
    B('el_sofa_woodshell_endR', t1 + 0.01, s_front + 0.40, Z0 + 0.48, 0.025, 0.80, 0.80, M_wood, 0.008)
    nleg = max(2, int(L / 1.4) + 1)
    for i in range(nleg):
        t = t0 + 0.12 + (L - 0.24) * i / (nleg - 1)
        for s in (s_front + 0.10, s_front + DEP - 0.10):
            B('el_sofa_leg', t, s, Z0 + 0.06, 0.025, 0.025, 0.12, M_chr)
    print('el sofa: built %d parts, L %.2f m, front %.2f m from wall, floor z %.3f, mats %s/%s/%s' % (len(col.objects), L, s_front, Z0,
          M_chev.name if M_chev else None, M_wood.name if M_wood else None, M_chr.name if M_chr else None))
    # clearance check vs other rendered objects' bboxes near the sofa footprint
    fp = [a + d * t + n * s for t in (t0, t1) for s in (s_front, s_front + DEP)]
    xs = [p.x for p in fp]; ys = [p.y for p in fp]
    hits = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render or o.name in col.objects or o.name.startswith('dc_rug'): continue
        bb = [o.matrix_world @ Vector(v) for v in o.bound_box]
        if max(v.z for v in bb) < Z0 + 0.05 or min(v.z for v in bb) > Z0 + 1.0: continue
        cx = sum(v.x for v in bb)/8; cy = sum(v.y for v in bb)/8
        if min(xs) < cx < max(xs) and min(ys) < cy < max(ys):
            t, s = uv(Vector((cx, cy, 0)))
            if t0 < t < t1 and s_front < s < s_front + DEP: hits.append(o.name)
    print('el sofa: objects centred inside footprint:', hits[:30])
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('el sofa: SAVED', time.strftime('%H:%M:%S'))
