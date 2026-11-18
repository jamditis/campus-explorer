"""Session ue (Nov 5 2026 ~2:24 PM ET, MAIN, day 9): College Hall EAST face from 1960s Digital Commons slides.

Photo-backed (1960s slides; current state UNVERIFIED):
- Replace east ground-floor punched windows with arched openings (slides 345/595/311).
- Secondary rectangular E door on south end of long E wing (slide 345) — NO globe lamps
  (256/269 ceremonial door face ambiguous / likely W; furniture rule).
- Subtle E belt course + deeper arched reveals + sill drips.

Do NOT undo tw/tz cream. Do not touch University Hall / Webster / Normal Ave furniture.
Tag ue_obj=1; collection UE_Cole_Hall_east_UNVERIFIED.
REVERT=1 restores TZ EN window/drip meshes from backup and deletes ue objects.
"""
import bpy, bmesh, os, math, json, shutil
from mathutils import Vector, Matrix

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DRY = os.environ.get('DRY') == '1'
D = '/workspace/nj-scenes/montclair-state/'
CN = 'UE_Cole_Hall_east_UNVERIFIED'
TAG = 'ue_obj'
TZ_WIN = 'TZ_Cole_windows_EN_UNVERIFIED'
TZ_DRIP = 'TZ_Cole_sill_drips_EN_UNVERIFIED'
BAK_DIR = D + 'data/ue/'
BAK_WIN = BAK_DIR + 'bak_TZ_Cole_windows_EN.obj'  # not used; use blend mesh copy
GRADE = 131.61
SCALE = 0.70

def mat(name, col, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    m.use_fake_user = True
    return m

def ensure_col():
    sc = bpy.context.scene
    col = bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
    if CN not in [c.name for c in sc.collection.children]:
        sc.collection.children.link(col)
    return col

def new_obj(name, mats, col):
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    for m in mats:
        me.materials.append(m)
    o[TAG] = 1
    o['ue_source'] = '20261105ue'
    return o

def add_box(bm, cx, cy, z0, z1, hx, hy, rot, mi):
    R = Matrix.Rotation(rot, 4, 'Z')
    vs = []
    for z in (z0, z1):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(Vector((cx, cy, 0)) + (R @ Vector((sx * hx, sy * hy, 0))).to_3d() + Vector((0, 0, z))))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f]).material_index = mi

