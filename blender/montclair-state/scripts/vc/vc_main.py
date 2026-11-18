"""Session vc (Nov 6 2026 ~1:20–~2:12 PM ET, MAIN, day-10 Freeman polish).

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) Dark interior backplanes behind W (+S / N-bay / E / entrance) recessed glass
     so Transmission glass reads clear at eye instead of cream shell through the pane.
     Thin dark grey planes INSIDE openings, set back from glass (not coplanar — SELF_REVIEW 4a).
  B) N entrance mid-wall cream — thin proud cream overlays on recess returns + pier flanks
     matching VB_Freeman_cream_brick_strong look / new VC cream mat. Must NOT cover
     lettering, terracotta bay, doors, glass, or screen face.
  C) Light polish after WIP review (separate vc_polish.py).

Collection: VC_Freeman_polish_UNVERIFIED
Tags: vc_obj / vc_mat / vc_slot_restore
REVERT=1 restores slots + removes vc objs/mats/colls (does NOT touch va lettering / ub/uc / vb)
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vc'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VC_Freeman_polish_UNVERIFIED'
COL_CAM = 'VC_Freeman_cams'

def ensure_coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def remove_obj(o):
    if o is None: return
    me = o.data; t = o.type
    bpy.data.objects.remove(o, do_unlink=True)
    if me is not None and me.users == 0:
        if t == 'MESH': bpy.data.meshes.remove(me)
        elif t == 'CAMERA': bpy.data.cameras.remove(me)
        elif t in ('FONT', 'CURVE'):
            try: bpy.data.curves.remove(me)
            except Exception: pass

def restore_slots():
    for o in bpy.data.objects:
        raw = o.get('vc_slot_restore')
        if not raw: continue
        try:
            names = json.loads(raw) if isinstance(raw, str) else list(raw)
        except Exception:
            continue
        while len(o.material_slots) < len(names):
            o.data.materials.append(None)
        for i, n in enumerate(names):
            if i >= len(o.material_slots): break
            o.material_slots[i].material = bpy.data.materials.get(n) if n else None
        del o['vc_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vc_kept_fake'):
            m.use_fake_user = False
            del m['vc_kept_fake']

GLASS_STASH = DATA + '/vc_glass_stash.json'

def stash_glass():
    g = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
    if not g or not g.use_nodes: return
    b = g.node_tree.nodes.get('Principled BSDF')
    if not b: return
    if os.path.exists(GLASS_STASH): return
    d = {
        'Base Color': list(b.inputs['Base Color'].default_value),
        'Roughness': b.inputs['Roughness'].default_value,
        'Alpha': b.inputs['Alpha'].default_value,
    }
    if 'Transmission Weight' in b.inputs:
        d['Transmission Weight'] = b.inputs['Transmission Weight'].default_value
    if 'Coat Weight' in b.inputs:
        d['Coat Weight'] = b.inputs['Coat Weight'].default_value
        d['Coat Roughness'] = b.inputs['Coat Roughness'].default_value
    if 'Specular IOR Level' in b.inputs:
        d['Specular IOR Level'] = b.inputs['Specular IOR Level'].default_value
    json.dump(d, open(GLASS_STASH, 'w'), indent=2)

def restore_glass():
    g = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
    if not g or not g.use_nodes: return
    if not os.path.exists(GLASS_STASH): return
    d = json.load(open(GLASS_STASH))
    b = g.node_tree.nodes.get('Principled BSDF')
    if not b: return
    for k, v in d.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    print('VC restored VB glass from stash')

def revert():
    restore_glass()
    restore_slots()
    for o in [o for o in list(bpy.data.objects) if o.get('vc_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vc_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VC REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vc', 'fixes': [], 'GR': GR, 'UNVERIFIED': True}

def mat_dark_backplane(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vc_mat'] = 1
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    # near-black / dark charcoal interior void
    b.inputs['Base Color'].default_value = (0.025, 0.025, 0.028, 1.0)
    b.inputs['Roughness'].default_value = 0.92
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.05
    if 'Metallic' in b.inputs:
        b.inputs['Metallic'].default_value = 0.0
    return m

def mat_cream_brick_vc(name):
    """Match VB cream brick strong look (Generated+Mapping)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vc_mat'] = 1
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.92
    t = nt.nodes.new('ShaderNodeTexBrick')
    t.inputs['Color1'].default_value = (0.80, 0.74, 0.60, 1)
    t.inputs['Color2'].default_value = (0.70, 0.64, 0.52, 1)
    t.inputs['Mortar'].default_value = (0.32, 0.28, 0.22, 1)
    t.inputs['Brick Width'].default_value = 0.22
    t.inputs['Row Height'].default_value = 0.068
    t.inputs['Mortar Size'].default_value = 0.018
    t.inputs['Scale'].default_value = 4.0
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mapping = nt.nodes.new('ShaderNodeMapping')
    mapping.inputs['Scale'].default_value = (2.2, 2.2, 2.2)
    nt.links.new(tc.outputs['Generated'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], t.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.28
    bump.inputs['Distance'].default_value = 0.005
    nt.links.new(t.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

M_dark = mat_dark_backplane('VC_Freeman_glass_backplane_dark_UNVERIFIED')
M_cream = mat_cream_brick_vc('VC_Freeman_cream_brick_midwall_UNVERIFIED')
# Prefer reusing VB cream mat if present so fills match eye look exactly
M_cream_vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED') or M_cream
log['fixes'].append('mats_dark_backplane_cream_midwall')
stash_glass()


class MB:
    def __init__(s, name, mats, coll):
        s.bm = bmesh.new(); s.name = name; s.mats = mats; s.coll = coll
    def box(s, c, u, n, w, dep, z0, z1, mi=0):
        u = Vector((u[0], u[1], 0)).normalized()
        n = Vector((n[0], n[1], 0)).normalized()
        c = Vector((c[0], c[1], 0))
        vs = []
        for z in (z0, z1):
            for a, b_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                p = c + u * (a * w / 2) + n * (b_ * dep / 2)
                vs.append(s.bm.verts.new((p.x, p.y, z)))
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            try: s.bm.faces.new([vs[i] for i in f]).material_index = mi
            except ValueError: pass
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o = bpy.data.objects.new(s.name, me); s.coll.objects.link(o)
        o['vc_obj'] = 1
        o['UNVERIFIED'] = 'vc Freeman polish; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- A) Dark backplanes ----------
# W face (edge 1) — match uy_polish proud glass at OUT+0.18
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
pitch = 3.6
centers_w = []
n_bays = max(1, int((L1 - 4.0) / pitch))
for i in range(n_bays):
    t = 2.0 + pitch * (i + 0.5)
    if t > L1 - 2.0: break
    centers_w.append(t)

# glass bands only (skip spandrel mi=2 bands)
w_glass_bands = [
    (GR + 1.0, GR + 3.4),
    (GR + 3.85, GR + 6.25),
    (GR + 6.7, GR + 9.1),
    (GR + 9.55, GR + 11.95),
    (GR + 12.4, TOPZ - 0.55),
]
# glass center at OUT+0.18 dep 0.08 → back face ~OUT+0.14; place backplane ~0.12 m further in
BP_W = OUT + 0.02   # center; dep 0.04 → OUT..OUT+0.04; ~14 cm behind glass center — not coplanar
mb_w = MB('VC_Freeman_W_glass_backplanes_UNVERIFIED', [M_dark], col)
n_w_bp = 0
for t in centers_w:
    c = A1 + U1 * t
    for z0, z1 in w_glass_bands:
        if z1 <= z0 + 0.05: continue
        # inset 2 cm from glass edges in U; set back along -N from glass
        mb_w.box(c + N1 * BP_W, U1, N1, 0.88, 0.04, z0 + 0.02, z1 - 0.02, 0)
        n_w_bp += 1
mb_w.done()
log['fixes'].append(f'W_glass_backplanes_x{n_w_bp}_bays{len(centers_w)}')
log['W_backplanes'] = n_w_bp

# S face (edge 3) — uy_main recessed glass at OUT-0.05
e3 = [e for e in OSM['edges'] if e['i'] == 3][0]
U3 = Vector((e3['u'][0], e3['u'][1], 0)).normalized()
N3 = Vector((e3['n'][0], e3['n'][1], 0)).normalized()
A3 = Vector((e3['a'][0], e3['a'][1], 0))
L3 = e3['len']
s_ts = [3.5, 7.5, 11.5]
s_glass_bands = [
    (GR + 1.0, GR + 4.0), (GR + 4.5, GR + 8.0), (GR + 8.5, TOPZ - 0.6),
]
BP_S = OUT - 0.18  # glass at OUT-0.05; backplane further in
mb_s = MB('VC_Freeman_S_glass_backplanes_UNVERIFIED', [M_dark], col)
n_s_bp = 0
for t in s_ts:
    if t > L3 - 1.5: continue
    c = A3 + U3 * t
    for z0, z1 in s_glass_bands:
        if z1 <= z0 + 0.05: continue
        mb_s.box(c + N3 * BP_S, U3, N3, 0.82, 0.04, z0 + 0.02, z1 - 0.02, 0)
        n_s_bp += 1
mb_s.done()
log['fixes'].append(f'S_glass_backplanes_x{n_s_bp}')
log['S_backplanes'] = n_s_bp

# E face (edge 5) — uv recessed glass at OUT-0.05
e5 = [e for e in OSM['edges'] if e['i'] == 5][0]
U5 = Vector((e5['u'][0], e5['u'][1], 0)).normalized()
N5 = Vector((e5['n'][0], e5['n'][1], 0)).normalized()
A5 = Vector((e5['a'][0], e5['a'][1], 0))
L5 = e5['len']
centers_e = []
n_bays_e = max(1, int((L5 - 4.0) / pitch))
for i in range(n_bays_e):
    t = 2.0 + pitch * (i + 0.5)
    if t > L5 - 2.0: break
    centers_e.append(t)
e_glass_bands = [
    (GR + 1.0, GR + 3.6), (GR + 3.9, GR + 6.5), (GR + 6.8, GR + 9.4),
    (GR + 9.7, GR + 12.3), (GR + 12.6, TOPZ - 0.6),
]
BP_E = OUT - 0.18
mb_e = MB('VC_Freeman_E_glass_backplanes_UNVERIFIED', [M_dark], col)
n_e_bp = 0
for t in centers_e:
    c = A5 + U5 * t
    for z0, z1 in e_glass_bands:
        if z1 <= z0 + 0.05: continue
        mb_e.box(c + N5 * BP_E, U5, N5, 0.88, 0.04, z0 + 0.02, z1 - 0.02, 0)
        n_e_bp += 1
mb_e.done()
log['fixes'].append(f'E_glass_backplanes_x{n_e_bp}_bays{len(centers_e)}')
log['E_backplanes'] = n_e_bp

# N terracotta bay glass (uy polish PROUD = OUT+0.32)
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A = Vector((e6['a'][0], e6['a'][1], 0))
L6 = e6['len']
# bay t 3.29-6.64; 3 panels; glass 2 rows
T_BAY0, T_BAY1 = 3.29, 6.64
ww = T_BAY1 - T_BAY0
wc = A + U * ((T_BAY0 + T_BAY1) / 2)
pane_w = ww / 3
PROUD = OUT + 0.32
glass_mid = GR + 4.70
glass_top = TOPZ - 0.55
glass_split = (glass_mid + glass_top) / 2
BP_BAY = PROUD - 0.14  # set back from glass; not coplanar
mb_bay = MB('VC_Freeman_Nbay_glass_backplanes_UNVERIFIED', [M_dark], col)
n_bay_bp = 0
for i in range(3):
    pc = A + U * (T_BAY0 + (i + 0.5) * pane_w)
    for z0, z1 in ((glass_mid, glass_split - 0.05), (glass_split + 0.05, glass_top)):
        mb_bay.box(pc + N * BP_BAY, U, N, pane_w - 0.16, 0.04, z0 + 0.02, z1 - 0.02, 0)
        n_bay_bp += 1
mb_bay.done()
log['fixes'].append(f'Nbay_glass_backplanes_x{n_bay_bp}')
log['Nbay_backplanes'] = n_bay_bp

# N entrance curtain glass backplanes (deep recess)
T_ENT0, T_ENT1 = 5.58, 12.85
ew = T_ENT1 - T_ENT0
ec = A + U * ((T_ENT0 + T_ENT1) / 2)
recess = 0.85
# glass at OUT - recess; backplane further inside building
BP_ENT = OUT - recess - 0.12
mb_ent = MB('VC_Freeman_N_entrance_glass_backplanes_UNVERIFIED', [M_dark], col)
# one tall backplane behind curtain (slightly smaller than glass) + per-door strips
mb_ent.box(ec + N * BP_ENT, U, N, ew - 0.45, 0.04, GR + 2.55, TOPZ - 0.35, 0)
# behind door glass leaves (lower)
door_w = ew / 4
for i in range(4):
    dc = A + U * (T_ENT0 + (i + 0.5) * door_w)
    mb_ent.box(dc + N * BP_ENT, U, N, door_w - 0.22, 0.04, GR + 0.08, GR + 2.40, 0)
mb_ent.done()
log['fixes'].append('N_entrance_glass_backplanes')
log['entrance_backplanes'] = 1 + 4

# ---------- B) N entrance mid-wall cream (returns + pier flanks) ----------
fills = []
# Recess side returns: concrete grey → cream overlay proud into recess
# uv: returns at ec ± U*(ew/2), along N of length recess, thickness 0.20 along U
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U * (sgn * ew / 2)
    # center of return slab along depth
    cc = rc + N * (OUT - recess / 2)
    # proud into recess along -sgn * U (toward center)
    cc = cc + U * (-sgn * 0.04)
    mb = MB(f'VC_Freeman_N_cream_fill_entrance_return_{tag}_UNVERIFIED', [M_cream_vb], col)
    # along-face direction is N (into recess), outward normal is U
    mb.box(cc, N, U, recess - 0.08, 0.06, GR - 0.02, TOPZ - 0.15, 0)
    mb.done()
    fills.append(f'return_{tag}')

# Outer pier flanks between bay/screen and entrance opening — thin cream on wall face
# West pier: just east of bay end / west of curtain (~t 6.55-6.85) — bay ends 6.64; curtain starts 5.58
# Use t 6.55-6.90 only ABOVE door head / outside glass overhang risk: full height thin strip at OUT
# Stay clear of terracotta bay (t<=6.64) → start at 6.68
# East pier: just west of screen (screen 11.98) / east of curtain — t 11.70-11.95
for t0, t1, tag in ((6.68, 6.95, 'pierW'), (11.70, 11.95, 'pierE')):
    w = t1 - t0
    if w < 0.05: continue
    mid = A + U * ((t0 + t1) / 2)
    mb = MB(f'VC_Freeman_N_cream_fill_entrance_{tag}_UNVERIFIED', [M_cream_vb], col)
    mb.box(mid + N * (OUT + 0.055), U, N, w, 0.06, GR - 0.02, TOPZ - 0.12, 0)
    mb.done()
    fills.append(tag)

# Mid-wall cream ABOVE canopy on entrance side — between glass curtain outer and screen/bay,
# only where grey OSM wall may still read at the outer plane beside canopy ends.
# Canopy covers entrance; grey often shows as vertical slabs beside recess at eye.
# Additional: cream apron on outer face for t 7.0-7.4 and 11.4-11.7 ABOVE canopy only (z>canopy)
can_z1 = GR + 3.85
for t0, t1, tag in ((7.00, 7.45, 'midW_above_canopy'), (11.35, 11.70, 'midE_above_canopy')):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    mb = MB(f'VC_Freeman_N_cream_fill_{tag}_UNVERIFIED', [M_cream_vb], col)
    # only above canopy to avoid covering doors/glass at eye — still on outer wall beside recess
    mb.box(mid + N * (OUT + 0.055), U, N, w, 0.06, can_z1 + 0.05, TOPZ - 0.12, 0)
    mb.done()
    fills.append(tag)

log['n_fills'] = fills
log['fixes'].append('N_cream_fills_' + '+'.join(fills))

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vc_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vc_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# close-up W glass with backplanes visible
mid_w = A1 + U1 * (centers_w[len(centers_w)//3] if centers_w else L1 * 0.4)
add_cam('VC_CAM_closeup_Freeman_W_glass_backplane',
        (mid_w.x + N1.x * 7.5, mid_w.y + N1.y * 7.5, GR + 4.5),
        (mid_w.x, mid_w.y, GR + 7.0), 50)
# N entrance mid-wall cream close-up
scr_c = A + U * 9.2  # mid entrance
add_cam('VC_CAM_closeup_Freeman_N_midwall_cream',
        (scr_c.x + N.x * 9.0 - U.x * 0.5, scr_c.y + N.y * 9.0 - U.y * 0.5, GR + 2.8),
        (scr_c.x, scr_c.y, GR + 5.5), 40)

log['cams'] = [o.name for o in cc.objects if o.get('vc_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vc_obj'] = sum(1 for o in bpy.data.objects if o.get('vc_obj'))
log['n_vc_mat'] = sum(1 for m in bpy.data.materials if m.get('vc_mat'))
log['n_vb_obj'] = sum(1 for o in bpy.data.objects if o.get('vb_obj'))
# lettering integrity
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }
json.dump(log, open(DATA + '/vc_main.json', 'w'), indent=2)
print('VC MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
