"""2026-10-20 session dc (~3:21-4:03 PM ET). CCOM 1st-floor EAST lounge interior per Joe's 5 photos (3:17 PM ET).
Purpose: what is VISIBLE THROUGH the east lounge glazing (not a full interior).
Run on MAIN:  SAVE=1 blender -b montclair_state.blend --python scripts/ccom_east_interior_joe_20261020dc.py
Idempotent: deletes its own collection, restores everything it hid / re-materialled (props dc_hidden / dc_orig_mat), then rebuilds.
Sizes/positions photo-scaled = UNVERIFIED. Room shell (glass line, walls, floor 134.85, ceiling 142.62) is the existing jf/al geometry.
"""
import bpy, bmesh, os, math
from mathutils import Vector
TAG = '20261020dc'; CN = 'CCOM_east_interior_joe_20261020dc'
sc = bpy.context.scene
# ---------------- restore previous run ----------------
old = bpy.data.collections.get(CN)
if old:
    for o in list(old.all_objects):
        me = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and getattr(me, 'users', 1) == 0:
            (bpy.data.meshes if isinstance(me, bpy.types.Mesh) else bpy.data.lights).remove(me)
    bpy.data.collections.remove(old)
for o in bpy.data.objects:
    if o.get('dc_hidden'):
        o.hide_render = bool(o.get('dc_orig_hr', 0)); o.hide_viewport = bool(o.get('dc_orig_hv', 0)); del o['dc_hidden']
    if o.get('dc_orig_mat') is not None:
        m = bpy.data.materials.get(o['dc_orig_mat'])
        if m: o.data.materials[0] = m
        del o['dc_orig_mat']
col = bpy.data.collections.new(CN); sc.collection.children.link(col)
# ---------------- room frame (MEASURED from existing geometry) ----------------
A = Vector((23.45, -24.78)); Nend = Vector((25.0, -18.76))
D = (Nend - A).normalized(); NI = Vector((-D.y, D.x))  # inward (west-ish)
if NI.x > 0: NI = -NI
Z0, ZC = 134.85, 142.62
def W(u, v, z): p = A + D * u + NI * v; return Vector((p.x, p.y, z))
def ray(o, origin, direc):
    mi = o.matrix_world.inverted(); ok, loc, nor, idx = o.ray_cast(mi @ origin, (mi.to_3x3() @ direc).normalized())
    return (o.matrix_world @ loc - origin).length if ok else None