def add_arch_window(bm, cx, cy, z0, z1, half_w, depth, rot, mi_fr, mi_gl, mi_st, segs=12):
    """Open arched window: dark glass fill + thin dark frame rim + thin cream edge lips (NOT a solid cream block)."""
    R = Matrix.Rotation(rot, 4, 'Z')
    h_rect = (z1 - z0) * 0.58
    z_spring = z0 + h_rect
    r = half_w * 0.98
    # Full glass: rect body
    gx = (R @ Vector((0, 0.22, 0))).x
    gy = (R @ Vector((0, 0.22, 0))).y
    add_box(bm, cx + gx, cy + gy, z0 + 0.03, z_spring, half_w * 0.88, 0.05, rot, mi_gl)
    # Full glass: arch head stacked
    for i in range(segs):
        t0 = i / segs
        t1 = (i + 1) / segs
        h0 = t0 * r
        h1 = t1 * r
        hm = 0.5 * (h0 + h1)
        hw = math.sqrt(max(1e-6, r * r - hm * hm))
        z_lo = z_spring + h0
        z_hi = z_spring + h1 + 0.008
        add_box(bm, cx + gx, cy + gy, z_lo, z_hi, hw * 0.92, 0.04, rot, mi_gl)
    # Dark frame rim — left/right jambs + sill + spring bar
    fx = (R @ Vector((0, 0.06, 0))).x
    fy = (R @ Vector((0, 0.06, 0))).y
    jamb = 0.06
    # left jamb
    add_box(bm, cx + fx + (R @ Vector((-half_w + jamb * 0.5, 0, 0))).x,
                 cy + fy + (R @ Vector((-half_w + jamb * 0.5, 0, 0))).y,
                 z0, z_spring + r * 0.15, jamb * 0.5, 0.05, rot, mi_fr)
    # right jamb
    add_box(bm, cx + fx + (R @ Vector((half_w - jamb * 0.5, 0, 0))).x,
                 cy + fy + (R @ Vector((half_w - jamb * 0.5, 0, 0))).y,
                 z0, z_spring + r * 0.15, jamb * 0.5, 0.05, rot, mi_fr)
    # sill
    add_box(bm, cx + fx, cy + fy, z0, z0 + 0.07, half_w * 0.95, 0.055, rot, mi_fr)
    # spring bar
    add_box(bm, cx + fx, cy + fy, z_spring - 0.04, z_spring + 0.04, half_w * 0.92, 0.05, rot, mi_fr)
    # arch frame rim (outer edge only)
    for i in range(segs):
        t0 = i / segs
        t1 = (i + 1) / segs
        h0 = t0 * r
        h1 = t1 * r
        hm = 0.5 * (h0 + h1)
        hw = math.sqrt(max(1e-6, r * r - hm * hm))
        z_lo = z_spring + h0
        z_hi = z_spring + h1 + 0.008
        for sign in (-1.0, 1.0):
            u = sign * (hw - 0.04)
            add_box(bm,
                    cx + fx + (R @ Vector((u, 0, 0))).x,
                    cy + fy + (R @ Vector((u, 0, 0))).y,
                    z_lo, z_hi, 0.045, 0.05, rot, mi_fr)
    # cream lip — thin outer border only (sill ledge + side strips), not a fill
    sx = (R @ Vector((0, 0.01, 0))).x
    sy = (R @ Vector((0, 0.01, 0))).y
    add_box(bm, cx + sx, cy + sy, z0 - 0.05, z0 + 0.02, half_w + 0.08, 0.04, rot, mi_st)  # sill drip lip
    for sign in (-1.0, 1.0):
        u = sign * (half_w + 0.05)
        add_box(bm,
                cx + sx + (R @ Vector((u, 0, 0))).x,
                cy + sy + (R @ Vector((u, 0, 0))).y,
                z0, z_spring + r * 0.2, 0.04, 0.035, rot, mi_st)

def remove_ue_objects():
    # remove tagged objects
    for o in [o for o in list(bpy.data.objects) if o.get(TAG)]:
        me = o.data if o.type == 'MESH' else None
        cam = o.data if o.type == 'CAMERA' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if me and hasattr(me, 'users') and me.users == 0:
            bpy.data.meshes.remove(me)
        if cam and hasattr(cam, 'users') and cam.users == 0:
            bpy.data.cameras.remove(cam)
    col = bpy.data.collections.get(CN)
    if col:
        bpy.data.collections.remove(col)
    # restore TZ meshes from hidden backup objects
    for bak_name, live_name in (
        ('UE_bak_TZ_Cole_windows_EN', TZ_WIN),
        ('UE_bak_TZ_Cole_sill_drips_EN', TZ_DRIP),
    ):
        bak = bpy.data.objects.get(bak_name)
        live = bpy.data.objects.get(live_name)
        if bak and live and bak.type == 'MESH' and live.type == 'MESH':
            # replace live mesh data with bak copy
            new_me = bak.data.copy()
            old = live.data
            live.data = new_me
            if old.users == 0:
                bpy.data.meshes.remove(old)
            bpy.data.objects.remove(bak, do_unlink=True)
            if bak.data and bak.data.users == 0:
                pass
        elif bak:
            bpy.data.objects.remove(bak, do_unlink=True)
    # also remove leftover bak meshes named UE_bak_*
    for me in list(bpy.data.meshes):
        if me.name.startswith('UE_bak_') and me.users == 0:
            bpy.data.meshes.remove(me)
    print('UE REVERTED')

def backup_mesh_object(live_name, bak_name):
    live = bpy.data.objects.get(live_name)
    if not live or live.type != 'MESH':
        return False
    # if backup already exists, skip (idempotent apply after partial)
    if bpy.data.objects.get(bak_name):
        return True
    me = live.data.copy()
    me.name = bak_name + '_mesh'
    o = bpy.data.objects.new(bak_name, me)
    o.hide_viewport = True
    o.hide_render = True
    o[TAG] = 1  # will be removed on revert after restore — actually bak should NOT have TAG for remove_ue first pass
    # Store bak outside TAG sweep: use different marker
    o['ue_bak'] = 1
    # link to scene but hidden
    bpy.context.scene.collection.objects.link(o)
    return True

