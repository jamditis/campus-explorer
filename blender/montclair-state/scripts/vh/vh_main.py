"""Session vh (Nov 6 2026 ~6:21–~7:12 PM ET, MAIN, day-10 Freeman polish after vg) — SILENT.

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) W grazing glass clarity — nudge VD_Freeman_W_glass_pane Alpha slightly below vg ~0.52,
     Coat higher / cooler Base; boost continuous VF sky-tint sheet (stash mats).
  B) N cream punch vs 1096 — additive pier/belt/return/quoin overlays (VB cream language);
     never cover lettering/bay/doors/glass/screen.
  C) Optional S/E mid-distance match — brighten VG SE glass Alpha/Coat + mild spandrel punch.
  D) No invented N apron. UH untouched. Webster lawn forever.

Collection: VH_Freeman_polish_UNVERIFIED
Tags: vh_obj / vh_mat / vh_slot_restore / vh_hidden
REVERT=1 restores principled stashes + removes vh objs/mats/colls + restores slots + unhides
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vh'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VH_Freeman_polish_UNVERIFIED'
COL_CAM = 'VH_Freeman_cams'
GLASS_STASH = DATA + '/vh_w_glass_stash.json'
VBGLASS_STASH = DATA + '/vh_vb_glass_stash.json'
SEGLASS_STASH = DATA + '/vh_se_glass_stash.json'
SESPAN_STASH = DATA + '/vh_se_span_stash.json'
SKY_STASH = DATA + '/vh_sky_stash.json'

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
        raw = o.get('vh_slot_restore')
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
        del o['vh_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vh_kept_fake'):
            m.use_fake_user = False
            del m['vh_kept_fake']

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
    print('VH restored', mat_name, 'from stash')

def unhide_vh_hidden():
    for o in bpy.data.objects:
        if o.get('vh_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vh_hidden']

def revert():
    restore_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
    restore_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
    restore_principled(SEGLASS_STASH, 'VG_Freeman_SE_glass_pane_UNVERIFIED')
    restore_principled(SESPAN_STASH, 'VG_Freeman_SE_spandrel_deep_UNVERIFIED')
    restore_principled(SKY_STASH, 'VF_Freeman_W_sky_tint_UNVERIFIED')
    restore_principled(DATA + '/vh_vb_cream_stash.json', 'VB_Freeman_cream_brick_strong_UNVERIFIED')
    restore_slots()
    unhide_vh_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vh_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vh_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VH REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vh', 'fixes': [], 'GR': GR, 'UNVERIFIED': True, 'SILENT': True}

# ---- materials ----
def mat_cream_punch(name):
    """Punchier cream than VF — warmer brick + slight roughness for mortar read."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vh_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.78, 0.68, 0.52, 1.0)
    b.inputs['Roughness'].default_value = 0.82
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.12
    return m

def mat_shadow(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vh_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.018, 0.015, 0.012, 1.0)
    b.inputs['Roughness'].default_value = 0.88
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.05
    return m

