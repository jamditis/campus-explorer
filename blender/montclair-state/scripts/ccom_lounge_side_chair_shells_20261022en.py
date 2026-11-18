"""Session en (~3:35 AM ET Oct 22). MAIN, CCOM east lounge (em Next 2): the 4 visible dc side chairs (facing the sofa across
em's square tables) were 8-vertex boxes (seat slab, flat back slab, square legs). Joe's photos 01/04 show moulded
upholstered shell chairs on light wood legs. This hides the box parts (hide_render + bounds display, prop en_hidden) and
builds per chair, in the chair's own frame: a bevelled seat cushion with a slight waterfall front, a curved shell back
(arc radius 0.42 m, 8 deg recline, rounded shoulders, solidify 14 mm, subdiv 1) that runs down to the seat's rear edge,
and 4 tapered, slightly splayed wood legs. Same footprint, seat height and materials (CCOM_dc_shell_*, CCOM_dc_light_wood).
Shape generic, APPROXIMATE. Run AFTER ccom_lounge_square_tables_20261022em.py. SAVE=1 saves; REVERT=1 restores."""
import bpy, bmesh, os, time, math, re
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'
CN = 'CCOM_side_chair_shells_en'; O = bpy.data.objects
col = bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
for o in O:
    if o.get('en_hidden'):
        o.hide_render = False; o.display_type = o.get('en_disp', 'TEXTURED'); del o['en_hidden']
        if 'en_disp' in o: del o['en_disp']
bpy.context.view_layer.update()
def mctr(o): vs = [o.matrix_world @ v.co for v in o.data.vertices]; return sum(vs, Vector()) / len(vs)
if REV:
    print('en chairs: REVERTED')
else:
    groups = {}
    for o in O:
        m = re.match(r'(dc_side_chair_\d+_\d+)_', o.name)
        if m and not o.hide_render: groups.setdefault(m.group(1), []).append(o)
    col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    wood = bpy.data.materials['CCOM_dc_light_wood']
    def link(name, me, mw, mat):
        me.materials.append(mat); ob = bpy.data.objects.new(name, me); col.objects.link(ob); ob.matrix_world = mw
        ob['en_shell_chair_approx'] = 1; return ob
    n = 0
    for k, parts in sorted(groups.items()):
        seat = next(o for o in parts if o.name.endswith('_seat')); back = next(o for o in parts if o.name.endswith('_back'))
        legs = [o for o in parts if '_leg' in o.name]
        sc = mctr(seat); bc = mctr(back)
        zfl = min((l.matrix_world @ v.co).z for l in legs for v in l.data.vertices)
        zst = max((seat.matrix_world @ v.co).z for v in seat.data.vertices)
        b = bc - sc; b.z = 0; bd = b.length; b.normalize(); f = -b; r = Vector((f.y, -f.x, 0))
        # local frame: x = right, y = forward, z = up; origin seat centre on the floor
        R = Matrix(((r.x, f.x, 0, sc.x), (r.y, f.y, 0, sc.y), (0, 0, 1, zfl), (0, 0, 0, 1)))
        hs = zst - zfl; mat = seat.active_material
        # seat cushion: 0.48 x 0.46, 6 cm thick, waterfall front
        me = bpy.data.meshes.new(k + '_en_seat'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.48, 0.46, 0.06), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0.0, hs - 0.03), verts=bm.verts)
        for v in bm.verts:
            if v.co.y > 0 and v.co.z < hs - 0.03: v.co.y -= 0.02; v.co.z -= 0.012  # rolled front edge
        bm.to_mesh(me); bm.free(); ob = link(k + '_en_seat', me, R, mat)
        m = ob.modifiers.new('bev', 'BEVEL'); m.width = 0.022; m.segments = 4
        for p in me.polygons: p.use_smooth = True
        # curved shell back
        yb = -min(bd, 0.24) + 0.02; Rc = 0.42; W = 0.46; H = 0.40; NU, NV = 14, 10; rec = math.radians(8)
        me = bpy.data.meshes.new(k + '_en_back'); bm = bmesh.new(); grid = []
        for j in range(NV + 1):
            v = j / NV; z = hs - 0.01 + v * H
            wf = 1.0 if v < 0.6 else math.sqrt(max(0.0, 1 - ((v - 0.6) / 0.4) ** 2)) * 0.25 + 0.75  # rounded shoulders
            wf = wf * (0.94 + 0.06 * v)  # slight flare up the back
            row = []
            for i in range(NU + 1):
                u = (i / NU - 0.5) * W * wf; ph = u / Rc
                x = Rc * math.sin(ph); y = yb + Rc * (1 - math.cos(ph)) - math.tan(rec) * (z - hs)
                row.append(bm.verts.new((x, y, z)))
            grid.append(row)
        for j in range(NV):
            for i in range(NU): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        bm.normal_update(); bm.to_mesh(me); bm.free(); ob = link(k + '_en_back', me, R, mat)
        s = ob.modifiers.new('sol', 'SOLIDIFY'); s.thickness = 0.014; s.offset = -1
        sd = ob.modifiers.new('sub', 'SUBSURF'); sd.levels = sd.render_levels = 1
        for p in me.polygons: p.use_smooth = True
        # tapered splayed legs from the original leg feet
        for l in legs:
            lc = mctr(l); lx = (lc - sc).dot(r); ly = (lc - sc).dot(f)
            sp = math.radians(5); hl = hs - 0.06
            me = bpy.data.meshes.new(l.name + '_en'); bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.011, radius2=0.017, depth=hl)
            bmesh.ops.translate(bm, vec=(0, 0, hl / 2), verts=bm.verts)
            # splay: feet outward from the seat centre
            ax = Vector((lx, ly, 0)).normalized(); top_off = ax * (-math.tan(sp) * hl)
            for v in bm.verts: t = v.co.z / hl; v.co.x += top_off.x * t; v.co.y += top_off.y * t
            bmesh.ops.translate(bm, vec=(lx, ly, 0), verts=bm.verts)
            bm.to_mesh(me); bm.free(); ob = link(l.name + '_en', me, R, wood)
            for p in me.polygons: p.use_smooth = True
        for o in parts:
            o['en_disp'] = o.display_type; o.hide_render = True; o.display_type = 'BOUNDS'; o['en_hidden'] = 1
        n += 1
        print('en chairs: %s seat h %.3f back dist %.3f mat %s' % (k, hs, bd, mat.name))
    print('en chairs: rebuilt %d chairs' % n)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('en chairs: SAVED', time.strftime('%H:%M:%S'))
