"""Session uf (Nov 5 2026 ~3:18 PM ET, MAIN, day 9 leftover polish):
(A) Normal Ave soft-end material fade on UA asphalt (UD leftover) — FLOAT attr
    uf_end_fade + UF_asphalt_softfade_UNVERIFIED (alpha fade near soft ends).
(B) College Hall east arch polish — smoother segs, clearer glass, thin mullion,
    deeper recess; hide UE arched GF mesh; keep UE drips/belt/door.
ALL UNVERIFIED. Tag uf_obj / uf_mat / uf_fix. REVERT=1 restores mats + attrs + UE visibility.
"""
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/uf/'
os.makedirs(DATA, exist_ok=True)
COLN = 'UF_day9_leftover_polish_UNVERIFIED'
TAG = 'uf_obj'
SRC_MAT = 'UD_asphalt_worn_NormalAve_UNVERIFIED'
UF_MAT = 'UF_asphalt_softfade_UNVERIFIED'
ATTR = 'uf_end_fade'
TAPER_M = 8.0  # match UA TAPER_M
UA_ASPHALT = [
    'UA_NormalAve_CR618_583841725_727_729_UNVERIFIED',
    'UA_CollegeAve_spur_1557427669_UNVERIFIED',
    'UA_SkylineWay_south_232846698_UNVERIFIED',
]
UE_ARCH = 'UE_Cole_east_arched_GF_UNVERIFIED'
UF_ARCH = 'UF_Cole_east_arched_GF_UNVERIFIED'
UF_DRIP = 'UF_Cole_east_arch_drips_polish_UNVERIFIED'  # optional extra; may skip
J_MAT = DATA + 'ua_mat_slots.json'
J_ATTR = DATA + 'ua_end_fade_backup.json'  # whether attr existed
J_HIDE = DATA + 'ue_arch_hide.json'
GRADE = 131.61


