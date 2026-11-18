"""Session vg (Nov 6 2026 ~5:25–~6:12 PM ET, MAIN, day-10 Freeman polish after vf).

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) S and E facade window rhythm toward vd W pane-grid language
     (split panes + mullion/muntin + terracotta spandrel + cooler glass;
      hide+replace UY S / UV E recessed; keep VC S/E dark backplanes).
  B) Optional mild W glass Alpha/Coat/sky-tint nudge if time.
  C) Optional mild N cream pier/belt punch if safe (never cover lettering/bay/doors/glass/screen).
  D) No invented N apron (Footpaths_OSM only). UH untouched. Webster lawn forever.

Collection: VG_Freeman_polish_UNVERIFIED
Tags: vg_obj / vg_mat / vg_slot_restore / vg_hidden
REVERT=1 restores slots + unhides + removes vg objs/mats/colls + restores glass stash
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vg'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VG_Freeman_polish_UNVERIFIED'
COL_CAM = 'VG_Freeman_cams'
GLASS_STASH = DATA + '/vg_w_glass_stash.json'
VBGLASS_STASH = DATA + '/vg_vb_glass_stash.json'

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
        raw = o.get('vg_slot_restore')
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
        del o['vg_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vg_kept_fake'):
            m.use_fake_user = False
            del m['vg_kept_fake']

def stash_principled(path, mat_name, keys=('Base Color','Roughness','Alpha','Coat Weight','Coat Roughness','Specular IOR Level','Transmission Weight','Metallic','Emission Color','Emission Strength')):
    m = bpy.data.materials.get(mat_name)
    if not m or not m.use_nodes or os.path.exists(path): return
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    d = {}
    for k in keys:
        if k in b.inputs:
            v = b.inputs[k].default_value
            try: d[k] = list(v)
            except TypeError: d[k] = float(v)
    json.dump(d, open(path, 'w'), indent=2)

def restore_principled(path, mat_name):
    m = bpy.data.materials.get(mat_name)
    if not m or not m.use_nodes or not os.path.exists(path): return
    d = json.load(open(path))
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    for k, v in d.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    print('VG restored', mat_name, 'from stash')

def unhide_vg_hidden():
    for o in bpy.data.objects:
        if o.get('vg_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vg_hidden']

def revert():
    restore_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
    restore_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
    restore_slots()
    unhide_vg_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vg_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vg_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VG REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vg', 'fixes': [], 'GR': GR, 'UNVERIFIED': True}

# ---- materials (reuse vd W language; new vg-tagged copies for S/E) ----
def mat_frame_dark(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vg_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.045, 0.035, 0.032, 1.0)
    b.inputs['Roughness'].default_value = 0.55
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.25
    return m

def mat_reveal(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vg_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.02, 0.018, 0.016, 1.0)
    b.inputs['Roughness'].default_value = 0.75
    return m

def mat_glass_vg(name):
    """Cooler/clearer glass matching post-vf W pane language (Alpha~0.55, Coat~0.70)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vg_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.66, 0.80, 0.93, 1.0)
    b.inputs['Roughness'].default_value = 0.012
    b.inputs['Alpha'].default_value = 0.55
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in b.inputs:
        b.inputs['Transmission'].default_value = 1.0
    if 'IOR' in b.inputs:
        b.inputs['IOR'].default_value = 1.45
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 0.70
        b.inputs['Coat Roughness'].default_value = 0.025
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.78
    m.blend_method = 'HASHED'
    try: m.shadow_method = 'HASHED'
    except Exception: pass
    return m

def mat_spandrel_vg(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vg_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.42, 0.16, 0.10, 1.0)
    b.inputs['Roughness'].default_value = 0.78
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.15
    return m

def mat_bp_dark(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vg_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.035, 0.045, 0.055, 1.0)
    b.inputs['Roughness'].default_value = 0.92
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.05
    return m

M_frame = mat_frame_dark('VG_Freeman_SE_frame_dark_UNVERIFIED')
M_reveal = mat_reveal('VG_Freeman_SE_reveal_dark_UNVERIFIED')
M_glass = mat_glass_vg('VG_Freeman_SE_glass_pane_UNVERIFIED')
M_span = mat_spandrel_vg('VG_Freeman_SE_spandrel_deep_UNVERIFIED')
M_bp = mat_bp_dark('VG_Freeman_SE_glass_backplane_UNVERIFIED')
M_frame_uy = bpy.data.materials.get('UV_Freeman_window_frame_darkred_UNVERIFIED') or M_frame
log['fixes'].append('mats_SE_pane_grid')

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
        o['vg_obj'] = 1
        o['UNVERIFIED'] = 'vg Freeman SE pane grid; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# W-matched storey bands
glass_bands = [
    (GR + 1.0, GR + 3.4),
    (GR + 3.85, GR + 6.25),
    (GR + 6.7, GR + 9.1),
    (GR + 9.55, GR + 11.95),
    (GR + 12.4, TOPZ - 0.55),
]
span_bands = [
    (GR + 3.4, GR + 3.85),
    (GR + 6.25, GR + 6.7),
    (GR + 9.1, GR + 9.55),
    (GR + 11.95, GR + 12.4),
]