def strip_east_gf_from_tz(live_name, z_max, x_min=-80.0):
    """Remove mesh islands whose face centers are on east GF (x > x_min, z < z_max)."""
    o = bpy.data.objects.get(live_name)
    if not o or o.type != 'MESH':
        return 0
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    # mark verts belonging to east-GF faces
    kill = set()
    for f in bm.faces:
        c = o.matrix_world @ f.calc_center_median()
        if c.x >= x_min and c.z <= z_max:
            for v in f.verts:
                kill.add(v)
    n = len(kill)
    # also kill connected faces that are mostly east-GF (orphan frame bits)
    bmesh.ops.delete(bm, geom=list(kill), context='VERTS')
    bm.to_mesh(o.data)
    o.data.update()
    bm.free()
    return n

if REV:
    # restore first needs bak objects present — remove_ue deletes TAG objs including bak if tagged
    # So: restore from ue_bak marker objects, then delete remaining ue_obj
    for bak_name, live_name in (
        ('UE_bak_TZ_Cole_windows_EN', TZ_WIN),
        ('UE_bak_TZ_Cole_sill_drips_EN', TZ_DRIP),
    ):
        bak = bpy.data.objects.get(bak_name)
        live = bpy.data.objects.get(live_name)
        if bak and live and bak.type == 'MESH' and live.type == 'MESH':
            new_me = bak.data.copy()
            old = live.data
            live.data = new_me
            if old.users == 0:
                bpy.data.meshes.remove(old)
            me_ref = bak.data
            bpy.data.objects.remove(bak, do_unlink=True)
            if me_ref.users == 0:
                bpy.data.meshes.remove(me_ref)
            print('UE restored', live_name)
        elif bak:
            bpy.data.objects.remove(bak, do_unlink=True)
    for o in [o for o in list(bpy.data.objects) if o.get(TAG) or o.get('ue_bak')]:
        me = o.data if o.type == 'MESH' else None
        cam = o.data if o.type == 'CAMERA' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)
        if cam and cam.users == 0:
            bpy.data.cameras.remove(cam)
    col = bpy.data.collections.get(CN)
    if col:
        bpy.data.collections.remove(col)
    # purge session materials (fake-user leftovers)
    for m in list(bpy.data.materials):
        if m.name.startswith('UE_Cole_') or m.name.startswith('UE_'):
            bpy.data.materials.remove(m)
    print('UE REVERTED')
    if SAVE:
        bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# ---- APPLY ----
# Idempotent: revert soft first if prior ue objects exist
if any(o.get(TAG) for o in bpy.data.objects) or bpy.data.objects.get('UE_bak_TZ_Cole_windows_EN'):
    print('UE prior state detected — cleaning before re-apply')
    # inline soft revert without save
    for bak_name, live_name in (
        ('UE_bak_TZ_Cole_windows_EN', TZ_WIN),
        ('UE_bak_TZ_Cole_sill_drips_EN', TZ_DRIP),
    ):
        bak = bpy.data.objects.get(bak_name)
        live = bpy.data.objects.get(live_name)
        if bak and live and bak.type == 'MESH' and live.type == 'MESH':
            new_me = bak.data.copy()
            old = live.data
            live.data = new_me
            if old.users == 0:
                bpy.data.meshes.remove(old)
            me_ref = bak.data
            bpy.data.objects.remove(bak, do_unlink=True)
            if me_ref.users == 0:
                bpy.data.meshes.remove(me_ref)
    for o in [o for o in list(bpy.data.objects) if (o.get(TAG) or o.get('ue_bak')) and o.type != 'CAMERA']:
        me = o.data if o.type == 'MESH' else None
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)
    col = bpy.data.collections.get(CN)
    if col:
        # keep collection; just emptied of meshes
        pass

