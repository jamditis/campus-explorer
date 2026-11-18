"""Session vm (Nov 6 2026 ~11:23 PM–~12:1x AM ET, MAIN, day-10 Freeman polish after vl).

Targets (ALL UNVERIFIED; photo language 1096/1114; Joe Nov 6 glass more reflective;
best-judgment after ≥3 silent updates — no ask Joe; SILENT overnight):
  A) Extreme W grazing cream-behind-panes → deepen dark void (darken VC/VG BPs) +
     thicken VL interbay + add VM interbay dark reveals ×10 prouder/wider + push
     reflective glass further (Alpha~0.16 / Coat 1.0 / Spec~1.36 / cooler) + sky-tint
     emiss~3.10. Keep VD pane grid; keep VJ/VK/VL interbay (hide none).
  B) N cream punch vs 1096 — additive pier lips / shadow grooves / storey belts /
     mortar fillets / tip quoins / return belts (over vl). Warmer/brighter VM cream.
     Never cover lettering / terracotta bay / doors / glass / screen. va lettering untouched.
  C) S/E mid-distance: polish existing VG S×3 + E×11 pane mats only (Alpha~0.19 /
     Coat 1.0 / Spec~1.28 / terracotta/BP mild). Do NOT change bay counts (leave UNVERIFIED).
  D) No invented N apron. UH untouched. Webster lawn forever.

Collection: VM_Freeman_polish_UNVERIFIED
Tags: vm_obj / vm_mat / vm_slot_restore / vm_hidden
REVERT=1 restores principled stashes + removes vm objs/mats/colls + restores slots + unhides
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vm'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VM_Freeman_polish_UNVERIFIED'
COL_CAM = 'VM_Freeman_cams'
GLASS_STASH = DATA + '/vm_w_glass_stash.json'
VBGLASS_STASH = DATA + '/vm_vb_glass_stash.json'
SEGLASS_STASH = DATA + '/vm_se_glass_stash.json'
SESPAN_STASH = DATA + '/vm_se_span_stash.json'
SKY_STASH = DATA + '/vm_sky_stash.json'
VBCREAM_STASH = DATA + '/vm_vb_cream_stash.json'
VISHADOW_STASH = DATA + '/vm_vi_shadow_stash.json'
VICREAM_STASH = DATA + '/vm_vi_cream_stash.json'
VIMORTAR_STASH = DATA + '/vm_vi_mortar_stash.json'
SEBP_STASH = DATA + '/vm_se_bp_stash.json'
VJCREAM_STASH = DATA + '/vm_vj_cream_stash.json'
VJSHADOW_STASH = DATA + '/vm_vj_shadow_stash.json'
VJMORTAR_STASH = DATA + '/vm_vj_mortar_stash.json'
VJIBAY_STASH = DATA + '/vm_vj_ibay_stash.json'
VKCREAM_STASH = DATA + '/vm_vk_cream_stash.json'
VKSHADOW_STASH = DATA + '/vm_vk_shadow_stash.json'
VKMORTAR_STASH = DATA + '/vm_vk_mortar_stash.json'
VKIBAY_STASH = DATA + '/vm_vk_ibay_stash.json'
VCBP_STASH = DATA + '/vm_vc_bp_w_stash.json'
VLCREAM_STASH = DATA + '/vm_vl_cream_stash.json'
VLSHADOW_STASH = DATA + '/vm_vl_shadow_stash.json'
VLMORTAR_STASH = DATA + '/vm_vl_mortar_stash.json'
VLIBAY_STASH = DATA + '/vm_vl_ibay_stash.json'

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
        raw = o.get('vm_slot_restore')
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
        del o['vm_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vm_kept_fake'):
            m.use_fake_user = False
            del m['vm_kept_fake']

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
    print('VM restored', mat_name, 'from stash')

def unhide_vm_hidden():
    for o in bpy.data.objects:
        if o.get('vm_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vm_hidden']

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
    restore_principled(VKCREAM_STASH, 'VK_Freeman_N_cream_punch_UNVERIFIED')
    restore_principled(VKSHADOW_STASH, 'VK_Freeman_N_shadow_deep_UNVERIFIED')
    restore_principled(VKMORTAR_STASH, 'VK_Freeman_N_mortar_line_UNVERIFIED')
    restore_principled(VKIBAY_STASH, 'VK_Freeman_W_interbay_dark_UNVERIFIED')
    restore_principled(VCBP_STASH, 'VC_Freeman_W_backplane_dark_UNVERIFIED')
    restore_principled(VLCREAM_STASH, 'VL_Freeman_N_cream_punch_UNVERIFIED')
    restore_principled(VLSHADOW_STASH, 'VL_Freeman_N_shadow_deep_UNVERIFIED')
    restore_principled(VLMORTAR_STASH, 'VL_Freeman_N_mortar_line_UNVERIFIED')
    restore_principled(VLIBAY_STASH, 'VL_Freeman_W_interbay_dark_UNVERIFIED')
    restore_slots()
    unhide_vm_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vm_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vm_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VM REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vm', 'fixes': [], 'GR': GR, 'UNVERIFIED': True, 'SILENT': True,
       'joe_glass': 'more reflective wherever accurate interior not modeled',
       'best_judgment': 'S/E bay pitch/count left UNVERIFIED (mat polish only); W interbay deepen + glass Alpha~0.16/sky~3.10; N cream punch continue; overnight silent'}

# ---- materials ----
def mat_cream_punch(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vm_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.98, 0.86, 0.64, 1.0)
    b.inputs['Roughness'].default_value = 0.60
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.21
    return m

def mat_shadow(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vm_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.0012, 0.001, 0.0008, 1.0)
    b.inputs['Roughness'].default_value = 0.95
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.02
    return m

def mat_mortar(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vm_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.18, 0.13, 0.09, 1.0)
    b.inputs['Roughness'].default_value = 0.97
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.04
    return m

def mat_interbay_dark(name):
    """Near-black reveal between W panes — kills cream stripe at extreme grazing."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vm_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.0016, 0.0013, 0.0011, 1.0)
    b.inputs['Roughness'].default_value = 0.93
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.025
    return m

