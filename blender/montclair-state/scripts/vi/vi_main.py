"""Session vi (Nov 6 2026 ~7:22–~8:12 PM ET, MAIN, day-10 Freeman polish after vh).

Targets (ALL UNVERIFIED; photo language 1096/1114; Joe Nov 6 glass more reflective):
  A) W glass more reflective at grazing — Coat~1.0 / Spec IOR~1.15 / Alpha~0.36 clearer;
     cooler Base; mild VF sky-tint boost (stash mats). Keep VC/VG dark BPs.
  B) N cream punch vs 1096 — additive pier/fillet/belt/return/quoin overlays (VB cream);
     never cover lettering/bay/doors/glass/screen.
  C) Optional S/E mid-distance — mild Alpha/Coat/terracotta on existing VG SE mats only.
  D) No invented N apron. UH untouched. Webster lawn forever.

Collection: VI_Freeman_polish_UNVERIFIED
Tags: vi_obj / vi_mat / vi_slot_restore / vi_hidden
REVERT=1 restores principled stashes + removes vi objs/mats/colls + restores slots + unhides
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vi'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VI_Freeman_polish_UNVERIFIED'
COL_CAM = 'VI_Freeman_cams'
GLASS_STASH = DATA + '/vi_w_glass_stash.json'
VBGLASS_STASH = DATA + '/vi_vb_glass_stash.json'
SEGLASS_STASH = DATA + '/vi_se_glass_stash.json'
SESPAN_STASH = DATA + '/vi_se_span_stash.json'
SKY_STASH = DATA + '/vi_sky_stash.json'
VBCREAM_STASH = DATA + '/vi_vb_cream_stash.json'
VHSHADOW_STASH = DATA + '/vi_vh_shadow_stash.json'

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
        raw = o.get('vi_slot_restore')
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
        del o['vi_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vi_kept_fake'):
            m.use_fake_user = False
            del m['vi_kept_fake']

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
    print('VI restored', mat_name, 'from stash')

def unhide_vi_hidden():
    for o in bpy.data.objects:
        if o.get('vi_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vi_hidden']

def revert():
    restore_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
    restore_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
    restore_principled(SEGLASS_STASH, 'VG_Freeman_SE_glass_pane_UNVERIFIED')
    restore_principled(SESPAN_STASH, 'VG_Freeman_SE_spandrel_deep_UNVERIFIED')
    restore_principled(SKY_STASH, 'VF_Freeman_W_sky_tint_UNVERIFIED')
    restore_principled(VBCREAM_STASH, 'VB_Freeman_cream_brick_strong_UNVERIFIED')
    restore_principled(VHSHADOW_STASH, 'VH_Freeman_N_shadow_deep_UNVERIFIED')
    restore_slots()
    unhide_vi_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vi_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vi_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VI REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vi', 'fixes': [], 'GR': GR, 'UNVERIFIED': True, 'SILENT': True,
       'joe_glass': 'more reflective wherever accurate interior not modeled'}

# ---- materials ----
def mat_cream_punch(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vi_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    # punchier / warmer vs soft mid cream — reads at entrance eye
    b.inputs['Base Color'].default_value = (0.86, 0.75, 0.56, 1.0)
    b.inputs['Roughness'].default_value = 0.74
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.14
    return m

def mat_shadow(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vi_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.008, 0.006, 0.005, 1.0)
    b.inputs['Roughness'].default_value = 0.90
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.04
    return m

def mat_mortar(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vi_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.38, 0.32, 0.24, 1.0)
    b.inputs['Roughness'].default_value = 0.94
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.06
    return m

M_cream = mat_cream_punch('VI_Freeman_N_cream_punch_UNVERIFIED')
M_vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED') or M_cream
M_shadow = mat_shadow('VI_Freeman_N_shadow_deep_UNVERIFIED')
M_mortar = mat_mortar('VI_Freeman_N_mortar_line_UNVERIFIED')
log['fixes'].append('mats_cream_shadow_mortar')

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
        o['vi_obj'] = 1
        o['UNVERIFIED'] = 'vi Freeman polish; sizes UNVERIFIED; photo 1096/1114; Joe glass reflective'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- A) W glass more reflective (Joe) + sky tint ----------
stash_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
stash_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
stash_principled(SEGLASS_STASH, 'VG_Freeman_SE_glass_pane_UNVERIFIED')
stash_principled(SESPAN_STASH, 'VG_Freeman_SE_spandrel_deep_UNVERIFIED')
stash_principled(SKY_STASH, 'VF_Freeman_W_sky_tint_UNVERIFIED')
stash_principled(VBCREAM_STASH, 'VB_Freeman_cream_brick_strong_UNVERIFIED')
stash_principled(VHSHADOW_STASH, 'VH_Freeman_N_shadow_deep_UNVERIFIED')

wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        # Joe: a little more reflective — prefer sky/coat over empty cream shell
        # clearer than vh Alpha 0.40; high Coat + Spec IOR
        b.inputs['Alpha'].default_value = 0.36
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.01
        b.inputs['Base Color'].default_value = (0.82, 0.93, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.004
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.15
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 1.0
        log['fixes'].append('W_glass_Alpha0.36_Coat1.0_SpecIOR1.15_JoeReflective')
        log['W_glassA'] = 0.36

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        # mild continuous-sheet boost — avoid milky wash of mid-tones
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 1.85
        b.inputs['Base Color'].default_value = (0.78, 0.89, 0.99, 1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (0.80, 0.90, 1.0, 1.0)
        b.inputs['Alpha'].default_value = 0.42
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.35
            b.inputs['Coat Roughness'].default_value = 0.04
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.35
        log['fixes'].append('sky_tint_emiss1.85_Alpha0.42_mildCoat')

# Ensure continuous sky sheet still present
sky_obj = bpy.data.objects.get('VF_Freeman_W_sky_tint_continuous_UNVERIFIED')
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
if sky_obj is None and sky:
    t0, t1 = 2.5, L1 - 2.5
    mid = A1 + U1 * ((t0 + t1) / 2)
    mb = MB('VI_Freeman_W_sky_tint_continuous_UNVERIFIED', [sky], col)
    mb.box(mid + N1 * 0.14, U1, N1, t1 - t0, 0.02, GR + 0.90, TOPZ - 0.40, 0)
    mb.done()
    log['fixes'].append('vi_sky_sheet_rebuild')
else:
    log['fixes'].append('kept_vf_sky_sheet')

# ---------- B) N cream punch (lettering-safe; additive over vh) ----------
e6 = [ed for ed in OSM['edges'] if ed['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
L6 = e6['len']
n_fills = []

# Proud pier face lips further out than vh (vh OUT+0.118) — lettering band clear
for t0, t1, tag in ((6.66, 6.97, 'pierW'), (11.68, 11.97, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.10, GR + 3.38, 'lo'), (GR + 6.35, TOPZ - 0.35, 'hi')):
        mb = MB(f'VI_Freeman_N_cream_lip_{tag}_{ztag}_UNVERIFIED', [M_vb, M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.148), U6, N6, w - 0.006, 0.065, z0, z1, 0)
        mb.box(mid + U6 * ((w / 2) * (1 if tag == 'pierW' else -1) * 0.025) + N6 * (OUT + 0.155),
               U6, N6, 0.030, 0.028, z0 + 0.05, z1 - 0.05, 1)
        mb.done()
        n_fills.append(f'lip_{tag}_{ztag}')

# Deeper shadow grooves toward curtain (outboard of vh)
for t, tag in ((6.98, 'pierW_E'), (11.67, 'pierE_W')):
    mid = A6 + U6 * t
    for z0, z1, ztag in ((GR + 0.12, GR + 3.32, 'lo'), (GR + 6.38, TOPZ - 0.40, 'hi')):
        mb = MB(f'VI_Freeman_N_shadow_groove_{tag}_{ztag}_UNVERIFIED', [M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.132), U6, N6, 0.050, 0.040, z0, z1, 0)
        mb.done()
        n_fills.append(f'shadow_{tag}_{ztag}')

# Storey belt punch — pier faces; skip zi that lands in lettering band
belt_zs = [GR + 3.45, GR + 6.85, GR + 10.25, TOPZ - 0.62]
for t0, t1, tag in ((6.66, 6.97, 'pierW'), (11.68, 11.97, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for zi, z in enumerate(belt_zs):
        if zi == 1:
            continue  # keep lettering band clear
        mb = MB(f'VI_Freeman_N_belt_punch_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.165), U6, N6, w - 0.002, 0.078, z - 0.01, z + 0.135, 0)
        mb.box(mid + N6 * (OUT + 0.172), U6, N6, w - 0.010, 0.034, z - 0.050, z - 0.01, 1)
        mb.done()
        n_fills.append(f'belt_{tag}_{zi}')

# Mid-pier vertical fillet (mortar read) — lettering-safe z ranges only
for t0, t1, tag in ((6.80, 6.84, 'pierW_fillet'), (11.81, 11.85, 'pierE_fillet')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.15, GR + 3.30, 'lo'), (GR + 6.40, TOPZ - 0.50, 'hi')):
        mb = MB(f'VI_Freeman_N_mortar_fillet_{tag}_{ztag}_UNVERIFIED', [M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.158), U6, N6, w, 0.022, z0, z1, 0)
        mb.done()
        n_fills.append(f'fillet_{tag}_{ztag}')

# Quoin outer tips — both ends; clear of lettering z≈137.95
let_z0 = 137.55
for t0, t1, tag in ((1.05, 1.58, 'Wtip_outer'), (max(1.0, L6 - 1.55), max(1.4, L6 - 1.05), 'Etip_outer')):
    if t1 <= t0 + 0.05 or t1 > L6 - 0.15 or t0 < 0.2:
        continue
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    mb = MB(f'VI_Freeman_N_quoin_punch_{tag}_UNVERIFIED', [M_vb, M_shadow], col)
    mb.box(mid + N6 * (OUT + 0.150), U6, N6, w, 0.078, GR - 0.02, let_z0 - 0.25, 0)
    mb.box(mid + N6 * (OUT + 0.150), U6, N6, w, 0.078, let_z0 + 0.70, TOPZ - 0.10, 0)
    mb.box(mid + U6 * (w / 2 * 0.85) + N6 * (OUT + 0.156), U6, N6, 0.038, 0.032, GR + 0.2, let_z0 - 0.28, 1)
    mb.done()
    n_fills.append(f'quoin_{tag}')

# Return wall shelves — clear of doors/glass/screen; set back from lettering face
T_ENT0, T_ENT1 = 5.58, 12.85
ew = T_ENT1 - T_ENT0
ec = A6 + U6 * ((T_ENT0 + T_ENT1) / 2)
recess = 0.85
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U6 * (sgn * ew / 2) + U6 * (-sgn * 0.05)
    cc = rc + N6 * (OUT - recess / 2)
    for zi, z in enumerate((GR + 3.40, GR + 6.80, GR + 10.20)):
        mb = MB(f'VI_Freeman_N_return_belt_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(cc + N6 * 0.055, N6, U6, recess - 0.14, 0.10, z - 0.01, z + 0.135, 0)
        mb.box(cc + N6 * 0.065, N6, U6, recess - 0.18, 0.035, z - 0.055, z - 0.01, 1)
        mb.done()
        n_fills.append(f'return_belt_{tag}_{zi}')

# Mild VB cream brick punch (stash already taken)
vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
if vb and vb.use_nodes:
    b = vb.node_tree.nodes.get('Principled BSDF')
    if b:
        cur = list(b.inputs['Base Color'].default_value)
        # slightly warmer brick punch at entrance eye (not milky)
        b.inputs['Base Color'].default_value = (
            min(0.94, cur[0] * 1.04 + 0.02),
            min(0.86, cur[1] * 1.03 + 0.015),
            min(0.68, cur[2] * 1.02 + 0.01),
            1.0,
        )
        b.inputs['Roughness'].default_value = max(0.55, min(0.88, float(b.inputs['Roughness'].default_value) * 0.97))
        log['fixes'].append('VB_cream_brick_mild_punch')
        log['VB_cream'] = [round(x, 3) for x in b.inputs['Base Color'].default_value]

# deepen existing VH shadow mat slightly (stashed)
vhs = bpy.data.materials.get('VH_Freeman_N_shadow_deep_UNVERIFIED')
if vhs and vhs.use_nodes:
    b = vhs.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.006, 0.005, 0.004, 1.0)
        log['fixes'].append('VH_shadow_deeper')

log['n_cream_fills'] = n_fills
log['fixes'].append('N_cream_punch_' + '+'.join(n_fills[:6]) + f'_plus{max(0,len(n_fills)-6)}')

# ---------- C) S/E mid-distance glass + spandrel ----------
sg = bpy.data.materials.get('VG_Freeman_SE_glass_pane_UNVERIFIED')
if sg and sg.use_nodes:
    b = sg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.38
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.95
            b.inputs['Coat Roughness'].default_value = 0.015
        b.inputs['Base Color'].default_value = (0.78, 0.91, 0.99, 1.0)
        b.inputs['Roughness'].default_value = 0.006
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.05
        log['fixes'].append('SE_glass_Alpha0.38_Coat0.95_Spec1.05')
        log['SEglassA'] = 0.38

ss = bpy.data.materials.get('VG_Freeman_SE_spandrel_deep_UNVERIFIED')
if ss and ss.use_nodes:
    b = ss.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.64, 0.24, 0.13, 1.0)
        b.inputs['Roughness'].default_value = 0.64
        log['fixes'].append('SE_spandrel_terracotta_punch')

vbg = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vbg and vbg.use_nodes:
    b = vbg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.42
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.92
            b.inputs['Coat Roughness'].default_value = 0.015
        b.inputs['Base Color'].default_value = (0.72, 0.88, 0.98, 1.0)
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.05
        log['fixes'].append('VB_glass_Alpha0.42_Coat0.92')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vi_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vi_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

centers = []
for i in range(max(1, int((L1 - 4.0) / 3.6))):
    t = 2.0 + 3.6 * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)
t_w = centers[max(0, len(centers) // 3)] if centers else L1 * 0.4
c_w = A1 + U1 * t_w
# Extreme grazing W glass closeup — flatter angle for coat/sky read
add_cam('VI_CAM_closeup_Freeman_W_glass_grazing',
        (c_w.x + N1.x * 7.2 - U1.x * 2.4, c_w.y + N1.y * 7.2 - U1.y * 2.4, GR + 5.5),
        (c_w.x + N1.x * (OUT + 0.14), c_w.y + N1.y * (OUT + 0.14), GR + 7.8), 48)

# N cream punch closeup
scr = A6 + U6 * 6.85
add_cam('VI_CAM_closeup_Freeman_N_cream_punch',
        (scr.x + N6.x * 9.0 - U6.x * 1.5, scr.y + N6.y * 9.0 - U6.y * 1.5, GR + 4.2),
        (scr.x + N6.x * (OUT + 0.12), scr.y + N6.y * (OUT + 0.12), GR + 7.2), 42)

log['cams'] = [o.name for o in cc.objects if o.get('vi_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vi_obj'] = sum(1 for o in bpy.data.objects if o.get('vi_obj'))
log['n_vi_mat'] = sum(1 for m in bpy.data.materials if m.get('vi_mat'))
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
log['kept_vh'] = sum(1 for o in bpy.data.objects if o.get('vh_obj'))
json.dump(log, open(DATA + '/vi_main.json', 'w'), indent=2)
print('VI MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