BAY_W = 1.22
FRAME_DEP = 0.30
GLASS_DEP = 0.10
SPAN_DEP = 0.06
REVEAL_DEP = 0.04
PANE_GAP = 0.06
PANE_INSET = 0.06
BP_DEP = 0.04

def build_pane_grid(edge_i, obj_name, centers_override=None, pitch=3.6):
    e = [ed for ed in OSM['edges'] if ed['i'] == edge_i][0]
    U = Vector((e['u'][0], e['u'][1], 0)).normalized()
    N = Vector((e['n'][0], e['n'][1], 0)).normalized()
    A = Vector((e['a'][0], e['a'][1], 0))
    L = e['len']
    if centers_override is not None:
        centers = [t for t in centers_override if 1.2 < t < L - 1.2]
    else:
        centers = []
        n_bays = max(1, int((L - 4.0) / pitch))
        for i in range(n_bays):
            t = 2.0 + pitch * (i + 0.5)
            if t > L - 2.0: break
            centers.append(t)
    mb = MB(obj_name, [M_frame_uy, M_glass, M_span, M_reveal], col)
    n_panes = 0
    for t in centers:
        c = A + U * t
        mb.box(c + N * (OUT + 0.12), U, N, BAY_W, FRAME_DEP, GR + 0.75, TOPZ - 0.35, 0)
        for sgn in (-1, 1):
            rc = c + U * (sgn * (BAY_W / 2 - 0.05))
            mb.box(rc + N * (OUT + 0.20), U, N, 0.05, REVEAL_DEP, GR + 0.95, TOPZ - 0.50, 3)
        inner_w = BAY_W - 0.18
        pane_w = (inner_w - PANE_GAP) / 2
        for z0, z1 in glass_bands:
            if z1 <= z0 + 0.08: continue
            mb.box(c + N * (OUT + 0.16), U, N, inner_w + 0.02, REVEAL_DEP, z0 - 0.015, z0 + 0.02, 3)
            mb.box(c + N * (OUT + 0.16), U, N, inner_w + 0.02, REVEAL_DEP, z1 - 0.02, z1 + 0.015, 3)
            for sgn in (-1, 1):
                pc = c + U * (sgn * (pane_w / 2 + PANE_GAP / 2))
                mb.box(pc + N * (OUT + 0.22), U, N, pane_w - PANE_INSET, GLASS_DEP, z0 + 0.025, z1 - 0.025, 1)
                n_panes += 1
            mb.box(c + N * (OUT + 0.20), U, N, PANE_GAP + 0.02, 0.08, z0 + 0.01, z1 - 0.01, 0)
            if (z1 - z0) > 2.0:
                midz = (z0 + z1) / 2
                mb.box(c + N * (OUT + 0.205), U, N, inner_w - 0.04, 0.06, midz - 0.025, midz + 0.025, 0)
        for z0, z1 in span_bands:
            if z1 <= z0 + 0.02: continue
            mb.box(c + N * (OUT + 0.14), U, N, inner_w - 0.04, SPAN_DEP, z0 + 0.01, z1 - 0.01, 2)
            for sgn in (-1, 1):
                sc = c + U * (sgn * (inner_w / 2 - 0.02))
                mb.box(sc + N * (OUT + 0.15), U, N, 0.04, REVEAL_DEP, z0, z1, 3)
    mb.done()
    # VC-style dark backplanes slightly behind glass (extend; keep existing VC objs)
    bp = MB(obj_name.replace('_pane_grid_', '_glass_backplanes_'), [M_bp], col)
    for t in centers:
        c = A + U * t
        inner_w = BAY_W - 0.18
        for z0, z1 in glass_bands:
            if z1 <= z0 + 0.08: continue
            # behind wall face / behind glass: OUT - 0.10 (inward from outer)
            bp.box(c + N * (OUT - 0.10), U, N, inner_w - 0.08, BP_DEP, z0 + 0.04, z1 - 0.04, 0)
    bp.done()
    return len(centers), n_panes, centers, U, N, A, L

# ---------- A) Hide prior S/E recessed; build pane grids ----------
uy_s = bpy.data.objects.get('UY_Freeman_S_recessed_vertical_windows_UNVERIFIED')
if uy_s:
    uy_s.hide_render = True
    uy_s.hide_viewport = True
    uy_s['vg_hidden'] = 1
    log['fixes'].append('hide_UY_S_recessed_windows')

uv_e = bpy.data.objects.get('UV_Freeman_E_recessed_vertical_windows_UNVERIFIED')
if uv_e:
    uv_e.hide_render = True
    uv_e.hide_viewport = True
    uv_e['vg_hidden'] = 1
    log['fixes'].append('hide_UV_E_recessed_windows')

# Keep existing VC S/E BPs (still useful); new VG BPs added with grids
s_bays, s_panes, s_centers, U3, N3, A3, L3 = build_pane_grid(
    3, 'VG_Freeman_S_pane_grid_UNVERIFIED', centers_override=[3.5, 7.5, 11.5])
