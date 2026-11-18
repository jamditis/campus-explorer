"""Session en (~3:40 AM ET Oct 22). MAIN, CCOM east lounge window: the 4 blue lounge chairs (dc_blue_lounge_*) were box
seat/back/arm slabs on dV's chrome swivel stems. Joe's photos 01/02 show moulded blue tub/egg shell chairs: a high
rounded back that sweeps down to low arms at the front, on a chrome stem with a 4-star base. This hides the box parts
(hide_render + bounds display, prop en2_hidden) and builds per chair, in its own frame (back direction from the old back
slab): one moulded shell (theta +-160 deg, rim height 0.25 m at the arms to 0.70 m at the back above the stem top,
tucked tub profile, solidify 16 mm + subdiv 1), a bottom cap and an oval seat cushion. Stems/bases (dV) unchanged.
Proportions by eye from the photos; APPROXIMATE. SAVE=1 saves; REVERT=1 restores."""
import bpy, bmesh, os, time, math, re
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'
CN = 'CCOM_blue_egg_chairs_en'; O = bpy.data.objects
col = bpy.data.collections.get(CN)
if col:
    for o in list(col.objects): bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(col)
for o in O:
    if o.get('en2_hidden'):
        o.hide_render = False; o.display_type = o.get('en2_disp', 'TEXTURED'); del o['en2_hidden']
        if 'en2_disp' in o: del o['en2_disp']
bpy.context.view_layer.update()
def mctr(o): vs = [o.matrix_world @ v.co for v in o.data.vertices]; return sum(vs, Vector()) / len(vs)
if REV:
    print('en egg: REVERTED')
else:
    groups = {}
    for o in O:
        m = re.match(r'(dc_blue_lounge_\d+)_', o.name)
        if m and not o.hide_render and o.type == 'MESH': groups.setdefault(m.group(1), []).append(o)
    col = bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    def link(name, me, mw, mat):
        me.materials.append(mat); ob = bpy.data.objects.new(name, me); col.objects.link(ob); ob.matrix_world = mw
        ob['en_egg_chair_approx'] = 1
        for p in me.polygons: p.use_smooth = True
        return ob
    n = 0
    for k, parts in sorted(groups.items()):
        seat = next(o for o in parts if o.name.endswith('_seat')); back = next(o for o in parts if o.name.endswith('_back'))
        mat = seat.active_material
        sc = mctr(seat); bc = mctr(back); b = bc - sc; b.z = 0; b.normalize(); f = -b; r = Vector((f.y, -f.x, 0))
        zb = min((seat.matrix_world @ v.co).z for v in seat.data.vertices)  # = stem top
        R = Matrix(((r.x, f.x, 0, sc.x), (r.y, f.y, 0, sc.y), (0, 0, 1, zb), (0, 0, 0, 1)))
        RX, RY = 0.36, 0.33; NT, NV = 36, 12; me = bpy.data.meshes.new(k + '_en_shell'); bm = bmesh.new(); grid = []
        for j in range(NV + 1):
            v = j / NV; row = []
            for i in range(NT + 1):
                th = math.radians(-160 + 320 * i / NT)
                H = 0.25 + 0.45 * ((1 + math.cos(th)) / 2) ** 1.5
                rho = 0.58 + 0.42 * math.sin(min(1.0, v / 0.5) * math.pi / 2)
                rho *= 1.0 - 0.04 * max(0.0, v - 0.7) / 0.3 * ((1 + math.cos(th)) / 2)  # slight inward roll at the back rim
                x = RX * rho * math.sin(th); y = -RY * rho * math.cos(th) + 0.03; z = v * H
                row.append(bm.verts.new((x, y, z)))
            grid.append(row)
        for j in range(NV):
            for i in range(NT): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
        # close the front lip under the seat: fan from the bottom ring
        bm.normal_update()
        for fc in bm.faces:
            c = fc.calc_center_median()
            if fc.normal.dot(Vector((c.x, c.y - 0.03, 0))) < 0: fc.normal_flip()
        bm.to_mesh(me); bm.free(); ob = link(k + '_en_shell', me, R, mat)
        s = ob.modifiers.new('sol', 'SOLIDIFY'); s.thickness = 0.016; s.offset = -1
        sd = ob.modifiers.new('sub', 'SUBSURF'); sd.levels = sd.render_levels = 1
        # bottom cap (oval) at the shell base
        me = bpy.data.meshes.new(k + '_en_base'); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=36, radius1=1.0, radius2=1.0, depth=0.02)
        bmesh.ops.scale(bm, vec=(RX * 0.58, RY * 0.58, 1), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0.03, 0.01), verts=bm.verts)
        bm.to_mesh(me); bm.free(); link(k + '_en_base', me, R, mat)
        # oval seat cushion
        me = bpy.data.meshes.new(k + '_en_cushion'); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=36, radius1=1.0, radius2=1.0, depth=0.06)
        bmesh.ops.scale(bm, vec=(0.29, 0.27, 1), verts=bm.verts); bmesh.ops.translate(bm, vec=(0, 0.06, 0.11), verts=bm.verts)
        bm.to_mesh(me); bm.free(); ob = link(k + '_en_cushion', me, R, mat)
        m = ob.modifiers.new('bev', 'BEVEL'); m.width = 0.02; m.segments = 3
        for o in parts:
            o['en2_disp'] = o.display_type; o.hide_render = True; o.display_type = 'BOUNDS'; o['en2_hidden'] = 1
        n += 1; print('en egg: %s stem top %.3f facing (%.2f, %.2f)' % (k, zb, f.x, f.y))
    print('en egg: rebuilt %d chairs' % n)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('en egg: SAVED', time.strftime('%H:%M:%S'))