M_cream = mat_cream_punch('VM_Freeman_N_cream_punch_UNVERIFIED')
M_vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED') or M_cream
M_shadow = mat_shadow('VM_Freeman_N_shadow_deep_UNVERIFIED')
M_mortar = mat_mortar('VM_Freeman_N_mortar_line_UNVERIFIED')
M_ibay = mat_interbay_dark('VM_Freeman_W_interbay_dark_UNVERIFIED')
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
        o['vm_obj'] = 1
        o['UNVERIFIED'] = 'vm Freeman polish; sizes UNVERIFIED; photo 1096/1114; Joe glass reflective'
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
stash_principled(VKCREAM_STASH, 'VK_Freeman_N_cream_punch_UNVERIFIED')
stash_principled(VKSHADOW_STASH, 'VK_Freeman_N_shadow_deep_UNVERIFIED')
stash_principled(VKMORTAR_STASH, 'VK_Freeman_N_mortar_line_UNVERIFIED')
stash_principled(VKIBAY_STASH, 'VK_Freeman_W_interbay_dark_UNVERIFIED')
stash_principled(VCBP_STASH, 'VC_Freeman_W_backplane_dark_UNVERIFIED')
stash_principled(VLCREAM_STASH, 'VL_Freeman_N_cream_punch_UNVERIFIED')
stash_principled(VLSHADOW_STASH, 'VL_Freeman_N_shadow_deep_UNVERIFIED')
stash_principled(VLMORTAR_STASH, 'VL_Freeman_N_mortar_line_UNVERIFIED')
stash_principled(VLIBAY_STASH, 'VL_Freeman_W_interbay_dark_UNVERIFIED')