def ensure_coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def mat_simple(name, col, rough=0.6, metal=0.0, trans=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.blend_method = 'HASHED'
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = trans
    if 'Alpha' in b.inputs:
        b.inputs['Alpha'].default_value = alpha
    m.use_fake_user = False
    m['uf_mat'] = 1
    return m


def remove_uf_objects():
    n = 0
    for o in list(bpy.data.objects):
        if o.get(TAG):
            me = o.data
            t = o.type
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and me.users == 0:
                if t == 'MESH':
                    bpy.data.meshes.remove(me)
                elif t == 'CAMERA':
                    bpy.data.cameras.remove(me)
            n += 1
    c = bpy.data.collections.get(COLN)
    if c and len(c.objects) == 0 and len(c.children) == 0:
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        is_uf = bool(m.get('uf_mat')) or (m.name.startswith('UF_') and m.name != SRC_MAT)
        if not is_uf:
            continue
        m.use_fake_user = False
        if m.users == 0:
            bpy.data.materials.remove(m)
    return n


def restore_mat_slots():
    if not os.path.exists(J_MAT):
        print('UF no mat slot backup')
        return 0
    d = json.load(open(J_MAT))
    n = 0
    for name, slots in d.items():
        o = bpy.data.objects.get(name)
        if not o:
            continue
        for i, mn in enumerate(slots):
            if i >= len(o.material_slots):
                break
            m = bpy.data.materials.get(mn) if mn else None
            o.material_slots[i].material = m
        if o.get('uf_fix'):
            del o['uf_fix']
        n += 1
    m = bpy.data.materials.get(UF_MAT)
    if m:
        m.use_fake_user = False
        if m.users == 0:
            bpy.data.materials.remove(m)
    # leave SRC_MAT fake_user as-is (ud may want it); ensure it exists
    if bpy.data.materials.get(SRC_MAT) is None:
        print('UF WARN missing', SRC_MAT, 'after restore')
    print('UF restored mat slots', n)
    return n


def clear_end_fade_attrs():
    n = 0
    for name in UA_ASPHALT:
        o = bpy.data.objects.get(name)
        if not o or o.type != 'MESH':
            continue
        me = o.data
        if ATTR in me.attributes:
            me.attributes.remove(me.attributes[ATTR])
            n += 1
        if o.get('uf_fix'):
            del o['uf_fix']
    print('UF cleared end_fade attrs', n)
    return n


def restore_ue_arch_visibility():
    if not os.path.exists(J_HIDE):
        return
    d = json.load(open(J_HIDE))
    for name, state in d.items():
        o = bpy.data.objects.get(name)
        if not o:
            continue
        o.hide_viewport = state.get('hide_viewport', False)
        o.hide_render = state.get('hide_render', False)
    print('UF restored UE arch visibility')


def revert():
    restore_mat_slots()
    clear_end_fade_attrs()
    restore_ue_arch_visibility()
    n = remove_uf_objects()
    print('UF REVERTED objs_removed', n)


# Always soft-clean prior uf state before apply or on REVERT
revert()
if REV:
    if SAVE:
        bpy.ops.wm.save_mainfile()
        print('SAVED')
    raise SystemExit


# ---------- APPLY A: soft-end fade ----------
def paint_end_fade(o):
    """FLOAT attr uf_end_fade: 1 at soft tip, 0 beyond TAPER_M along principal XY axis."""
    me = o.data
    mw = o.matrix_world
    pts = [mw @ v.co for v in me.vertices]
    if len(pts) < 4:
        return 0
    # centroid + covariance for principal XY axis
    cx = sum(p.x for p in pts) / len(pts)
    cy = sum(p.y for p in pts) / len(pts)
    sxx = syy = sxy = 0.0
    for p in pts:
        dx, dy = p.x - cx, p.y - cy
        sxx += dx * dx
        syy += dy * dy
        sxy += dx * dy
    # largest eigenvector of 2x2
    # [sxx sxy; sxy syy]
    tr = sxx + syy
    det = sxx * syy - sxy * sxy
    # eigenvalue
    disc = max(0.0, tr * tr / 4 - det)
    lam = tr / 2 + math.sqrt(disc)
    if abs(sxy) > 1e-9:
        ax, ay = lam - syy, sxy
    elif sxx >= syy:
        ax, ay = 1.0, 0.0
    else:
        ax, ay = 0.0, 1.0
    L = math.hypot(ax, ay) or 1.0
    ax, ay = ax / L, ay / L
    projs = [(p.x - cx) * ax + (p.y - cy) * ay for p in pts]
    pmin, pmax = min(projs), max(projs)
    span = max(pmax - pmin, 1e-3)
    # write attribute
    if ATTR in me.attributes:
        me.attributes.remove(me.attributes[ATTR])
    attr = me.attributes.new(ATTR, 'FLOAT', 'POINT')
    n_hot = 0
    for i, pr in enumerate(projs):
        d = min(pr - pmin, pmax - pr)
        # smoothstep fade over TAPER_M
        t = max(0.0, min(1.0, d / TAPER_M))
        # smoothstep
        t = t * t * (3 - 2 * t)
        fade = 1.0 - t  # 1 at tip
        attr.data[i].value = fade
        if fade > 0.05:
            n_hot += 1
    o['uf_fix'] = 1
    o['UNVERIFIED_uf'] = 'soft-end alpha fade via uf_end_fade attr; visual/UNVERIFIED'
    print('UF painted', o.name, 'hot_verts', n_hot, 'span', round(span, 1), 'axis', round(ax, 3), round(ay, 3))
    return n_hot


def make_softfade_mat():
    src = bpy.data.materials.get(SRC_MAT)
    if src is None:
        raise SystemExit('missing ' + SRC_MAT)
    old = bpy.data.materials.get(UF_MAT)
    if old:
        bpy.data.materials.remove(old)
    # Pin source so Blender save does not purge it while slots point at UF copy
    src.use_fake_user = True
    src['uf_keep'] = 1
    m = src.copy()
    m.name = UF_MAT
    m['uf_mat'] = 1
    m.use_fake_user = False
    m['UNVERIFIED'] = 'UA asphalt soft-end alpha fade; material-only; UNVERIFIED'
    m.blend_method = 'HASHED'
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    b = nodes.get('Principled BSDF')
    out = nodes.get('Material Output')
    if not b or not out:
        raise SystemExit('UF mat missing Principled/Output')
    # Attribute → invert → Alpha; also Mix toward Transparent for strong tips
    attr = nodes.new('ShaderNodeAttribute')
    attr.attribute_name = ATTR
    attr.location = (-600, -200)
    inv = nodes.new('ShaderNodeMath')
    inv.operation = 'SUBTRACT'
    inv.inputs[0].default_value = 1.0
    inv.location = (-400, -200)
    links.new(attr.outputs['Fac'], inv.inputs[1])
    # Power curve so mid-taper stays mostly opaque, tip goes clear
    pown = nodes.new('ShaderNodeMath')
    pown.operation = 'POWER'
    pown.inputs[1].default_value = 1.6  # (1-fade)^1.6 → stronger tip clear
    pown.location = (-220, -200)
    links.new(inv.outputs[0], pown.inputs[0])
    # wire to Alpha
    # disconnect existing Alpha if any
    for l in list(b.inputs['Alpha'].links):
        links.remove(l)
    links.new(pown.outputs[0], b.inputs['Alpha'])
    # Also Mix Shader with Transparent for hairline kill (Cycles HASHED)
    trans = nodes.new('ShaderNodeBsdfTransparent')
    trans.location = (200, -300)
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (400, -50)
    # fac = fade (attr Fac) — 1 at tip → full transparent
    # use a second power on raw fade for mix fac
    powf = nodes.new('ShaderNodeMath')
    powf.operation = 'POWER'
    powf.inputs[1].default_value = 0.85
    powf.location = (200, 100)
    links.new(attr.outputs['Fac'], powf.inputs[0])
    links.new(powf.outputs[0], mix.inputs['Fac'])
    links.new(b.outputs['BSDF'], mix.inputs[1])
    links.new(trans.outputs['BSDF'], mix.inputs[2])
    # rewire Material Output
    for l in list(out.inputs['Surface'].links):
        links.remove(l)
    links.new(mix.outputs['Shader'], out.inputs['Surface'])
    print('UF made', UF_MAT)
    return m


def swap_ua_mats(uf_mat):
    slots_bak = {}
    for name in UA_ASPHALT:
        o = bpy.data.objects.get(name)
        if not o:
            print('UF missing', name)
            continue
        slots_bak[name] = [s.material.name if s.material else None for s in o.material_slots]
        for i, s in enumerate(o.material_slots):
            if s.material and s.material.name in (SRC_MAT, 'SF_asphalt_worn_UNVERIFIED'):
                o.material_slots[i].material = uf_mat
        o['uf_fix'] = 1
    json.dump(slots_bak, open(J_MAT, 'w'), indent=2)
    print('UF swapped mats on', list(slots_bak.keys()))
    return slots_bak


# ---------- APPLY B: arch polish ----------
def add_box(bm, cx, cy, z0, z1, hx, hy, rot, mi):
    R = Matrix.Rotation(rot, 4, 'Z')
    vs = []
    for z in (z0, z1):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(Vector((cx, cy, 0)) + (R @ Vector((sx * hx, sy * hy, 0))).to_3d() + Vector((0, 0, z))))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f]).material_index = mi


