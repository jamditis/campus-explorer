"""Session vk (Nov 6 2026 ~9:20–~10:12 PM ET, MAIN, day-10 Freeman polish after vj).

Targets (ALL UNVERIFIED; photo language 1096/1114; Joe Nov 6 glass more reflective;
best-judgment after ≥3 silent updates — no ask Joe):
  A) Extreme W grazing cream-between-panes → deepen/add interbay dark reveals + push
     reflective glass further (Alpha~0.23 / Coat 1.0 / Spec~1.27 / cooler) + sky-tint
     emiss~2.50. Keep VC/VG dark BPs; keep VD pane grid; keep VJ interbay (hide none).
  B) N cream punch vs 1096 — additive pier lips / shadow grooves / storey belts /
     mortar fillets / tip quoins / return belts (over vj). Warmer/brighter cream punch.
     Never cover lettering / terracotta bay / doors / glass / screen. va lettering untouched.
  C) S/E mid-distance: polish existing VG S×3 + E×11 pane mats only (Alpha/Coat/
     terracotta/BP mild). Do NOT change bay counts (leave pitch/count UNVERIFIED).
  D) No invented N apron. UH untouched. Webster lawn forever.

Collection: VK_Freeman_polish_UNVERIFIED
Tags: vk_obj / vk_mat / vk_slot_restore / vk_hidden
REVERT=1 restores principled stashes + removes vk objs/mats/colls + restores slots + unhides
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vk'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VK_Freeman_polish_UNVERIFIED'
COL_CAM = 'VK_Freeman_cams'
GLASS_STASH = DATA + '/vk_w_glass_stash.json'
VBGLASS_STASH = DATA + '/vk_vb_glass_stash.json'
SEGLASS_STASH = DATA + '/vk_se_glass_stash.json'
SESPAN_STASH = DATA + '/vk_se_span_stash.json'
SKY_STASH = DATA + '/vk_sky_stash.json'
VBCREAM_STASH = DATA + '/vk_vb_cream_stash.json'
VISHADOW_STASH = DATA + '/vk_vi_shadow_stash.json'
VICREAM_STASH = DATA + '/vk_vi_cream_stash.json'
VIMORTAR_STASH = DATA + '/vk_vi_mortar_stash.json'
SEBP_STASH = DATA + '/vk_se_bp_stash.json'
VJCREAM_STASH = DATA + '/vk_vj_cream_stash.json'
VJSHADOW_STASH = DATA + '/vk_vj_shadow_stash.json'
VJMORTAR_STASH = DATA + '/vk_vj_mortar_stash.json'
VJIBAY_STASH = DATA + '/vk_vj_ibay_stash.json'

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
        raw = o.get('vk_slot_restore')
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
        del o['vk_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vk_kept_fake'):
            m.use_fake_user = False
            del m['vk_kept_fake']

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
    print('VK restored', mat_name, 'from stash')

def unhide_vk_hidden():
    for o in bpy.data.objects:
        if o.get('vk_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vk_hidden']

def revert():
    restore_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
    restore_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
    restore_principled(SEGLASS_STASH, 'VG_Freeman_SE_glass_pane_UNVERIFIED')
    restore_principled(SESPAN_STASH, 'VG_Freeman_SE_spandrel_deep_UNVERIFIED')
    restore_principled(SKY_STASH, 'VF_Freeman_W_sky_tint_UNVERIFIED')
    restore_principled(VBCREAM_STASH, 'VB_Freeman_cream_brick_strong_UNVERIFIED')
    restore_principled(VISHADOW_STASH, 'VI_Freeman_N_shadow_deep_UNVERIFIED')
    restore_principled(VICREAM_STASH, 'VI_Freeman_N_cream_punch_UNVERIFIED')
    restore_principled(VIMORTAR_STASH, 'VI_Freeman_N_mortar_line_UNVERIFIED')
    restore_principled(SEBP_STASH, 'VG_Freeman_SE_backplane_dark_UNVERIFIED')
    restore_principled(VJCREAM_STASH, 'VJ_Freeman_N_cream_punch_UNVERIFIED')
    restore_principled(VJSHADOW_STASH, 'VJ_Freeman_N_shadow_deep_UNVERIFIED')
    restore_principled(VJMORTAR_STASH, 'VJ_Freeman_N_mortar_line_UNVERIFIED')
    restore_principled(VJIBAY_STASH, 'VJ_Freeman_W_interbay_dark_UNVERIFIED')
    restore_slots()
    unhide_vk_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vk_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vk_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VK REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vk', 'fixes': [], 'GR': GR, 'UNVERIFIED': True, 'SILENT': True,
       'joe_glass': 'more reflective wherever accurate interior not modeled',
       'best_judgment': 'S/E bay pitch/count left UNVERIFIED (mat polish only); W interbay deepen + glass Alpha~0.23/sky~2.50; N cream punch continue'}

# ---- materials ----
def mat_cream_punch(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vk_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.94, 0.82, 0.60, 1.0)
    b.inputs['Roughness'].default_value = 0.66
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.18
    return m

def mat_shadow(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vk_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.002, 0.0015, 0.001, 1.0)
    b.inputs['Roughness'].default_value = 0.94
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.02
    return m

def mat_mortar(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vk_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.24, 0.18, 0.12, 1.0)
    b.inputs['Roughness'].default_value = 0.96
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.04
    return m

def mat_interbay_dark(name):
    """Near-black reveal between W panes — kills cream stripe at extreme grazing."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vk_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.005, 0.004, 0.0035, 1.0)
    b.inputs['Roughness'].default_value = 0.90
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.03
    return m