ob = bpy.data.objects
mid = W(3.1, 3.0, 136.0)
vW = 3.0 + (ray(ob['CCOM_lounge_east_wallW_20261014jf'], mid, Vector((NI.x, NI.y, 0))) or 4.3)
uN = 3.1 + (ray(ob['CCOM_lounge_east_wallN_20261014jf'], mid, Vector((D.x, D.y, 0))) or 3.0)
uS = 3.1 - (ray(ob['CCOM_lounge_east_wallS_20261014jf'], mid, Vector((-D.x, -D.y, 0))) or 3.1)
gl = ray(ob['CCOM_lounge_east_glass_20261014jf'], mid, Vector((-NI.x, -NI.y, 0)))
v0 = 3.0 - gl if gl else 0.0
print('DC_ROOM vW %.3f uS %.3f uN %.3f glass_v %.3f' % (vW, uS, uN, v0), flush=True)
ANG = math.atan2(D.y, D.x)
# ---------------- materials ----------------
def mat(name, col_, rough=0.5, metal=0.0, emit=None, es=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col_, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = es
    return m
M_white = mat('CCOM_dc_wall_white', (0.80, 0.80, 0.78), 0.6)
M_base = mat('CCOM_dc_base_grey', (0.22, 0.22, 0.23), 0.5)
M_tz = mat('CCOM_dc_terrazzo', (0.66, 0.64, 0.60), 0.14)
t = M_tz.node_tree; vn = t.nodes.new('ShaderNodeTexVoronoi'); vn.inputs['Scale'].default_value = 140
cr = t.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (0.42, 0.40, 0.38, 1)
cr.color_ramp.elements[1].position = 0.18; cr.color_ramp.elements[1].color = (0.68, 0.66, 0.62, 1)
t.links.new(vn.outputs['Distance'], cr.inputs['Fac']); t.links.new(cr.outputs['Color'], t.nodes['Principled BSDF'].inputs['Base Color'])
M_tile = mat('CCOM_dc_ceiling_tile', (0.82, 0.82, 0.80), 0.85)
t = M_tile.node_tree; tc = t.nodes.new('ShaderNodeTexCoord'); bk = t.nodes.new('ShaderNodeTexBrick')
bk.offset = 0.0; bk.inputs['Scale'].default_value = 1.0; bk.inputs['Brick Width'].default_value = 0.61; bk.inputs['Row Height'].default_value = 0.61
bk.inputs['Mortar Size'].default_value = 0.012; bk.inputs['Color1'].default_value = (0.82, 0.82, 0.80, 1); bk.inputs['Color2'].default_value = (0.79, 0.79, 0.77, 1)
bk.inputs['Mortar'].default_value = (0.60, 0.60, 0.60, 1)
t.links.new(tc.outputs['Object'], bk.inputs['Vector']); t.links.new(bk.outputs['Color'], t.nodes['Principled BSDF'].inputs['Base Color'])
M_led = mat('CCOM_dc_linear_led', (0.95, 0.95, 0.95), 0.4, emit=(1.0, 0.96, 0.90), es=float(os.environ.get('LED', '6.0')))
M_slot = mat('CCOM_dc_slot_diffuser', (0.05, 0.05, 0.055), 0.7)
M_rug = mat('CCOM_dc_rug_charcoal', (0.035, 0.037, 0.04), 0.95)
M_tab = mat('CCOM_dc_table_white', (0.85, 0.85, 0.84), 0.25)
M_chr = mat('CCOM_dc_chrome', (0.8, 0.8, 0.8), 0.15, 1.0)
M_blue = mat('CCOM_dc_shell_blue', (0.03, 0.13, 0.42), 0.45)
M_sage = mat('CCOM_dc_shell_sage', (0.33, 0.37, 0.33), 0.5)
M_grey = mat('CCOM_dc_shell_grey', (0.30, 0.30, 0.31), 0.6)
M_orng = mat('CCOM_dc_lounge_orange', (0.75, 0.22, 0.04), 0.7)
M_wood = mat('CCOM_dc_light_wood', (0.55, 0.38, 0.20), 0.5)
M_mar = bpy.data.materials.get('CCOM_maroon_frame_20261014jf') or mat('CCOM_dc_maroon', (0.18, 0.03, 0.03), 0.4)
M_frost = mat('CCOM_dc_frosted_glass', (0.78, 0.80, 0.81), 0.35)
M_dkgl = mat('CCOM_dc_interior_glass_dark', (0.06, 0.07, 0.08), 0.08)
M_rail = mat('CCOM_dc_balcony_glass', (0.6, 0.66, 0.66), 0.05); M_rail.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.9
M_chev = mat('CCOM_dc_chevron', (0.5, 0.5, 0.5), 0.8)
t = M_chev.node_tree; tc = t.nodes.new('ShaderNodeTexCoord'); sx = t.nodes.new('ShaderNodeSeparateXYZ'); t.links.new(tc.outputs['Object'], sx.inputs[0])
m1 = t.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = 6.0; t.links.new(sx.outputs['Z'], m1.inputs[0])
m2 = t.nodes.new('ShaderNodeMath'); m2.operation = 'PINGPONG'; m2.inputs[1].default_value = 0.5; t.links.new(m1.outputs[0], m2.inputs[0])
m3 = t.nodes.new('ShaderNodeMath'); m3.operation = 'MULTIPLY_ADD'; m3.inputs[1].default_value = 1.0; t.links.new(m2.outputs[0], m3.inputs[0])
m4 = t.nodes.new('ShaderNodeMath'); m4.operation = 'MULTIPLY'; m4.inputs[1].default_value = 7.0; t.links.new(sx.outputs['X'], m4.inputs[0]); t.links.new(m4.outputs[0], m3.inputs[2])
m5 = t.nodes.new('ShaderNodeMath'); m5.operation = 'FRACT'; t.links.new(m3.outputs[0], m5.inputs[0])
cr = t.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'
cr.color_ramp.elements[0].color = (0.05, 0.16, 0.42, 1); cr.color_ramp.elements[1].position = 0.34; cr.color_ramp.elements[1].color = (0.80, 0.80, 0.78, 1)
e = cr.color_ramp.elements.new(0.67); e.color = (0.32, 0.33, 0.35, 1)
t.links.new(m5.outputs[0], cr.inputs['Fac']); t.links.new(cr.outputs['Color'], t.nodes['Principled BSDF'].inputs['Base Color'])
M_ss = mat('CCOM_dc_stainless', (0.7, 0.7, 0.7), 0.3, 1.0)
# ---------------- builders ----------------
def box(name, u0, u1, v0_, v1, z0, z1, m, rot=None, center=None):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); me.materials.append(m)
    o.scale = (abs(u1 - u0), abs(v1 - v0_), abs(z1 - z0))
    c = W((u0 + u1) / 2, (v0_ + v1) / 2, (z0 + z1) / 2) if center is None else center
    o.location = c; o.rotation_euler = (0, 0, ANG if rot is None else rot)
    o['dc_unverified'] = 1; return o