col = ensure_col()
M_st = bpy.data.materials.get('TW_Cole_stucco_cream_UNVERIFIED') or mat('TW_Cole_stucco_cream_UNVERIFIED', (0.86, 0.835, 0.78), 0.88)
M_fr = bpy.data.materials.get('TW_Cole_win_frame_UNVERIFIED') or mat('TW_Cole_win_frame_UNVERIFIED', (0.92, 0.90, 0.86), 0.55)
M_fr_dark = mat('UE_Cole_arch_frame_dark_UNVERIFIED', (0.12, 0.11, 0.10), 0.55)
M_gl = bpy.data.materials.get('TW_Cole_win_glass_UNVERIFIED') or mat('TW_Cole_win_glass_UNVERIFIED', (0.04, 0.05, 0.055), 0.25)
M_door = mat('UE_Cole_door_dark_UNVERIFIED', (0.08, 0.12, 0.09), 0.55)
M_drip = bpy.data.materials.get('TZ_Cole_sill_drip_UNVERIFIED') or mat('UE_Cole_sill_drip_UNVERIFIED', (0.18, 0.16, 0.14), 0.85)
M_belt = mat('UE_Cole_belt_course_UNVERIFIED', (0.82, 0.80, 0.74), 0.78)
M_step = mat('UE_Cole_step_concrete_UNVERIFIED', (0.55, 0.53, 0.48), 0.90)

if not DRY:
    backup_mesh_object(TZ_WIN, 'UE_bak_TZ_Cole_windows_EN')
    backup_mesh_object(TZ_DRIP, 'UE_bak_TZ_Cole_sill_drips_EN')
    # untag bak so TAG sweep on next revert uses ue_bak
    for bn in ('UE_bak_TZ_Cole_windows_EN', 'UE_bak_TZ_Cole_sill_drips_EN'):
        b = bpy.data.objects.get(bn)
        if b and TAG in b:
            del b[TAG]
        if b:
            b['ue_bak'] = 1

    # GF east punch removal: sill row0 top ~ GRADE + 1.58*0.7 + 2.72*0.7 ≈ 131.61+1.11+1.90 ≈ 134.62
    z_cut = GRADE + 1.58 * SCALE + 2.72 * SCALE + 0.35  # ~134.97
    n1 = strip_east_gf_from_tz(TZ_WIN, z_cut, x_min=-80.0)
    n2 = strip_east_gf_from_tz(TZ_DRIP, z_cut, x_min=-80.0)
    print('UE stripped east-GF verts from TZ win/drip', n1, n2)

