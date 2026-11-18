"""2026-10-21 session dV (~10:45 AM ET). Joe's photo 02 (and CCOM's own X photo refs/ccom_x/02) show two small ROUND white
pedestal tables (chrome stem + round chrome foot) among the blue high-back chairs at CCOM's east lounge window, and a white
duplex outlet plate in the sill wall under the glass. dc had the blue chairs but no round tables -> add 2 tables (top dia 0.56 m,
top at floor+0.56 m; sizes photo-scaled from the chairs, UNVERIFIED +/-0.1 m) between chair pairs 0/1 and 2/3, pulled 0.3 m into
the room, and one outlet plate (0.07 x 0.115 m) 0.30 m above the floor on the sill wall's inner face (found by ray), near table 2.
Photo 02 / X 02 also show the blue chairs on CHROME 4-star swivel bases (dc gave them 4 wood legs) -> the 16 dc wood legs
are hidden (prop dV_hidden_leg; REVERT shows them again) and each chair gets a chrome stem + 4-arm star foot.
Collection CCOM_east_window_tables_dV (child of the dc collection); idempotent (rebuilt each run); REVERT=1 removes; SAVE=1 saves."""
import bpy, bmesh, os, math
from mathutils import Vector, Matrix
CN = 'CCOM_east_window_tables_dV'
if CN in bpy.data.collections:
    C = bpy.data.collections[CN]
    for o in list(C.objects): me = o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    bpy.data.collections.remove(C)
for o in bpy.data.objects:
    if o.get('dV_hidden_leg'): o.hide_render = False; o.hide_viewport = False; del o['dV_hidden_leg']
if os.environ.get('REVERT') == '1': print('DVTAB reverted', flush=True)
else:
    P0 = bpy.data.collections['CCOM_east_interior_joe_20261020dc']
    C = bpy.data.collections.new(CN); P0.children.link(C)
    M = bpy.data.materials; white = M['CCOM_dc_table_white']; chrome = M['CCOM_dc_chrome']; grey = M['CCOM_dc_base_grey']
    FZ = 134.85
    def cyl(name, x, y, z0, z1, r, mat, seg=32):
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0)
        bm.transform(Matrix.Translation((x, y, (z0 + z1) / 2))); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        me.materials.append(mat); ob = bpy.data.objects.new(name, me); C.objects.link(ob); return ob
    def cen(n):
        objs = [o for o in bpy.data.objects if o.name.startswith(n)]
        P = [o.matrix_world @ Vector(b) for o in objs for b in o.bound_box]; return sum(P, Vector()) / len(P)
    ch = [cen('dc_blue_lounge_%d_' % i) for i in range(4)]
    g = bpy.data.objects['CCOM_lounge_east_glass_20261014jf']; G = [g.matrix_world @ Vector(b) for b in g.bound_box]
    gmin = min(G, key=lambda p: p.y); gmax = max(G, key=lambda p: p.y)
    tan = (gmax - gmin).to_2d().normalized(); nrm = Vector((tan.y, -tan.x))            # +nrm = outward (east)
    made = []
    for k, (i, j) in enumerate(((0, 1), (2, 3))):
        m = ((ch[i] + ch[j]) / 2).to_2d() - nrm * 0.30
        cyl('dV_round_table_%d_top' % k, m.x, m.y, FZ + 0.535, FZ + 0.56, 0.28, white)
        cyl('dV_round_table_%d_stem' % k, m.x, m.y, FZ + 0.02, FZ + 0.535, 0.028, chrome, 16)
        cyl('dV_round_table_%d_foot' % k, m.x, m.y, FZ + 0.002, FZ + 0.02, 0.21, chrome)
        made.append((round(m.x, 2), round(m.y, 2)))
    for i, c in enumerate(ch):
        for o in bpy.data.objects:
            if o.name.startswith('dc_blue_lounge_%d_leg' % i): o.hide_render = True; o.hide_viewport = True; o['dV_hidden_leg'] = 1
        cyl('dV_blue_chair_%d_stem' % i, c.x, c.y, FZ + 0.03, FZ + 0.33, 0.03, chrome, 16)
        for a in range(4):
            ang = math.radians(45 + 90 * a + 15 * i)
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
            bm.transform(Matrix.Translation((c.x, c.y, FZ + 0.025)) @ Matrix.Rotation(ang, 4, 'Z') @ Matrix.Translation((0.17, 0, 0)) @ Matrix.Diagonal((0.34, 0.035, 0.03, 1)))
            me = bpy.data.meshes.new('dV_blue_chair_%d_star_%d' % (i, a)); bm.to_mesh(me); bm.free(); me.materials.append(chrome)
            C.objects.link(bpy.data.objects.new(me.name, me))
    # outlet on the sill wall inner face, near table 1
    dg = bpy.context.evaluated_depsgraph_get(); scn = bpy.context.scene
    m = ((ch[2] + ch[3]) / 2).to_2d() + tan * 0.45
    org = Vector((m.x, m.y, FZ + 0.30)) - nrm.to_3d() * 1.5; dv = nrm.to_3d(); hitp = None
    for _ in range(10):
        h, loc, no, idx, ob, mt = scn.ray_cast(dg, org, dv, distance=4)
        if not h: break
        if ob.name.startswith('dc_blue') or ob.name.startswith('dV_') or ob.name.startswith('Terrain') or 'grass' in ob.name.lower(): org = loc + dv * 1e-3; continue
        hitp = (loc, ob.name); break
    if hitp:
        loc = hitp[0] - dv * 0.004
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
        R = Matrix(((tan.x, -nrm.x, 0), (tan.y, -nrm.y, 0), (0, 0, 1))).to_4x4()
        bm.transform(Matrix.Translation(loc) @ R @ Matrix.Diagonal((0.07, 0.006, 0.115, 1)))
        me = bpy.data.meshes.new('dV_sill_outlet_plate'); bm.to_mesh(me); bm.free(); me.materials.append(white)
        C.objects.link(bpy.data.objects.new(me.name, me))
        for s, dz in ((0, 0.022), (1, -0.022)):
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
            bm.transform(Matrix.Translation(loc - dv * 0.004 + Vector((0, 0, dz))) @ R @ Matrix.Diagonal((0.034, 0.004, 0.026, 1)))
            me = bpy.data.meshes.new('dV_sill_outlet_recept_%d' % s); bm.to_mesh(me); bm.free(); me.materials.append(grey)
            C.objects.link(bpy.data.objects.new(me.name, me))
    print('DVTAB tables', made, 'outlet', None if not hitp else (tuple(round(c, 2) for c in hitp[0]), hitp[1]), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DVTAB_SAVED', flush=True)