def cyl(name, u, v, z0, z1, r, m, seg=24):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1 - z0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); me.materials.append(m); o.location = W(u, v, (z0 + z1) / 2); return o
def lbox(name, cu, cv, du, dv, z0, z1, m, yaw):
    """box centred at (cu,cv) in room coords, size du x dv, rotated yaw (rad) relative to room axes"""
    o = box(name, 0, du, 0, dv, z0, z1, m, rot=ANG + yaw, center=W(cu, cv, (z0 + z1) / 2)); return o
def offs(cu, cv, yaw, a, b):
    ca, sa = math.cos(yaw), math.sin(yaw); return cu + a * ca - b * sa, cv + a * sa + b * ca
# ---------------- hide what Joe's photos contradict / what we replace ----------------
def hide(o):
    if o.get('dc_hidden'): return
    o['dc_orig_hr'] = int(o.hide_render); o['dc_orig_hv'] = int(o.hide_viewport); o['dc_hidden'] = 1; o.hide_render = True; o.hide_viewport = True
nh = 0
for o in list(bpy.data.objects):
    n = o.name
    if ('_swivel' in n and n.startswith('CCOM_lounge')) or n.startswith('CCOM_lounge_rtable') or n.startswith('CCOM_lounge_ceil_') and n.endswith('20261015aw') \
       or n.startswith('CCOM_lounge_east_light'):
        hide(o); nh += 1
print('DC_HIDDEN', nh, flush=True)
# ---------------- materials on existing shell (reversible) ----------------
def swap(o, m):
    o['dc_orig_mat'] = o.data.materials[0].name; o.data.materials[0] = m
for n in ('CCOM_lounge_east_wallS_20261014jf', 'CCOM_lounge_east_wallN_20261014jf', 'CCOM_lounge_east_wallW_20261014jf'): swap(ob[n], M_white)
swap(ob['CCOM_lounge_east_floor_20261014jf'], M_tz)
# ---------------- 1 ceiling: tiles + linear LEDs + slot diffusers ----------------
ZT = 142.52; BAL0 = vW - 2.2; ZB = 139.07
box('dc_ceiling_tiles', uS - 0.03, uN + 0.03, v0 + 0.02, vW + 0.03, ZT - 0.02, ZT, M_tile)
for i, uc in enumerate((uS + 1.1, (uS + uN) / 2, uN - 1.1)):
    box('dc_linear_led_%d' % i, uc - 0.035, uc + 0.035, v0 + 0.5, vW - 0.4, ZT - 0.045, ZT - 0.02, M_led)