log['fixes'].append(f'S_pane_grid_bays{s_bays}_panes{s_panes}')
log['S_bays'] = s_bays
log['S_panes'] = s_panes

e_bays, e_panes, e_centers, U5, N5, A5, L5 = build_pane_grid(
    5, 'VG_Freeman_E_pane_grid_UNVERIFIED')
log['fixes'].append(f'E_pane_grid_bays{e_bays}_panes{e_panes}')
log['E_bays'] = e_bays
log['E_panes'] = e_panes

# ---------- B) Mild W glass nudge (stash first) ----------
stash_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
stash_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        # vf left Alpha~0.60 / Coat~0.80 — nudge slightly clearer, avoid opaque/black
        b.inputs['Alpha'].default_value = 0.52
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.85
            b.inputs['Coat Roughness'].default_value = 0.02
        b.inputs['Base Color'].default_value = (0.70, 0.84, 0.95, 1.0)
        b.inputs['Roughness'].default_value = 0.010
        log['fixes'].append('W_glass_Alpha0.52_Coat0.85_skycooler')
        log['W_glassA'] = 0.52

# ---------- C) Mild N cream eye punch (safe zones only) ----------
M_cream = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
M_shadow = M_reveal
e6 = [ed for ed in OSM['edges'] if ed['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
# Pier outer faces only — stop well clear of lettering band (~GR+4.2 to GR+5.6 typical)
# lettering is on N wing solid panel; pier punches already exist from vf — add thin outer tip lips only
n_fills = []
for t0, t1, tag in ((6.68, 6.95, 'pierW'), (11.70, 11.95, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    # outer tip lip below lettering / above canopy zone only mid-height skip lettering:
    # lips at GR+0.2..GR+3.5 and GR+6.2..TOPZ-0.4 (skip GR+3.5..GR+6.2 lettering band)
    for z0, z1, ztag in ((GR + 0.15, GR + 3.45, 'lo'), (GR + 6.25, TOPZ - 0.45, 'hi')):
        mb = MB(f'VG_Freeman_N_cream_tip_{tag}_{ztag}_UNVERIFIED', [M_cream], col)
        mb.box(mid + N6 * (OUT + 0.105), U6, N6, w - 0.01, 0.04, z0, z1, 0)
        mb.done()
        n_fills.append(f'tip_{tag}_{ztag}')
# thin shadow groove deepen on pier inner edges (toward curtain) — below/above lettering
for t, tag in ((6.97, 'pierW_E'), (11.68, 'pierE_W')):
    mid = A6 + U6 * t
    for z0, z1, ztag in ((GR + 0.2, GR + 3.4, 'lo'), (GR + 6.3, TOPZ - 0.5, 'hi')):
        mb = MB(f'VG_Freeman_N_shadow_deep_{tag}_{ztag}_UNVERIFIED', [M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.095), U6, N6, 0.035, 0.03, z0, z1, 0)
        mb.done()
        n_fills.append(f'shadow_{tag}_{ztag}')
log['n_cream_fills'] = n_fills
log['fixes'].append('N_cream_tip_lips_lettering_safe_' + '+'.join(n_fills[:4]) + f'_plus{max(0,len(n_fills)-4)}')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vg_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vg_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# S closeup — middle bay
t_s = s_centers[len(s_centers)//2] if s_centers else 7.5
c_s = A3 + U3 * t_s
add_cam('VG_CAM_closeup_Freeman_S_pane_grid',
        (c_s.x + N3.x * 5.5, c_s.y + N3.y * 5.5, GR + 5.8),
        (c_s.x + N3.x * (OUT + 0.22), c_s.y + N3.y * (OUT + 0.22), GR + 7.0), 50)

# E eye / polish view — mid bay from east
t_e = e_centers[len(e_centers)//3] if e_centers else L5 * 0.35
c_e = A5 + U5 * t_e
add_cam('VG_CAM_eye_Freeman_E_pane_grid',
        (c_e.x + N5.x * 18.0, c_e.y + N5.y * 18.0, GR + 4.5),
        (c_e.x, c_e.y, GR + 8.0), 35)
add_cam('VG_CAM_closeup_Freeman_E_pane_grid',
        (c_e.x + N5.x * 5.2, c_e.y + N5.y * 5.2, GR + 6.0),
        (c_e.x + N5.x * (OUT + 0.22), c_e.y + N5.y * (OUT + 0.22), GR + 7.2), 55)

# SE oblique overview for hero S/E together
cent = A3 + U3 * (L3 * 0.5) + N3 * 2.0
add_cam('VG_CAM_oblique_Freeman_from_SE',
        (cent.x + 22.0, cent.y + 8.0, GR + 22.0),
        (cent.x - 5.0, cent.y - 15.0, GR + 8.0), 28)

log['cams'] = [o.name for o in cc.objects if o.get('vg_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vg_obj'] = sum(1 for o in bpy.data.objects if o.get('vg_obj'))
log['n_vg_mat'] = sum(1 for m in bpy.data.materials if m.get('vg_mat'))
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }
json.dump(log, open(DATA + '/vg_main.json', 'w'), indent=2)
print('VG MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