def add_arch_window_hi(bm, cx, cy, z0, z1, half_w, rot, mi_fr, mi_gl, mi_st, segs=20):
    """Smoother arched window: deeper recess, clearer glass, thin center mullion, cream lip."""
    R = Matrix.Rotation(rot, 4, 'Z')
    h_rect = (z1 - z0) * 0.58
    z_spring = z0 + h_rect
    r = half_w * 0.98
    # deeper glass plane (more into wall / more recessed from frame)
    g_off = 0.32
    gx = (R @ Vector((0, g_off, 0))).x
    gy = (R @ Vector((0, g_off, 0))).y
    # glass rect body
    add_box(bm, cx + gx, cy + gy, z0 + 0.04, z_spring, half_w * 0.86, 0.035, rot, mi_gl)
    # glass arch head — more segs, tighter stack
    for i in range(segs):
        t0 = i / segs
        t1 = (i + 1) / segs
        h0 = t0 * r
        h1 = t1 * r
        hm = 0.5 * (h0 + h1)
        hw = math.sqrt(max(1e-6, r * r - hm * hm))
        z_lo = z_spring + h0
        z_hi = z_spring + h1 + 0.004
        add_box(bm, cx + gx, cy + gy, z_lo, z_hi, hw * 0.90, 0.032, rot, mi_gl)
    # frame
    fx = (R @ Vector((0, 0.05, 0))).x
    fy = (R @ Vector((0, 0.05, 0))).y
    jamb = 0.055
    add_box(bm, cx + fx + (R @ Vector((-half_w + jamb * 0.5, 0, 0))).x,
                 cy + fy + (R @ Vector((-half_w + jamb * 0.5, 0, 0))).y,
                 z0, z_spring + r * 0.12, jamb * 0.5, 0.045, rot, mi_fr)
    add_box(bm, cx + fx + (R @ Vector((half_w - jamb * 0.5, 0, 0))).x,
                 cy + fy + (R @ Vector((half_w - jamb * 0.5, 0, 0))).y,
                 z0, z_spring + r * 0.12, jamb * 0.5, 0.045, rot, mi_fr)
    add_box(bm, cx + fx, cy + fy, z0, z0 + 0.06, half_w * 0.94, 0.05, rot, mi_fr)  # sill
    add_box(bm, cx + fx, cy + fy, z_spring - 0.035, z_spring + 0.035, half_w * 0.90, 0.045, rot, mi_fr)  # spring
    # arch frame rim
    for i in range(segs):
        t0 = i / segs
        t1 = (i + 1) / segs
        h0 = t0 * r
        h1 = t1 * r
        hm = 0.5 * (h0 + h1)
        hw = math.sqrt(max(1e-6, r * r - hm * hm))
        z_lo = z_spring + h0
        z_hi = z_spring + h1 + 0.004
        for sign in (-1.0, 1.0):
            u = sign * (hw - 0.035)
            add_box(bm,
                    cx + fx + (R @ Vector((u, 0, 0))).x,
                    cy + fy + (R @ Vector((u, 0, 0))).y,
                    z_lo, z_hi, 0.038, 0.045, rot, mi_fr)
    # thin center vertical mullion (style accent UNVERIFIED)
    add_box(bm, cx + gx * 0.6, cy + gy * 0.6, z0 + 0.08, z_spring + r * 0.55,
            0.022, 0.03, rot, mi_fr)
    # cream outer lip (thin)
    sx = (R @ Vector((0, -0.01, 0))).x
    sy = (R @ Vector((0, -0.01, 0))).y
    add_box(bm, cx + sx, cy + sy, z0 - 0.04, z0 + 0.015, half_w + 0.07, 0.035, rot, mi_st)
    for sign in (-1.0, 1.0):
        u = sign * (half_w + 0.045)
        add_box(bm,
                cx + sx + (R @ Vector((u, 0, 0))).x,
                cy + sy + (R @ Vector((u, 0, 0))).y,
                z0, z_spring + r * 0.15, 0.035, 0.03, rot, mi_st)