# ---------- A) W glass more reflective + sky + interbay dark ----------
wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        # clearer than vl polish Alpha 0.185; keep Coat/Spec high (Joe reflective)
        b.inputs['Alpha'].default_value = 0.165
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.002
        b.inputs['Base Color'].default_value = (0.86, 0.95, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.001
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.35
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 1.0
        log['fixes'].append('W_glass_Alpha0.165_Coat1.0_SpecIOR1.35_JoeReflective')
        log['W_glassA'] = 0.165

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 3.05
        b.inputs['Base Color'].default_value = (0.80, 0.90, 1.0, 1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (0.83, 0.92, 1.0, 1.0)
        b.inputs['Alpha'].default_value = 0.26
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.55
            b.inputs['Coat Roughness'].default_value = 0.018
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.55
        log['fixes'].append('sky_tint_emiss3.05_Alpha0.26_mildCoat')

sky_obj = bpy.data.objects.get('VF_Freeman_W_sky_tint_continuous_UNVERIFIED')
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
if sky_obj is None and sky:
    t0, t1 = 2.5, L1 - 2.5
    mid = A1 + U1 * ((t0 + t1) / 2)
    mb = MB('VM_Freeman_W_sky_tint_continuous_UNVERIFIED', [sky], col)
    mb.box(mid + N1 * 0.14, U1, N1, t1 - t0, 0.02, GR + 0.90, TOPZ - 0.40, 0)
    mb.done()
    log['fixes'].append('vl_sky_sheet_rebuild')
else:
    log['fixes'].append('kept_vf_sky_sheet')

# Deepen VJ/VK/VL interbay mats; add slightly prouder/wider VM interbay dark overlays
for mname, note, rgb in (
    ('VJ_Freeman_W_interbay_dark_UNVERIFIED', 'VJ_interbay_darker_nudge', (0.0022, 0.0018, 0.0015, 1.0)),
    ('VK_Freeman_W_interbay_dark_UNVERIFIED', 'VK_interbay_darker_nudge', (0.0018, 0.0015, 0.0012, 1.0)),
    ('VL_Freeman_W_interbay_dark_UNVERIFIED', 'VL_interbay_darker_nudge', (0.0015, 0.0012, 0.0010, 1.0)),
):
    mm = bpy.data.materials.get(mname)
    if mm and mm.use_nodes:
        b = mm.node_tree.nodes.get('Principled BSDF')
        if b:
            b.inputs['Base Color'].default_value = rgb
            log['fixes'].append(note)

# Darken VC W backplane (and SE BP) for deeper void behind panes
for mname, note in (
    ('VC_Freeman_W_backplane_dark_UNVERIFIED', 'VC_W_BP_darker'),
    ('VG_Freeman_SE_backplane_dark_UNVERIFIED', 'VG_SE_BP_darker'),
    ('VC_Freeman_S_backplane_dark_UNVERIFIED', 'VC_S_BP_darker'),
    ('VC_Freeman_E_backplane_dark_UNVERIFIED', 'VC_E_BP_darker'),
    ('VG_Freeman_E_backplane_dark_UNVERIFIED', 'VG_E_BP_darker'),
    ('VG_Freeman_S_backplane_dark_UNVERIFIED', 'VG_S_BP_darker'),
):
    mm = bpy.data.materials.get(mname)
    if mm and mm.use_nodes:
        b = mm.node_tree.nodes.get('Principled BSDF')
        if b:
            cur = list(b.inputs['Base Color'].default_value)
            b.inputs['Base Color'].default_value = (
                max(0.003, cur[0] * 0.62), max(0.0025, cur[1] * 0.62),
                max(0.003, cur[2] * 0.62), 1.0)
            log['fixes'].append(note)

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
    gap_w = max(0.36, pitch - BAY_W - 0.12)  # slightly wider than vl
    c = A1 + U1 * t_mid
    mb = MB(f'VM_Freeman_W_interbay_dark_{i:02d}_UNVERIFIED', [M_ibay, M_shadow], col)
    # prouder/wider than VL to kill residual cream stripe
    mb.box(c + N1 * (OUT + 0.118), U1, N1, gap_w * 1.06, 0.056, GR + 0.60, TOPZ - 0.24, 0)
    for sgn in (-1, 1):
        rc = c + U1 * (sgn * (gap_w / 2 - 0.016))
        mb.box(rc + N1 * (OUT + 0.128), U1, N1, 0.056, 0.032, GR + 0.75, TOPZ - 0.34, 1)
    mb.done()
    interbay.append(i)
log['W_interbay_dark'] = len(interbay)
log['fixes'].append(f'W_interbay_dark_reveals_{len(interbay)}')

# ---------- B) N cream punch (lettering-safe; additive over vl) ----------
e6 = [ed for ed in OSM['edges'] if ed['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
L6 = e6['len']
n_fills = []

# Proud pier face lips further out than vl (vl OUT+0.208)
for t0, t1, tag in ((6.66, 6.97, 'pierW'), (11.68, 11.97, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.10, GR + 3.38, 'lo'), (GR + 6.35, TOPZ - 0.35, 'hi')):
        mb = MB(f'VM_Freeman_N_cream_lip_{tag}_{ztag}_UNVERIFIED', [M_cream, M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.228), U6, N6, w - 0.002, 0.082, z0, z1, 0)
        mb.box(mid + U6 * ((w / 2) * (1 if tag == 'pierW' else -1) * 0.028) + N6 * (OUT + 0.235),
               U6, N6, 0.036, 0.034, z0 + 0.05, z1 - 0.05, 1)
        mb.done()
        n_fills.append(f'lip_{tag}_{ztag}')

# Deeper shadow grooves
for t, tag in ((6.98, 'pierW_E'), (11.67, 'pierE_W')):
    mid = A6 + U6 * t
    for z0, z1, ztag in ((GR + 0.12, GR + 3.32, 'lo'), (GR + 6.38, TOPZ - 0.40, 'hi')):
        mb = MB(f'VM_Freeman_N_shadow_groove_{tag}_{ztag}_UNVERIFIED', [M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.192), U6, N6, 0.065, 0.052, z0, z1, 0)
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
        mb = MB(f'VM_Freeman_N_belt_punch_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.242), U6, N6, w - 0.001, 0.094, z - 0.01, z + 0.155, 0)
        mb.box(mid + N6 * (OUT + 0.250), U6, N6, w - 0.008, 0.040, z - 0.060, z - 0.01, 1)
        mb.done()
        n_fills.append(f'belt_{tag}_{zi}')

# Mid-pier vertical fillet
for t0, t1, tag in ((6.80, 6.84, 'pierW_fillet'), (11.81, 11.85, 'pierE_fillet')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.15, GR + 3.30, 'lo'), (GR + 6.40, TOPZ - 0.50, 'hi')):
        mb = MB(f'VM_Freeman_N_mortar_fillet_{tag}_{ztag}_UNVERIFIED', [M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.238), U6, N6, w, 0.028, z0, z1, 0)
        mb.done()
        n_fills.append(f'fillet_{tag}_{ztag}')

# Quoin outer tips — clear of lettering z≈137.95
let_z0 = 137.55
for t0, t1, tag in ((1.00, 1.62, 'Wtip_outer'), (max(1.0, L6 - 1.60), max(1.4, L6 - 1.00), 'Etip_outer')):
    if t1 <= t0 + 0.05 or t1 > L6 - 0.15 or t0 < 0.2:
        continue
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    mb = MB(f'VM_Freeman_N_quoin_punch_{tag}_UNVERIFIED', [M_vb, M_shadow], col)
    mb.box(mid + N6 * (OUT + 0.228), U6, N6, w, 0.096, GR - 0.02, let_z0 - 0.28, 0)
    mb.box(mid + N6 * (OUT + 0.228), U6, N6, w, 0.096, let_z0 + 0.72, TOPZ - 0.10, 0)
    mb.box(mid + U6 * (w / 2 * 0.85) + N6 * (OUT + 0.235), U6, N6, 0.044, 0.038, GR + 0.2, let_z0 - 0.30, 1)
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
        mb = MB(f'VM_Freeman_N_return_belt_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(cc + N6 * 0.078, N6, U6, recess - 0.10, 0.13, z - 0.01, z + 0.155, 0)
        mb.box(cc + N6 * 0.090, N6, U6, recess - 0.14, 0.042, z - 0.062, z - 0.01, 1)
        mb.done()
        n_fills.append(f'return_belt_{tag}_{zi}')

# Mild VB cream brick punch
vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
if vb and vb.use_nodes:
    b = vb.node_tree.nodes.get('Principled BSDF')
    if b:
        cur = list(b.inputs['Base Color'].default_value)
        b.inputs['Base Color'].default_value = (
            min(0.99, cur[0] * 1.018 + 0.012),
            min(0.92, cur[1] * 1.018 + 0.010),
            min(0.76, cur[2] * 1.012 + 0.006),
            1.0,
        )
        b.inputs['Roughness'].default_value = max(0.46, min(0.80, float(b.inputs['Roughness'].default_value) * 0.92))
        log['fixes'].append('VB_cream_brick_mild_punch')
        log['VB_cream'] = [round(x, 3) for x in b.inputs['Base Color'].default_value]

# deepen VI/VJ/VK shadow + warm cream + darken mortar slightly
for mname, path_note, rgb in (
    ('VI_Freeman_N_shadow_deep_UNVERIFIED', 'VI_shadow_deeper', (0.0012, 0.0010, 0.0008, 1.0)),
    ('VI_Freeman_N_cream_punch_UNVERIFIED', 'VI_cream_warmer', (0.94, 0.83, 0.61, 1.0)),
    ('VI_Freeman_N_mortar_line_UNVERIFIED', 'VI_mortar_darker', (0.20, 0.14, 0.10, 1.0)),
    ('VJ_Freeman_N_cream_punch_UNVERIFIED', 'VJ_cream_warmer', (0.96, 0.84, 0.62, 1.0)),
    ('VJ_Freeman_N_shadow_deep_UNVERIFIED', 'VJ_shadow_deeper', (0.0011, 0.0009, 0.0007, 1.0)),
    ('VJ_Freeman_N_mortar_line_UNVERIFIED', 'VJ_mortar_darker', (0.18, 0.13, 0.09, 1.0)),
    ('VK_Freeman_N_cream_punch_UNVERIFIED', 'VK_cream_warmer', (0.97, 0.85, 0.63, 1.0)),
    ('VK_Freeman_N_shadow_deep_UNVERIFIED', 'VK_shadow_deeper', (0.0010, 0.0008, 0.0006, 1.0)),
    ('VK_Freeman_N_mortar_line_UNVERIFIED', 'VK_mortar_darker', (0.16, 0.12, 0.08, 1.0)),
    ('VL_Freeman_N_cream_punch_UNVERIFIED', 'VL_cream_warmer', (0.98, 0.86, 0.64, 1.0)),
    ('VL_Freeman_N_shadow_deep_UNVERIFIED', 'VL_shadow_deeper', (0.0008, 0.0006, 0.0005, 1.0)),
    ('VL_Freeman_N_mortar_line_UNVERIFIED', 'VL_mortar_darker', (0.14, 0.10, 0.07, 1.0)),
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
        b.inputs['Alpha'].default_value = 0.19
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.006
        b.inputs['Base Color'].default_value = (0.82, 0.93, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.002
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.26
        log['fixes'].append('SE_glass_Alpha0.19_Coat1.0_Spec1.26')
        log['SEglassA'] = 0.19

ss = bpy.data.materials.get('VG_Freeman_SE_spandrel_deep_UNVERIFIED')
if ss and ss.use_nodes:
    b = ss.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.70, 0.27, 0.14, 1.0)
        b.inputs['Roughness'].default_value = 0.58
        log['fixes'].append('SE_spandrel_terracotta_punch')

vbg = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vbg and vbg.use_nodes:
    b = vbg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.28
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.006
        b.inputs['Base Color'].default_value = (0.72, 0.89, 0.99, 1.0)
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.20
        log['fixes'].append('VB_glass_Alpha0.28_Coat1.0')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vm_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vm_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

t_w = centers[min(2, len(centers) - 1)] if centers else L1 * 0.45
c_w = A1 + U1 * t_w
add_cam('VM_CAM_closeup_Freeman_W_glass_grazing',
        (c_w.x + N1.x * 8.5 - U1.x * 1.35, c_w.y + N1.y * 8.5 - U1.y * 1.35, GR + 6.2),
        (c_w.x + N1.x * (OUT + 0.14), c_w.y + N1.y * (OUT + 0.14), GR + 8.4), 44)

scr = A6 + U6 * 6.82
add_cam('VM_CAM_closeup_Freeman_N_cream_punch',
        (scr.x + N6.x * 6.85 - U6.x * 0.28, scr.y + N6.y * 6.85 - U6.y * 0.28, GR + 5.55),
        (scr.x + N6.x * (OUT + 0.21), scr.y + N6.y * (OUT + 0.21), GR + 8.15), 42)

log['cams'] = [o.name for o in cc.objects if o.get('vm_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vm_obj'] = sum(1 for o in bpy.data.objects if o.get('vm_obj'))
log['n_vm_mat'] = sum(1 for m in bpy.data.materials if m.get('vm_mat'))
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
log['kept_vl'] = sum(1 for o in bpy.data.objects if o.get('vl_obj'))
log['kept_vk'] = sum(1 for o in bpy.data.objects if o.get('vk_obj'))
log['kept_vj'] = sum(1 for o in bpy.data.objects if o.get('vj_obj'))
log['kept_vi'] = sum(1 for o in bpy.data.objects if o.get('vi_obj'))
json.dump(log, open(DATA + '/vm_main.json', 'w'), indent=2)
print('VM MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