for i, uc in enumerate((uS + 2.05, uN - 2.05)):
    box('dc_slot_diffuser_%d' % i, uc - 0.025, uc + 0.025, v0 + 0.6, BAL0 - 0.3, ZT - 0.024, ZT - 0.019, M_slot)
# ---------------- 2 floor base trim, balcony, doors ----------------
box('dc_base_S', uS - 0.03, uS + 0.015, v0 + 0.32, vW + 0.03, Z0, Z0 + 0.10, M_base)
box('dc_base_N', uN - 0.015, uN + 0.03, v0 + 0.32, vW + 0.03, Z0, Z0 + 0.10, M_base)
box('dc_base_W', uS - 0.03, uN + 0.03, vW - 0.015, vW + 0.03, Z0, Z0 + 0.10, M_base)
# balcony (upper floor at the lab floor level 139.07, MEASURED level; depth UNVERIFIED)
box('dc_balcony_slab', uS - 0.05, uN + 0.05, BAL0, vW + 0.05, ZB - 0.35, ZB, M_white)
box('dc_balcony_soffit_tiles', uS - 0.03, uN + 0.03, BAL0 + 0.02, vW + 0.03, ZB - 0.37, ZB - 0.35, M_tile)
box('dc_balcony_led', (uS + uN) / 2 - 2.0, (uS + uN) / 2 + 2.0, BAL0 + 1.0, BAL0 + 1.07, ZB - 0.395, ZB - 0.37, M_led)
box('dc_balcony_rail_glass', uS + 0.05, uN - 0.05, BAL0 + 0.05, BAL0 + 0.062, ZB, ZB + 1.0, M_rail)
nposts = 6
for i in range(nposts):
    uc = uS + 0.1 + (uN - uS - 0.2) * i / (nposts - 1); cyl('dc_balcony_post_%d' % i, uc, BAL0 + 0.04, ZB, ZB + 1.07, 0.025, M_chr, 12)
box('dc_balcony_handrail', uS, uN, BAL0 + 0.02, BAL0 + 0.07, ZB + 1.05, ZB + 1.09, M_chr)
# maroon-framed interior window above the balcony (W wall; size/pos UNVERIFIED)
wu0, wu1, wz0, wz1 = uS + 1.4, uN - 1.4, ZB + 1.0, ZB + 2.6
box('dc_int_window_glass', wu0, wu1, vW - 0.03, vW - 0.01, wz0, wz1, M_dkgl)
for nm, a in (('L', (wu0 - 0.07, wu0, wz0 - 0.07, wz1 + 0.07)), ('R', (wu1, wu1 + 0.07, wz0 - 0.07, wz1 + 0.07)),
              ('B', (wu0, wu1, wz0 - 0.07, wz0)), ('T', (wu0, wu1, wz1, wz1 + 0.07)), ('M', ((wu0 + wu1) / 2 - 0.03, (wu0 + wu1) / 2 + 0.03, wz0, wz1))):
    box('dc_int_window_frame_' + nm, a[0], a[1], vW - 0.06, vW - 0.005, a[2], a[3], M_mar)