def mat_mortar(name):
    """Thin dark-cream mortar line for pier/belt edge read."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vh_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.55, 0.48, 0.38, 1.0)
    b.inputs['Roughness'].default_value = 0.92
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.08
    return m

M_cream = mat_cream_punch('VH_Freeman_N_cream_punch_UNVERIFIED')
# Prefer VB strong if present for pier faces
M_vb = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED') or M_cream
M_shadow = mat_shadow('VH_Freeman_N_shadow_deep_UNVERIFIED')
M_mortar = mat_mortar('VH_Freeman_N_mortar_line_UNVERIFIED')
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
        o['vh_obj'] = 1
        o['UNVERIFIED'] = 'vh Freeman polish; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- A) W glass clearer + sky tint boost ----------
stash_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
stash_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
stash_principled(SEGLASS_STASH, 'VG_Freeman_SE_glass_pane_UNVERIFIED')
stash_principled(SESPAN_STASH, 'VG_Freeman_SE_spandrel_deep_UNVERIFIED')
stash_principled(SKY_STASH, 'VF_Freeman_W_sky_tint_UNVERIFIED')

wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        # clearer sky read at grazing — lower Alpha than vg 0.52, higher Coat, cooler
        b.inputs['Alpha'].default_value = 0.46
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.92
            b.inputs['Coat Roughness'].default_value = 0.015
        b.inputs['Base Color'].default_value = (0.74, 0.88, 0.98, 1.0)
        b.inputs['Roughness'].default_value = 0.008
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.0
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 1.0
        log['fixes'].append('W_glass_Alpha0.46_Coat0.92_skycooler')
        log['W_glassA'] = 0.46

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        # mild continuous-sheet boost (was emiss ~1.1) — stay soft, not milky slab
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 1.35
        b.inputs['Base Color'].default_value = (0.72, 0.84, 0.97, 1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (0.74, 0.86, 0.98, 1.0)
        b.inputs['Alpha'].default_value = 0.55
        log['fixes'].append('sky_tint_emiss1.35_cooler')

# Ensure continuous sky sheet still present; if missing, rebuild thin sheet
sky_obj = bpy.data.objects.get('VF_Freeman_W_sky_tint_continuous_UNVERIFIED')
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
if sky_obj is None and sky:
    t0, t1 = 2.5, L1 - 2.5
    mid = A1 + U1 * ((t0 + t1) / 2)
    mb = MB('VH_Freeman_W_sky_tint_continuous_UNVERIFIED', [sky], col)
    # OUT+0.14 between BP(~0.06) and glass(~0.22+) — non-coplanar
    mb.box(mid + N1 * 0.14, U1, N1, t1 - t0, 0.02, GR + 0.90, TOPZ - 0.40, 0)
    mb.done()
    log['fixes'].append('vh_sky_sheet_rebuild')
else:
    log['fixes'].append('kept_vf_sky_sheet')

# ---------- B) N cream punch (lettering-safe) ----------
e6 = [ed for ed in OSM['edges'] if ed['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
# lettering band ~GR+3.5..GR+6.2 — skip overlays there on pier faces near lettering
# pier outer tips: (6.68,6.95) and (11.70,11.95)
n_fills = []
# proud pier face lips (thicker than vg tips) below/above lettering
for t0, t1, tag in ((6.68, 6.95, 'pierW'), (11.70, 11.95, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for z0, z1, ztag in ((GR + 0.12, GR + 3.40, 'lo'), (GR + 6.30, TOPZ - 0.40, 'hi')):
        mb = MB(f'VH_Freeman_N_cream_lip_{tag}_{ztag}_UNVERIFIED', [M_vb, M_mortar], col)
        mb.box(mid + N6 * (OUT + 0.118), U6, N6, w - 0.008, 0.055, z0, z1, 0)
        # thin mortar edge on curtain side
        mb.box(mid + U6 * ((w / 2) * (1 if tag == 'pierW' else -1) * 0.02) + N6 * (OUT + 0.125),
               U6, N6, 0.028, 0.025, z0 + 0.05, z1 - 0.05, 1)
        mb.done()
        n_fills.append(f'lip_{tag}_{ztag}')
# deeper shadow grooves toward curtain (additive over vg/vf)
for t, tag, toward in ((6.96, 'pierW_E', +1), (11.69, 'pierE_W', -1)):
    mid = A6 + U6 * t
    for z0, z1, ztag in ((GR + 0.15, GR + 3.35, 'lo'), (GR + 6.35, TOPZ - 0.45, 'hi')):
        mb = MB(f'VH_Freeman_N_shadow_groove_{tag}_{ztag}_UNVERIFIED', [M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.108), U6, N6, 0.045, 0.035, z0, z1, 0)
        mb.done()
        n_fills.append(f'shadow_{tag}_{ztag}')
# storey belt punch — pier faces only, thicker/proud + under-shadow
belt_zs = [GR + 3.48, GR + 6.88, GR + 10.28, TOPZ - 0.68]
for t0, t1, tag in ((6.68, 6.95, 'pierW'), (11.70, 11.95, 'pierE')):
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    for zi, z in enumerate(belt_zs):
        # skip belt that lands inside lettering band for mid pier (zi0 near canopy OK; zi1 is lettering)
        if zi == 1:
            continue  # GR+6.88 is near lettering top — skip to keep band clear
        mb = MB(f'VH_Freeman_N_belt_punch_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(mid + N6 * (OUT + 0.135), U6, N6, w - 0.004, 0.07, z - 0.01, z + 0.12, 0)
        mb.box(mid + N6 * (OUT + 0.142), U6, N6, w - 0.012, 0.03, z - 0.045, z - 0.01, 1)
        mb.done()
        n_fills.append(f'belt_{tag}_{zi}')
# quoin outer tips — clear of lettering z≈137.95
let_z0 = 137.55
for t0, t1, tag in ((1.10, 1.55, 'Wtip_outer'), (16.90, 17.35, 'Etip_outer')):
    # clamp to edge length
    if t1 > e6['len'] - 0.3 or t0 < 0.3:
        continue
    w = t1 - t0
    mid = A6 + U6 * ((t0 + t1) / 2)
    mb = MB(f'VH_Freeman_N_quoin_punch_{tag}_UNVERIFIED', [M_vb, M_shadow], col)
    mb.box(mid + N6 * (OUT + 0.122), U6, N6, w, 0.07, GR - 0.02, let_z0 - 0.22, 0)
    mb.box(mid + N6 * (OUT + 0.122), U6, N6, w, 0.07, let_z0 + 0.65, TOPZ - 0.12, 0)
    mb.box(mid + U6 * (w / 2 * 0.9) + N6 * (OUT + 0.128), U6, N6, 0.035, 0.03, GR + 0.2, let_z0 - 0.25, 1)
    mb.done()
    n_fills.append(f'quoin_{tag}')
# return wall shelves (entrance recess returns) — clear of doors/glass/screen
T_ENT0, T_ENT1 = 5.58, 12.85
ew = T_ENT1 - T_ENT0
ec = A6 + U6 * ((T_ENT0 + T_ENT1) / 2)
recess = 0.85
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U6 * (sgn * ew / 2) + U6 * (-sgn * 0.05)
    cc = rc + N6 * (OUT - recess / 2)
    for zi, z in enumerate((GR + 3.42, GR + 6.82, GR + 10.22)):
        # zi1 (~GR+6.82) near lettering height on returns — keep but small + set back from lettering face
        mb = MB(f'VH_Freeman_N_return_belt_{tag}_{zi}_UNVERIFIED', [M_vb, M_shadow], col)
        mb.box(cc + N6 * 0.045, N6, U6, recess - 0.16, 0.09, z - 0.01, z + 0.12, 0)
        mb.box(cc + N6 * 0.055, N6, U6, recess - 0.20, 0.032, z - 0.05, z - 0.01, 1)
        mb.done()
        n_fills.append(f'return_belt_{tag}_{zi}')

log['n_cream_fills'] = n_fills
log['fixes'].append('N_cream_punch_' + '+'.join(n_fills[:6]) + f'_plus{max(0,len(n_fills)-6)}')

# ---------- C) S/E mid-distance glass + spandrel ----------
sg = bpy.data.materials.get('VG_Freeman_SE_glass_pane_UNVERIFIED')
if sg and sg.use_nodes:
    b = sg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.48
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.85
            b.inputs['Coat Roughness'].default_value = 0.02
        b.inputs['Base Color'].default_value = (0.70, 0.85, 0.96, 1.0)
        b.inputs['Roughness'].default_value = 0.010
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.90
        log['fixes'].append('SE_glass_Alpha0.48_Coat0.85')
        log['SEglassA'] = 0.48

ss = bpy.data.materials.get('VG_Freeman_SE_spandrel_deep_UNVERIFIED')
if ss and ss.use_nodes:
    b = ss.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.60, 0.22, 0.12, 1.0)
        b.inputs['Roughness'].default_value = 0.68
        log['fixes'].append('SE_spandrel_terracotta_brighter')

vbg = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vbg and vbg.use_nodes:
    b = vbg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.50
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.80
        b.inputs['Base Color'].default_value = (0.66, 0.82, 0.96, 1.0)
        log['fixes'].append('VB_glass_Alpha0.50_Coat0.80')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vh_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vh_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# W glass grazing closeup (primary A detail)
centers = []
for i in range(max(1, int((L1 - 4.0) / 3.6))):
    t = 2.0 + 3.6 * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)
t_w = centers[max(0, len(centers) // 3)] if centers else L1 * 0.4
c_w = A1 + U1 * t_w
add_cam('VH_CAM_closeup_Freeman_W_glass_grazing',
        (c_w.x + N1.x * 9.5 - U1.x * 1.1, c_w.y + N1.y * 9.5 - U1.y * 1.1, GR + 5.2),
        (c_w.x + N1.x * (OUT + 0.12), c_w.y + N1.y * (OUT + 0.12), GR + 7.2), 40)

# N cream punch closeup (primary B detail)
scr = A6 + U6 * 6.85
add_cam('VH_CAM_closeup_Freeman_N_cream_punch',
        (scr.x + N6.x * 10.0 - U6.x * 1.8, scr.y + N6.y * 10.0 - U6.y * 1.8, GR + 4.0),
        (scr.x, scr.y, GR + 7.0), 38)

log['cams'] = [o.name for o in cc.objects if o.get('vh_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vh_obj'] = sum(1 for o in bpy.data.objects if o.get('vh_obj'))
log['n_vh_mat'] = sum(1 for m in bpy.data.materials if m.get('vh_mat'))
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
json.dump(log, open(DATA + '/vh_main.json', 'w'), indent=2)
print('VH MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