M_cream = mat_cream_punch('VK_Freeman_N_cream_punch_UNVERIFIED')
M_vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED') or M_cream
M_shadow = mat_shadow('VK_Freeman_N_shadow_deep_UNVERIFIED')
M_mortar = mat_mortar('VK_Freeman_N_mortar_line_UNVERIFIED')
M_ibay = mat_interbay_dark('VK_Freeman_W_interbay_dark_UNVERIFIED')
log['fixes'].append('mats_cream_shadow_mortar_interbay')

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
        o['vk_obj'] = 1
        o['UNVERIFIED'] = 'vk Freeman polish; sizes UNVERIFIED; photo 1096/1114; Joe glass reflective'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- stash mats we'll nudge ----------
stash_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
stash_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
stash_principled(SEGLASS_STASH, 'VG_Freeman_SE_glass_pane_UNVERIFIED')
stash_principled(SESPAN_STASH, 'VG_Freeman_SE_spandrel_deep_UNVERIFIED')
stash_principled(SKY_STASH, 'VF_Freeman_W_sky_tint_UNVERIFIED')
stash_principled(VBCREAM_STASH, 'VB_Freeman_cream_brick_strong_UNVERIFIED')
stash_principled(VISHADOW_STASH, 'VI_Freeman_N_shadow_deep_UNVERIFIED')
stash_principled(VICREAM_STASH, 'VI_Freeman_N_cream_punch_UNVERIFIED')
stash_principled(VIMORTAR_STASH, 'VI_Freeman_N_mortar_line_UNVERIFIED')
stash_principled(SEBP_STASH, 'VG_Freeman_SE_backplane_dark_UNVERIFIED')
stash_principled(VJCREAM_STASH, 'VJ_Freeman_N_cream_punch_UNVERIFIED')
stash_principled(VJSHADOW_STASH, 'VJ_Freeman_N_shadow_deep_UNVERIFIED')
stash_principled(VJMORTAR_STASH, 'VJ_Freeman_N_mortar_line_UNVERIFIED')
stash_principled(VJIBAY_STASH, 'VJ_Freeman_W_interbay_dark_UNVERIFIED')

# ---------- A) W glass more reflective + sky + interbay dark ----------
wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        # clearer than vj polish Alpha 0.26; keep Coat/Spec high (Joe reflective)
        b.inputs['Alpha'].default_value = 0.23
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.003
        b.inputs['Base Color'].default_value = (0.86, 0.95, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.001
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.27
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 1.0
        log['fixes'].append('W_glass_Alpha0.23_Coat1.0_SpecIOR1.27_JoeReflective')
        log['W_glassA'] = 0.23

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 2.50
        b.inputs['Base Color'].default_value = (0.80, 0.90, 1.0, 1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (0.82, 0.91, 1.0, 1.0)
        b.inputs['Alpha'].default_value = 0.32
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.45
            b.inputs['Coat Roughness'].default_value = 0.025
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.45
        log['fixes'].append('sky_tint_emiss2.50_Alpha0.32_mildCoat')

sky_obj = bpy.data.objects.get('VF_Freeman_W_sky_tint_continuous_UNVERIFIED')
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
if sky_obj is None and sky:
    t0, t1 = 2.5, L1 - 2.5
    mid = A1 + U1 * ((t0 + t1) / 2)
    mb = MB('VK_Freeman_W_sky_tint_continuous_UNVERIFIED', [sky], col)
    mb.box(mid + N1 * 0.14, U1, N1, t1 - t0, 0.02, GR + 0.90, TOPZ - 0.40, 0)
    mb.done()
    log['fixes'].append('vk_sky_sheet_rebuild')
else:
    log['fixes'].append('kept_vf_sky_sheet')

# Deepen VJ interbay mat; add slightly prouder/wider VK interbay dark overlays
vj_ib = bpy.data.materials.get('VJ_Freeman_W_interbay_dark_UNVERIFIED')
if vj_ib and vj_ib.use_nodes:
    b = vj_ib.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.004, 0.0035, 0.003, 1.0)
        log['fixes'].append('VJ_interbay_darker_nudge')

pitch = 3.6
centers = []
for i in range(max(1, int((L1 - 4.0) / pitch))):
    t = 2.0 + pitch * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)