# maroon-framed glass doors + sidelites with frosted film under the balcony (back of visible depth)
def door_unit(k, uc):
    dw, sw, h = 0.95, 0.45, 2.25; u0 = uc - (dw + sw) / 2; us = u0 + sw
    box('dc_door%d_frost' % k, u0, u0 + dw + sw, vW - 0.025, vW - 0.008, Z0, Z0 + h, M_frost)
    for nm, a in (('L', (u0 - 0.06, u0)), ('S', (us - 0.03, us + 0.03)), ('R', (u0 + dw + sw, u0 + dw + sw + 0.06))):
        box('dc_door%d_frame_%s' % (k, nm), a[0], a[1], vW - 0.07, vW - 0.005, Z0, Z0 + h + 0.06, M_mar)
    box('dc_door%d_frame_T' % k, u0 - 0.06, u0 + dw + sw + 0.06, vW - 0.07, vW - 0.005, Z0 + h, Z0 + h + 0.06, M_mar)
    box('dc_door%d_frame_bot' % k, us, u0 + dw + sw, vW - 0.06, vW - 0.01, Z0, Z0 + 0.12, M_mar)
    box('dc_door%d_pull' % k, us + 0.10, us + 0.13, vW - 0.12, vW - 0.07, Z0 + 0.8, Z0 + 1.6, M_ss)
door_unit(0, uS + 1.5); door_unit(1, uN - 1.5)
cyl('dc_trash_stainless', (uS + uN) / 2, vW - 0.35, Z0, Z0 + 0.75, 0.21, M_ss)
# ---------------- 3 furniture ----------------
def shell_chair(name, cu, cv, yaw, m, low=True):
    sh = 0.40 if low else 0.46; w = 0.72 if low else 0.50; d = 0.70 if low else 0.50; bh = 0.38 if low else 0.36
    a, b = offs(cu, cv, yaw, 0, 0)
    lbox(name + '_seat', a, b, w, d, Z0 + sh - 0.07, Z0 + sh, m, yaw)
    a, b = offs(cu, cv, yaw, 0, d / 2 - 0.04); lbox(name + '_back', a, b, w, 0.06, Z0 + sh - 0.02, Z0 + sh + bh, m, yaw)
    if low:
        for s in (-1, 1):
            a, b = offs(cu, cv, yaw, s * (w / 2 - 0.03), 0.05); lbox(name + '_arm%d' % s, a, b, 0.06, d - 0.12, Z0 + sh - 0.02, Z0 + sh + 0.18, m, yaw)
    for i, (sx_, sy_) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        a, b = offs(cu, cv, yaw, sx_ * (w / 2 - 0.06), sy_ * (d / 2 - 0.06)); lbox(name + '_leg%d' % i, a, b, 0.035, 0.035, Z0, Z0 + sh - 0.07, M_wood, yaw)
# blue shell lounge chairs at the window (Joe photo; count/positions UNVERIFIED)
vb = v0 + 1.05
for i, (fu, yaw) in enumerate(((0.16, 0.35), (0.38, -0.2), (0.62, 0.25), (0.84, -0.3))):
    shell_chair('dc_blue_lounge_%d' % i, uS + (uN - uS) * fu, vb, math.pi / 2 + yaw, M_blue)  # facing the window-ish/room, angled
# white rectangular tables on charcoal rugs with sage/grey shell chairs
for k, uc in enumerate((uS + 1.55, uS + 3.65)):
    vc = v0 + 3.4
    box('dc_rug_%d' % k, uc - 0.95, uc + 0.95, vc - 1.3, vc + 1.3, Z0, Z0 + 0.012, M_rug)
    box('dc_table_%d_top' % k, uc - 0.40, uc + 0.40, vc - 0.80, vc + 0.80, Z0 + 0.72, Z0 + 0.75, M_tab)
    for j in (-1, 1):
        cyl('dc_table_%d_ped%d' % (k, j), uc, vc + j * 0.5, Z0 + 0.03, Z0 + 0.72, 0.035, M_chr, 12)
        box('dc_table_%d_foot%d' % (k, j), uc - 0.28, uc + 0.28, vc + j * 0.5 - 0.03, vc + j * 0.5 + 0.03, Z0 + 0.012, Z0 + 0.04, M_chr)
    for j, (du, dv, yaw) in enumerate(((-0.62, -0.4, -math.pi / 2), (-0.62, 0.4, -math.pi / 2), (0.62, -0.4, math.pi / 2), (0.62, 0.4, math.pi / 2))):
        shell_chair('dc_side_chair_%d_%d' % (k, j), uc + du, vc + dv, yaw + (0.12 if j % 2 else -0.08), M_sage if (j + k) % 2 else M_grey, low=False)