ring = json.load(open(D + 'north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
P = [Vector((x, y)) for x, y in ring]
if P[0] == P[-1]:
    P = P[:-1]
area = sum(P[i].x * P[(i + 1) % len(P)].y - P[(i + 1) % len(P)].x * P[i].y for i in range(len(P))) / 2

# East edges of interest: 18, 19, 20 (long E run)
EAST_EDGES = {18, 19, 20}

win = new_obj('UE_Cole_east_arched_GF_UNVERIFIED', [M_fr_dark, M_gl, M_st], col)
drip = new_obj('UE_Cole_east_arch_drips_UNVERIFIED', [M_drip], col)
belt = new_obj('UE_Cole_east_belt_UNVERIFIED', [M_belt], col)
door = new_obj('UE_Cole_east_door_secondary_UNVERIFIED', [M_door, M_fr, M_st, M_step], col)

bm_w = bmesh.new()
bm_d = bmesh.new()
bm_b = bmesh.new()
bm_door = bmesh.new()

narch = 0
# Arch dims from slides (UNVERIFIED sizes): taller/narrower than punched
arch_half_w = 0.78  # ~1.56 m wide
arch_sill = GRADE + 1.15
arch_top = GRADE + 4.10  # keep under mid-storey sill (~GRADE+4.4)
arch_pitch = 3.4

for i in range(len(P)):
    a, b = P[i], P[(i + 1) % len(P)]
    d = b - a
    L = d.length
    if L < 5.0:
        continue
    t = d / L
    n = Vector((t.y, -t.x)) if area > 0 else Vector((-t.y, t.x))
    if n.x <= 0.55:
        continue  # not east
    if i not in EAST_EDGES and L < 12:
        continue
    edge_rot = math.atan2(t.y, t.x)
    margin = 1.6
    usable = L - 2 * margin
    if usable < arch_pitch:
        continue
    # slide595: ~3 on south wing (edge 18); slide345: ~5 on central — use pitch
    nb = max(1, int(round(usable / arch_pitch)))
    # edge 18 (south wing): prefer 3; edge 19+20 share ~5 total
    if i == 18:
        nb = 3
    elif i == 19:
        nb = 3
    elif i == 20:
        nb = 2
    for k in range(nb):
        u = margin + (k + 0.5) * (usable / nb)
        cx = a.x + t.x * u
        cy = a.y + t.y * u
        # push slightly outward
        cx += n.x * 0.08
        cy += n.y * 0.08
        add_arch_window(bm_w, cx, cy, arch_sill, arch_top, arch_half_w, 0.40, edge_rot, 0, 1, 2, segs=8)
        # sill drip under arch
        add_box(bm_d, cx + n.x * 0.12, cy + n.y * 0.12, arch_sill - 0.05, arch_sill + 0.02, arch_half_w * 0.95, 0.04, edge_rot, 0)
        narch += 1
    # belt course along full east edge at ~GRADE+3.0 (rail height from door slides)
    bz0 = GRADE + 4.28
    bz1 = bz0 + 0.10
    # place as a long thin box along edge mid
    mid = (a + b) / 2
    add_box(bm_b, mid.x + n.x * 0.06, mid.y + n.y * 0.06, bz0, bz1, L * 0.48, 0.05, edge_rot, 0)

# Secondary east door — southern end of edge 18 (slide 345)
i = 18
a, b = P[i], P[(i + 1) % len(P)]
d = b - a
L = d.length
t = d / L
n = Vector((t.y, -t.x)) if area > 0 else Vector((-t.y, t.x))
edge_rot = math.atan2(t.y, t.x)
# near south end (small u)
u = 2.4
cx = a.x + t.x * u + n.x * 0.10
cy = a.y + t.y * u + n.y * 0.10
# surround
add_box(bm_door, cx, cy, GRADE + 0.05, GRADE + 3.35, 1.05, 0.14, edge_rot, 2)  # stucco surround
# recess
add_box(bm_door, cx + n.x * 0.08, cy + n.y * 0.08, GRADE + 0.15, GRADE + 3.15, 0.90, 0.10, edge_rot, 1)  # frame
# double doors (two leaves)
leaf_w = 0.42
add_box(bm_door, cx + (Matrix.Rotation(edge_rot, 4, 'Z') @ Vector((-leaf_w * 0.55, 0.18, 0))).x,
             cy + (Matrix.Rotation(edge_rot, 4, 'Z') @ Vector((-leaf_w * 0.55, 0.18, 0))).y,
             GRADE + 0.20, GRADE + 2.70, leaf_w * 0.5, 0.05, edge_rot, 0)
add_box(bm_door, cx + (Matrix.Rotation(edge_rot, 4, 'Z') @ Vector((leaf_w * 0.55, 0.18, 0))).x,
             cy + (Matrix.Rotation(edge_rot, 4, 'Z') @ Vector((leaf_w * 0.55, 0.18, 0))).y,
             GRADE + 0.20, GRADE + 2.70, leaf_w * 0.5, 0.05, edge_rot, 0)
# small landing (3 steps) — NOT globe lamps
for s in range(3):
    zs0 = GRADE - 0.05 + s * 0.14
    zs1 = zs0 + 0.14
    depth = 0.32
    out = 0.35 + s * 0.32
    add_box(bm_door, cx + n.x * out, cy + n.y * out, zs0, zs1, 1.15, depth * 0.5, edge_rot, 3)

if not DRY:
    bm_w.to_mesh(win.data); bm_w.free()
    bm_d.to_mesh(drip.data); bm_d.free()
    bm_b.to_mesh(belt.data); bm_b.free()
    bm_door.to_mesh(door.data); bm_door.free()
    print('UE arched GF', narch, 'door+belt built')
else:
    bm_w.free(); bm_d.free(); bm_b.free(); bm_door.free()
    print('UE DRY')

# Count
nue = sum(1 for o in bpy.data.objects if o.get(TAG))
print('UE objects tagged', nue, 'total objs', len(bpy.data.objects))

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