BAY_W = 1.22
interbay = []
for i in range(len(centers) - 1):
    t_mid = (centers[i] + centers[i + 1]) / 2
    gap_w = max(0.30, pitch - BAY_W - 0.20)
    c = A1 + U1 * t_mid
    mb = MB(f'VK_Freeman_W_interbay_dark_{i:02d}_UNVERIFIED', [M_ibay, M_shadow], col)
    # slightly prouder/wider than VJ to kill residual cream stripe
    mb.box(c + N1 * (OUT + 0.092), U1, N1, gap_w * 0.98, 0.040, GR + 0.70, TOPZ - 0.30, 0)
    for sgn in (-1, 1):
        rc = c + U1 * (sgn * (gap_w / 2 - 0.020))
        mb.box(rc + N1 * (OUT + 0.102), U1, N1, 0.040, 0.024, GR + 0.85, TOPZ - 0.40, 1)
    mb.done()
    interbay.append(i)
log['W_interbay_dark'] = len(interbay)
log['fixes'].append(f'W_interbay_dark_reveals_{len(interbay)}')

# ---------- B) N cream punch (lettering-safe; additive over vj) ----------
e6 = [ed for ed in OSM['edges'] if ed['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
L6 = e6['len']
n_fills = []

# Proud pier face lips further out than vj (vj OUT+0.168)
for t0, t1, tag in ((6.66, 6.97, 'pierW'), (11.68, 11.97, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.10, GR + 3.38, 'lo'), (GR + 6.35, TOPZ - 0.35, 'hi')):
        mb = MB(f'VK_Freeman_N_cream_lip_{tag}_{ztag}_UNVERIFIED', [M_cream, M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.188), U6, N6, w - 0.002, 0.076, z0, z1, 0)
        mb.box(mid + U6 * ((w / 2) * (1 if tag == 'pierW' else -1) * 0.028) + N6 * (OUT + 0.195),
               U6, N6, 0.034, 0.032, z0 + 0.05, z1 - 0.05, 1)
        mb.done()
        n_fills.append(f'lip_{tag}_{ztag}')

# Deeper shadow grooves
for t, tag in ((6.98, 'pierW_E'), (11.67, 'pierE_W')):
    mid = A6 + U6 * t
    for z0, z1, ztag in ((GR + 0.12, GR + 3.32, 'lo'), (GR + 6.38, TOPZ - 0.40, 'hi')):
        mb = MB(f'VK_Freeman_N_shadow_groove_{tag}_{ztag}_UNVERIFIED', [M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.162), U6, N6, 0.060, 0.048, z0, z1, 0)
        mb.done()
        n_fills.append(f'shadow_{tag}_{ztag}')

# Storey belt punch — skip zi==1 lettering band
belt_zs = [GR + 3.45, GR + 6.85, GR + 10.25, TOPZ - 0.62]
for t0, t1, tag in ((6.66, 6.97, 'pierW'), (11.68, 11.97, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for zi, z in enumerate(belt_zs):
        if zi == 1:
            continue
        mb = MB(f'VK_Freeman_N_belt_punch_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.202), U6, N6, w - 0.001, 0.088, z - 0.01, z + 0.150, 0)
        mb.box(mid + N6 * (OUT + 0.210), U6, N6, w - 0.008, 0.038, z - 0.058, z - 0.01, 1)
        mb.done()
        n_fills.append(f'belt_{tag}_{zi}')

# Mid-pier vertical fillet
for t0, t1, tag in ((6.80, 6.84, 'pierW_fillet'), (11.81, 11.85, 'pierE_fillet')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.15, GR + 3.30, 'lo'), (GR + 6.40, TOPZ - 0.50, 'hi')):
        mb = MB(f'VK_Freeman_N_mortar_fillet_{tag}_{ztag}_UNVERIFIED', [M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.198), U6, N6, w, 0.026, z0, z1, 0)
        mb.done()
        n_fills.append(f'fillet_{tag}_{ztag}')

# Quoin outer tips — clear of lettering z≈137.95
let_z0 = 137.55
for t0, t1, tag in ((1.00, 1.62, 'Wtip_outer'), (max(1.0, L6 - 1.60), max(1.4, L6 - 1.00), 'Etip_outer')):
    if t1 <= t0 + 0.05 or t1 > L6 - 0.15 or t0 < 0.2:
        continue
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    mb = MB(f'VK_Freeman_N_quoin_punch_{tag}_UNVERIFIED', [M_vb, M_shadow], col)
    mb.box(mid + N6 * (OUT + 0.188), U6, N6, w, 0.090, GR - 0.02, let_z0 - 0.28, 0)
    mb.box(mid + N6 * (OUT + 0.188), U6, N6, w, 0.090, let_z0 + 0.72, TOPZ - 0.10, 0)
    mb.box(mid + U6 * (w / 2 * 0.85) + N6 * (OUT + 0.195), U6, N6, 0.042, 0.036, GR + 0.2, let_z0 - 0.30, 1)
    mb.done()
    n_fills.append(f'quoin_{tag}')

# Return wall shelves
T_ENT0, T_ENT1 = 5.58, 12.85
ew = T_ENT1 - T_ENT0
ec = A6 + U6 * ((T_ENT0 + T_ENT1) / 2)
recess = 0.85
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U6 * (sgn * ew / 2) + U6 * (-sgn * 0.05)
    cc = rc + N6 * (OUT - recess / 2)
    for zi, z in enumerate((GR + 3.40, GR + 6.80, GR + 10.20)):
        mb = MB(f'VK_Freeman_N_return_belt_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(cc + N6 * 0.070, N6, U6, recess - 0.10, 0.12, z - 0.01, z + 0.150, 0)
        mb.box(cc + N6 * 0.082, N6, U6, recess - 0.14, 0.040, z - 0.060, z - 0.01, 1)
        mb.done()
        n_fills.append(f'return_belt_{tag}_{zi}')

# Mild VB cream brick punch
vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
if vb and vb.use_nodes:
    b = vb.node_tree.nodes.get('Principled BSDF')
    if b:
        cur = list(b.inputs['Base Color'].default_value)
        b.inputs['Base Color'].default_value = (
            min(0.97, cur[0] * 1.02 + 0.012),
            min(0.90, cur[1] * 1.02 + 0.010),
            min(0.72, cur[2] * 1.012 + 0.006),
            1.0,
        )
        b.inputs['Roughness'].default_value = max(0.50, min(0.84, float(b.inputs['Roughness'].default_value) * 0.95))
        log['fixes'].append('VB_cream_brick_mild_punch')
        log['VB_cream'] = [round(x, 3) for x in b.inputs['Base Color'].default_value]

# deepen VI/VJ shadow + warm cream + darken mortar slightly
for mname, path_note, rgb in (
    ('VI_Freeman_N_shadow_deep_UNVERIFIED', 'VI_shadow_deeper', (0.002, 0.0015, 0.001, 1.0)),
    ('VI_Freeman_N_cream_punch_UNVERIFIED', 'VI_cream_warmer', (0.92, 0.81, 0.59, 1.0)),
    ('VI_Freeman_N_mortar_line_UNVERIFIED', 'VI_mortar_darker', (0.24, 0.18, 0.12, 1.0)),
    ('VJ_Freeman_N_cream_punch_UNVERIFIED', 'VJ_cream_warmer', (0.94, 0.82, 0.60, 1.0)),
    ('VJ_Freeman_N_shadow_deep_UNVERIFIED', 'VJ_shadow_deeper', (0.0018, 0.0014, 0.001, 1.0)),
    ('VJ_Freeman_N_mortar_line_UNVERIFIED', 'VJ_mortar_darker', (0.22, 0.16, 0.11, 1.0)),
):
    mm = bpy.data.materials.get(mname)
    if mm and mm.use_nodes:
        b = mm.node_tree.nodes.get('Principled BSDF')
        if b:
            b.inputs['Base Color'].default_value = rgb
            log['fixes'].append(path_note)

log['n_cream_fills'] = n_fills
log['fixes'].append('N_cream_punch_' + '+'.join(n_fills[:6]) + f'_plus{max(0,len(n_fills)-6)}')

# ---------- C) S/E mid-distance glass + spandrel + mild BP (no bay count change) ----------
sg = bpy.data.materials.get('VG_Freeman_SE_glass_pane_UNVERIFIED')
if sg and sg.use_nodes:
    b = sg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.28
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.010
        b.inputs['Base Color'].default_value = (0.80, 0.92, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.004
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.18
        log['fixes'].append('SE_glass_Alpha0.28_Coat1.0_Spec1.18')
        log['SEglassA'] = 0.28

ss = bpy.data.materials.get('VG_Freeman_SE_spandrel_deep_UNVERIFIED')
if ss and ss.use_nodes:
    b = ss.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.68, 0.26, 0.14, 1.0)
        b.inputs['Roughness'].default_value = 0.60
        log['fixes'].append('SE_spandrel_terracotta_punch')

vbg = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vbg and vbg.use_nodes:
    b = vbg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.36
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.98
            b.inputs['Coat Roughness'].default_value = 0.010
        b.inputs['Base Color'].default_value = (0.72, 0.89, 0.99, 1.0)
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.12
        log['fixes'].append('VB_glass_Alpha0.36_Coat0.98')

# mild SE backplane darken if present (do not delete)
sebp = bpy.data.materials.get('VG_Freeman_SE_backplane_dark_UNVERIFIED')
if sebp and sebp.use_nodes:
    b = sebp.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.010, 0.009, 0.012, 1.0)
        log['fixes'].append('SE_BP_mild_darken')
else:
    for alt in ('VC_Freeman_SE_backplane_dark_UNVERIFIED', 'VG_Freeman_E_backplane_dark_UNVERIFIED',
                'VG_Freeman_S_backplane_dark_UNVERIFIED'):
        am = bpy.data.materials.get(alt)
        if am and am.use_nodes:
            b = am.node_tree.nodes.get('Principled BSDF')
            if b:
                cur = list(b.inputs['Base Color'].default_value)
                b.inputs['Base Color'].default_value = (
                    max(0.006, cur[0] * 0.82), max(0.005, cur[1] * 0.82),
                    max(0.007, cur[2] * 0.82), 1.0)
                log['fixes'].append(f'{alt}_mild_darken')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vk_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vk_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

t_w = centers[min(2, len(centers) - 1)] if centers else L1 * 0.45
c_w = A1 + U1 * t_w
add_cam('VK_CAM_closeup_Freeman_W_glass_grazing',
        (c_w.x + N1.x * 8.6 - U1.x * 1.4, c_w.y + N1.y * 8.6 - U1.y * 1.4, GR + 6.2),
        (c_w.x + N1.x * (OUT + 0.14), c_w.y + N1.y * (OUT + 0.14), GR + 8.4), 44)

scr = A6 + U6 * 6.82
add_cam('VK_CAM_closeup_Freeman_N_cream_punch',
        (scr.x + N6.x * 6.9 - U6.x * 0.30, scr.y + N6.y * 6.9 - U6.y * 0.30, GR + 5.5),
        (scr.x + N6.x * (OUT + 0.19), scr.y + N6.y * (OUT + 0.19), GR + 8.1), 42)

log['cams'] = [o.name for o in cc.objects if o.get('vk_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vk_obj'] = sum(1 for o in bpy.data.objects if o.get('vk_obj'))
log['n_vk_mat'] = sum(1 for m in bpy.data.materials if m.get('vk_mat'))
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }
log['kept_vd_grid'] = bpy.data.objects.get('VD_Freeman_W_pane_grid_UNVERIFIED') is not None
log['kept_vf_sky'] = bpy.data.objects.get('VF_Freeman_W_sky_tint_continuous_UNVERIFIED') is not None
log['kept_vg_S'] = bpy.data.objects.get('VG_Freeman_S_pane_grid_UNVERIFIED') is not None
log['kept_vg_E'] = bpy.data.objects.get('VG_Freeman_E_pane_grid_UNVERIFIED') is not None
log['kept_vj'] = sum(1 for o in bpy.data.objects if o.get('vj_obj'))
log['kept_vi'] = sum(1 for o in bpy.data.objects if o.get('vi_obj'))
json.dump(log, open(DATA + '/vk_main.json', 'w'), indent=2)
print('VK MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