# chevron bench sofa with wood back along the N wall
bu = uN - 0.36; bv0, bv1 = v0 + 2.4, v0 + 4.6
box('dc_chevron_bench_seat', bu - 0.30, bu + 0.30, bv0, bv1, Z0 + 0.10, Z0 + 0.45, M_chev)
box('dc_chevron_bench_plinth', bu - 0.26, bu + 0.26, bv0 + 0.05, bv1 - 0.05, Z0, Z0 + 0.10, M_base)
box('dc_chevron_bench_woodback', uN - 0.075, uN - 0.02, bv0 - 0.05, bv1 + 0.05, Z0 + 0.10, Z0 + 0.95, M_wood)
box('dc_chevron_bench_backcushion', uN - 0.16, uN - 0.075, bv0 + 0.02, bv1 - 0.02, Z0 + 0.45, Z0 + 0.85, M_chev)
# orange + grey lounge chairs under the balcony
shell_chair('dc_orange_lounge', uS + 1.0, BAL0 + 0.9, math.pi * 0.85, M_orng)
shell_chair('dc_grey_lounge', uS + 2.1, BAL0 + 1.1, math.pi * 1.1, M_grey)
# ---------------- interior light (invisible to camera/glossy/transmission) ----------------
def area(name, u, v, z, sx_, sy_, P, up=False):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = 'RECTANGLE'; ld.size = sx_; ld.size_y = sy_; ld.energy = P; ld.color = (1.0, 0.96, 0.90)
    o = bpy.data.objects.new(name, ld); col.objects.link(o); o.location = W(u, v, z); o.rotation_euler = (math.pi if up else 0, 0, ANG)
    o.visible_camera = False; o.visible_glossy = False; o.visible_transmission = False; return o
LP = float(os.environ.get('LP', '180'))
for i, uc in enumerate((uS + 1.1, (uS + uN) / 2, uN - 1.1)):
    area('dc_led_area_%d' % i, uc, (v0 + BAL0) / 2 + 0.3, ZT - 0.06, 0.25, BAL0 - v0, LP)
area('dc_balcony_area', (uS + uN) / 2, BAL0 + 1.0, ZB - 0.42, 4.0, 0.3, LP * 0.45)
area('dc_ceiling_wash', (uS + uN) / 2, (v0 + BAL0) / 2, 138.6, uN - uS - 0.6, BAL0 - v0 - 0.6, LP * 0.9, up=True)

# ---------------- rule 4a self-check: dc faces coplanar with the room shell planes (visible doubling) ----------------
bad = 0
for o in col.objects:
    if o.type != 'MESH': continue
    mw = o.matrix_world
    for f in o.data.polygons:
        c = mw @ f.center; nn = (mw.to_3x3() @ f.normal).normalized(); q = Vector((c.x, c.y)) - A
        u, v = q.dot(D), q.dot(NI)
        for val, ref, ax in ((u, uS, D), (u, uN, D), (v, vW, NI)):
            if abs(val - ref) < 0.004 and abs(Vector((nn.x, nn.y)).dot(ax)) > 0.99: bad += 1
        if abs(c.z - Z0) < 0.001 and abs(nn.z) > 0.99 and nn.z < 0: pass  # bottoms on the floor are hidden contact, not doubling
print('DC_4A coplanar faces with walls:', bad, flush=True)
for o in col.objects: o['dc_tag'] = TAG
sc['dc_ccom_east_interior'] = TAG
print('DC_BUILT', len(col.objects), 'objects', flush=True)
if os.environ.get('SAVE') == '1':
    bpy.ops.wm.save_mainfile(); print('DC_SAVED', bpy.data.filepath, flush=True)