def build_polished_arches(col):
    # hide UE arches (keep drips/belt/door)
    hide_bak = {}
    ue = bpy.data.objects.get(UE_ARCH)
    if ue:
        hide_bak[UE_ARCH] = {
            'hide_viewport': bool(ue.hide_viewport),
            'hide_render': bool(ue.hide_render),
        }
        ue.hide_viewport = True
        ue.hide_render = True
    json.dump(hide_bak, open(J_HIDE, 'w'), indent=2)

    M_fr = bpy.data.materials.get('UE_Cole_arch_frame_dark_UNVERIFIED') or mat_simple(
        'UF_Cole_arch_frame_dark_UNVERIFIED', (0.10, 0.09, 0.085), 0.50)
    M_gl = mat_simple('UF_Cole_arch_glass_clearer_UNVERIFIED', (0.05, 0.06, 0.07),
                      rough=0.12, trans=0.45)
    M_st = bpy.data.materials.get('TW_Cole_stucco_cream_UNVERIFIED') or mat_simple(
        'TW_Cole_stucco_cream_UNVERIFIED', (0.86, 0.835, 0.78), 0.88)

    win = bpy.data.objects.get(UF_ARCH)
    if win:
        me = win.data
        bpy.data.objects.remove(win, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(UF_ARCH)
    win = bpy.data.objects.new(UF_ARCH, me)
    col.objects.link(win)
    me.materials.append(M_fr)
    me.materials.append(M_gl)
    me.materials.append(M_st)
    win[TAG] = 1
    win['uf_source'] = '20261105uf'
    win['UNVERIFIED'] = 'College Hall east GF arches polish; 1960s slides; current state UNVERIFIED'

    ring = json.load(open(D + 'north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
    P = [Vector((x, y)) for x, y in ring]
    if P[0] == P[-1]:
        P = P[:-1]
    area = sum(P[i].x * P[(i + 1) % len(P)].y - P[(i + 1) % len(P)].x * P[i].y for i in range(len(P))) / 2
    EAST_EDGES = {18, 19, 20}
    arch_half_w = 0.78
    arch_sill = GRADE + 1.15
    arch_top = GRADE + 4.10
    bm = bmesh.new()
    narch = 0
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        d = b - a
        L = d.length
        if L < 5.0:
            continue
        t = d / L
        n = Vector((t.y, -t.x)) if area > 0 else Vector((-t.y, t.x))
        if n.x <= 0.55:
            continue
        if i not in EAST_EDGES and L < 12:
            continue
        edge_rot = math.atan2(t.y, t.x)
        margin = 1.6
        usable = L - 2 * margin
        if usable < 3.4:
            continue
        if i == 18:
            nb = 3
        elif i == 19:
            nb = 3
        elif i == 20:
            nb = 2
        else:
            nb = max(1, int(round(usable / 3.4)))
        for k in range(nb):
            u = margin + (k + 0.5) * (usable / nb)
            cx = a.x + t.x * u + n.x * 0.10  # slightly deeper into wall than ue 0.08
            cy = a.y + t.y * u + n.y * 0.10
            add_arch_window_hi(bm, cx, cy, arch_sill, arch_top, arch_half_w, edge_rot, 0, 1, 2, segs=20)
            narch += 1
    bm.to_mesh(win.data)
    bm.free()
    win.data.update()
    print('UF polished arches', narch, 'segs=20 deeper+mullion+clearer glass')
    return narch


def add_cams(col):
    def ground_z(x, y):
        dg = bpy.context.evaluated_depsgraph_get()
        best = None
        for nm in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
            o = bpy.data.objects.get(nm)
            if not o:
                continue
            e = o.evaluated_get(dg)
            iw = o.matrix_world.inverted()
            r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
            if r[0]:
                z = (o.matrix_world @ r[1]).z
                if best is None or z > best:
                    best = z
        return best if best is not None else 118.0

    def cam(name, loc, target, lens=35):
        old = bpy.data.objects.get(name)
        if old:
            cd = old.data
            bpy.data.objects.remove(old, do_unlink=True)
            if cd and cd.users == 0:
                bpy.data.cameras.remove(cd)
        c = bpy.data.cameras.new(name)
        c.lens = lens
        c.clip_end = 60000
        o = bpy.data.objects.new(name, c)
        o.location = Vector(loc)
        o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
        o[TAG] = 1
        col.objects.link(o)
        return o

    # soft-end closeup on Normal Ave west soft tip (~x -276)
    gz = ground_z(-270, -290)
    cam('UF_CAM_closeup_NormalAve_softend',
        (-268.0, -285.0, gz + 2.2), (-272.0, -295.0, gz + 0.3), lens=45)
    # Normal Ave eye
    gz2 = ground_z(-160, -250)
    cam('UF_CAM_eye_NormalAve_from_N',
        (-160.0, -250.0, gz2 + 1.7), (-160.0, -300.0, gz2 + 0.5), lens=35)
    # College Hall east eye (reuse ue framing-ish)
    gzE = ground_z(-35, -118)
    cam('UF_CAM_eye_CollegeHall_from_E',
        (-35.0, -118.0, gzE + 1.7), (-64, -115, 136), lens=35)
    # arch closeup
    gzC = ground_z(-48, -122)
    cam('UF_CAM_closeup_CollegeHall_east_arches',
        (-48.0, -122.0, gzC + 2.0), (-64, -118, 134.5), lens=32)
    # oblique overview of worked area (Normal Ave + College Hall east)
    cam('UF_CAM_oblique_day9_leftover_from_SE',
        (-20.0, -200.0, 195.0), (-120.0, -150.0, 135.0), lens=28)
    print('UF cams ready')


# ---- apply ----
col = ensure_coll(COLN)
uf_mat = make_softfade_mat()
for name in UA_ASPHALT:
    o = bpy.data.objects.get(name)
    if o:
        paint_end_fade(o)
    else:
        print('UF missing asphalt', name)
swap_ua_mats(uf_mat)
narch = build_polished_arches(col)
add_cams(col)

print('UF objects tagged', sum(1 for o in bpy.data.objects if o.get(TAG)),
      'total objs', len(bpy.data.objects), 'arches', narch)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
print('UF DONE')
