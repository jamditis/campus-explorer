"""Session vf (Nov 6 2026 ~4:17–~5:12 PM ET, MAIN, day-10 Freeman polish after ve).

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) W glass grazing — push VD_Freeman_W_glass_pane toward clearer sky/mirror read
     (Alpha ~0.58–0.65, Coat ~0.75, cooler Base, low Rough); thin sky-tint cards
     behind glass / in front of VC backplanes if needed; keep vd pane grid + VC BPs.
  B) N cream eye punch — stronger pier returns / shadow grooves / storey belts / quoins
     on N mid-wall cream; NEVER cover GRACE H. FREEMAN HALL, terracotta bay, doors,
     glass, or screen face.
  C) Optional mild mullion/frame contrast. No apron. No UH/Webster edits.

Collection: VF_Freeman_polish_UNVERIFIED
Tags: vf_obj / vf_mat / vf_slot_restore / vf_hidden
REVERT=1 restores slots + unhides + removes vf objs/mats/colls + restores glass/spandrel/frame stash
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vf'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VF_Freeman_polish_UNVERIFIED'
COL_CAM = 'VF_Freeman_cams'
GLASS_STASH = DATA + '/vf_glass_stash.json'
SPAN_STASH = DATA + '/vf_spandrel_stash.json'
VBGLASS_STASH = DATA + '/vf_vb_glass_stash.json'
FRAME_STASH = DATA + '/vf_frame_stash.json'
REVEAL_STASH = DATA + '/vf_reveal_stash.json'

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
        raw = o.get('vf_slot_restore')
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
        del o['vf_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vf_kept_fake'):
            m.use_fake_user = False
            del m['vf_kept_fake']

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
    print('VF restored', mat_name, 'from stash')

def unhide_vf_hidden():
    for o in bpy.data.objects:
        if o.get('vf_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vf_hidden']

def revert():
    restore_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
    restore_principled(SPAN_STASH, 'VD_Freeman_W_spandrel_deep_UNVERIFIED')
    restore_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
    restore_principled(FRAME_STASH, 'UV_Freeman_window_frame_darkred_UNVERIFIED')
    restore_principled(REVEAL_STASH, 'VD_Freeman_W_reveal_dark_UNVERIFIED')
    restore_principled(DATA + '/vf_vc_bp_stash.json', 'VC_Freeman_glass_backplane_dark_UNVERIFIED')
    restore_slots()
    unhide_vf_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vf_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vf_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VF REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vf', 'fixes': [], 'GR': GR, 'UNVERIFIED': True}

# ---- materials ----
def make_sky_tint(name):
    """Bright cool sky card — visible through glass as soft sky read (not milky)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vf_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.55, 0.72, 0.92, 1.0)
    b.inputs['Roughness'].default_value = 0.85
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.05
    if 'Emission Color' in b.inputs:
        b.inputs['Emission Color'].default_value = (0.62, 0.78, 0.98, 1.0)
    if 'Emission Strength' in b.inputs:
        b.inputs['Emission Strength'].default_value = 0.55
    return m

def make_cream_punch(name):
    """Warmer/shadowed cream for N pier depth overlays — punchier than VE soft."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vf_mat'] = 1
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (400, 200)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.location = (100, 200); b.name = 'Principled BSDF'
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.location = (-500, 200)
    noise.inputs['Scale'].default_value = 14.0
    noise.inputs['Detail'].default_value = 7.0
    noise.inputs['Roughness'].default_value = 0.5
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.location = (-250, 200)
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (0.50, 0.44, 0.33, 1)
    ramp.color_ramp.elements[1].position = 0.72
    ramp.color_ramp.elements[1].color = (0.68, 0.62, 0.48, 1)
    bump = nt.nodes.new('ShaderNodeBump'); bump.location = (-50, 50)
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.003
    texcoord = nt.nodes.new('ShaderNodeTexCoord'); texcoord.location = (-700, 200)
    mapping = nt.nodes.new('ShaderNodeMapping'); mapping.location = (-600, 200)
    nt.links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    b.inputs['Roughness'].default_value = 0.86
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.16
    return m

def make_shadow_punch(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vf_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.14, 0.11, 0.09, 1.0)
    b.inputs['Roughness'].default_value = 0.92
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.04
    return m

M_sky = make_sky_tint('VF_Freeman_W_sky_tint_UNVERIFIED')
M_cream = make_cream_punch('VF_Freeman_N_cream_punch_UNVERIFIED')
M_shadow = make_shadow_punch('VF_Freeman_shadow_punch_UNVERIFIED')
log['fixes'].append('mats_sky_cream_punch_shadow')

# Stash + polish glass / spandrel / frame
stash_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
stash_principled(SPAN_STASH, 'VD_Freeman_W_spandrel_deep_UNVERIFIED')
stash_principled(VBGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
stash_principled(FRAME_STASH, 'UV_Freeman_window_frame_darkred_UNVERIFIED')
stash_principled(REVEAL_STASH, 'VD_Freeman_W_reveal_dark_UNVERIFIED')

g = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b = g.node_tree.nodes.get('Principled BSDF')
    if b:
        # clearer sky/mirror at grazing — higher alpha + coat, cooler, not milky
        b.inputs['Base Color'].default_value = (0.48, 0.68, 0.90, 1.0)
        b.inputs['Alpha'].default_value = 0.62
        b.inputs['Roughness'].default_value = 0.012
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 1.0
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.78
            b.inputs['Coat Roughness'].default_value = 0.015
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.0
        if 'IOR' in b.inputs:
            b.inputs['IOR'].default_value = 1.52
        log['fixes'].append('VD_W_glass_grazing_alpha0.62_coat0.78')

s = bpy.data.materials.get('VD_Freeman_W_spandrel_deep_UNVERIFIED')
if s and s.use_nodes:
    b = s.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.74, 0.36, 0.17, 1.0)
        b.inputs['Roughness'].default_value = 0.68
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.24
        log['fixes'].append('VD_spandrel_punch_terracotta')

vg = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vg and vg.use_nodes:
    b = vg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.55, 0.74, 0.92, 1.0)
        if 'Alpha' in b.inputs:
            b.inputs['Alpha'].default_value = 0.52
        b.inputs['Roughness'].default_value = 0.015
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.60
            b.inputs['Coat Roughness'].default_value = 0.02
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.95
        log['fixes'].append('VB_glass_cool_SE_alpha0.52_coat0.60')

# C) mild mullion/frame contrast
fr = bpy.data.materials.get('UV_Freeman_window_frame_darkred_UNVERIFIED')
if fr and fr.use_nodes:
    b = fr.node_tree.nodes.get('Principled BSDF')
    if b:
        # slightly darker bronze so panes pop against cream
        cur = list(b.inputs['Base Color'].default_value)
        b.inputs['Base Color'].default_value = (max(0.05, cur[0]*0.72), max(0.04, cur[1]*0.70), max(0.03, cur[2]*0.68), 1.0)
        b.inputs['Roughness'].default_value = min(0.55, max(0.35, b.inputs['Roughness'].default_value))
        log['fixes'].append('frame_darker_mullion_contrast')

rv = bpy.data.materials.get('VD_Freeman_W_reveal_dark_UNVERIFIED')
if rv and rv.use_nodes:
    b = rv.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.10, 0.08, 0.07, 1.0)
        log['fixes'].append('reveal_darker')

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
        o['vf_obj'] = 1
        o['UNVERIFIED'] = 'vf Freeman polish; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- A) Sky-tint cards behind glass / in front of VC backplanes ----------
# Pane glass ~N-off 0.25; VC BP ~0.06 → place tint cards at ~0.14 (no coplanar)
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
pitch = 3.6
BAY_W = 1.10
centers = []
for i in range(max(1, int((L1 - 4.0) / pitch))):
    t = 2.0 + pitch * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)

sky_cards = []
SKY_N = 0.14  # between BP(~0.06) and glass(~0.25)
for i, t in enumerate(centers):
    c = A1 + U1 * t
    mb = MB(f'VF_Freeman_W_sky_tint_{i:02d}_UNVERIFIED', [M_sky], col)
    # thin card filling bay glass stack (leave spandrel bands somewhat; full-height soft sky)
    mb.box(c + N1 * SKY_N, U1, N1, BAY_W, 0.018, GR + 0.85, TOPZ - 0.45, 0)
    mb.done()
    sky_cards.append(i)
log['W_sky_tint'] = len(sky_cards)
log['fixes'].append(f'W_sky_tint_cards_{len(sky_cards)}')

# Soften remaining heavy interbay cream stripe if VE lips still read heavy:
# slightly proud soft cream wash over interbay gaps (lighter than VE shadow)
# — skip inventing more lips; sky cards + glass are primary A fix.

# ---------- B) N cream eye punch ----------
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A = Vector((e6['a'][0], e6['a'][1], 0))
T_ENT0, T_ENT1 = 5.58, 12.85
ew = T_ENT1 - T_ENT0
ec = A + U * ((T_ENT0 + T_ENT1) / 2)
recess = 0.85
can_z1 = GR + 3.85
fills = []

# Deeper pier side returns (proud of VE returns, still clear of curtain glass)
for t_face, tag, toward in (
    (6.95, 'pierW', +1),
    (11.70, 'pierE', -1),
):
    mid = A + U * t_face
    mb = MB(f'VF_Freeman_N_pier_return_punch_{tag}_UNVERIFIED', [M_cream, M_shadow], col)
    cc = mid + N * (OUT - recess / 2)
    mb.box(cc + N * 0.02, N, U, recess - 0.12, 0.09, GR - 0.02, TOPZ - 0.12, 0)
    # dark edge lip toward curtain
    edge = mid + U * (toward * 0.04) + N * (OUT - 0.08)
    mb.box(edge, U, N, 0.04, 0.04, GR + 0.15, TOPZ - 0.25, 1)
    mb.done()
    fills.append(f'return_punch_{tag}')

# Stronger shadow grooves (thicker/darker than VE)
for te, tag in ((6.94, 'pierW_E'), (11.71, 'pierE_W')):
    mid = A + U * te
    mb = MB(f'VF_Freeman_N_shadow_punch_{tag}_UNVERIFIED', [M_shadow], col)
    mb.box(mid + N * (OUT + 0.115), U, N, 0.05, 0.04, GR - 0.02, TOPZ - 0.18, 0)
    mb.done()
    fills.append(f'shadow_punch_{tag}')

# Punchier storey belts — thicker + more proud + under-shadow
belt_zs = [GR + 3.50, GR + 6.90, GR + 10.30, TOPZ - 0.70]
for t0, t1, tag in (
    (6.68, 6.95, 'pierW'),
    (11.70, 11.95, 'pierE'),
    (7.00, 7.45, 'midW'),
    (11.35, 11.70, 'midE'),
):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    for zi, z in enumerate(belt_zs):
        if tag.startswith('mid') and z < can_z1 + 0.2:
            continue
        mb = MB(f'VF_Freeman_N_belt_punch_{tag}_{zi}_UNVERIFIED', [M_cream, M_shadow], col)
        mb.box(mid + N * (OUT + 0.125), U, N, w - 0.005, 0.06, z - 0.01, z + 0.10, 0)
        mb.box(mid + N * (OUT + 0.132), U, N, w - 0.015, 0.028, z - 0.04, z - 0.01, 1)
        mb.done()
        fills.append(f'belt_punch_{tag}_{zi}')

# Return wall shelves punch
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U * (sgn * ew / 2) + U * (-sgn * 0.05)
    cc = rc + N * (OUT - recess / 2)
    for zi, z in enumerate((GR + 3.45, GR + 6.85, GR + 10.25)):
        mb = MB(f'VF_Freeman_N_return_belt_punch_{tag}_{zi}_UNVERIFIED', [M_cream, M_shadow], col)
        mb.box(cc + N * 0.04, N, U, recess - 0.14, 0.08, z - 0.01, z + 0.11, 0)
        mb.box(cc + N * 0.05, N, U, recess - 0.18, 0.03, z - 0.045, z - 0.01, 1)
        mb.done()
        fills.append(f'return_belt_punch_{tag}_{zi}')

# Quoin punch — stay clear of lettering band z≈137.95
let_z0 = 137.55
for t0, t1, tag in ((1.15, 1.60, 'Wtip_outer'), (4.80, 5.25, 'Wtip_near_ent')):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    mb = MB(f'VF_Freeman_N_quoin_punch_{tag}_UNVERIFIED', [M_cream, M_shadow], col)
    mb.box(mid + N * (OUT + 0.115), U, N, w, 0.065, GR - 0.02, let_z0 - 0.18, 0)
    mb.box(mid + N * (OUT + 0.115), U, N, w, 0.065, let_z0 + 0.60, TOPZ - 0.15, 0)
    mb.box(mid + U * (w / 2) + N * (OUT + 0.12), U, N, 0.04, 0.03, GR + 0.15, let_z0 - 0.22, 1)
    mb.done()
    fills.append(f'quoin_punch_{tag}')

# Soft vertical corner fillet at pier outer faces for layered read
for t0, t1, tag in ((6.70, 6.93, 'pierW_face'), (11.72, 11.93, 'pierE_face')):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    mb = MB(f'VF_Freeman_N_pier_face_punch_{tag}_UNVERIFIED', [M_cream], col)
    mb.box(mid + N * (OUT + 0.118), U, N, w, 0.04, GR - 0.02, TOPZ - 0.15, 0)
    mb.done()
    fills.append(f'pier_face_{tag}')

log['n_cream_fills'] = fills
log['fixes'].append('N_cream_punch_' + '+'.join(fills[:5]) + f'_plus{max(0,len(fills)-5)}')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vf_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vf_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

t_mid = centers[len(centers)//3] if centers else L1 * 0.4
c_mid = A1 + U1 * t_mid
add_cam('VF_CAM_closeup_Freeman_W_glass_sky',
        (c_mid.x + N1.x * 9.0 - U1.x * 1.0, c_mid.y + N1.y * 9.0 - U1.y * 1.0, GR + 5.5),
        (c_mid.x + N1.x * (OUT + 0.15), c_mid.y + N1.y * (OUT + 0.15), GR + 7.5), 42)

scr = A + U * 6.85
add_cam('VF_CAM_closeup_Freeman_N_cream_punch',
        (scr.x + N.x * 10.0 - U.x * 1.8, scr.y + N.y * 10.0 - U.y * 1.8, GR + 4.2),
        (scr.x, scr.y, GR + 7.2), 38)

log['cams'] = [o.name for o in cc.objects if o.get('vf_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vf_obj'] = sum(1 for o in bpy.data.objects if o.get('vf_obj'))
log['n_vf_mat'] = sum(1 for m in bpy.data.materials if m.get('vf_mat'))
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }
log['kept_vd_grid'] = bpy.data.objects.get('VD_Freeman_W_pane_grid_UNVERIFIED') is not None
log['kept_vc_W_bp'] = bpy.data.objects.get('VC_Freeman_W_glass_backplanes_UNVERIFIED') is not None
log['kept_ve_soft'] = bpy.data.materials.get('VE_Freeman_W_cream_soft_UNVERIFIED') is not None
json.dump(log, open(DATA + '/vf_main.json', 'w'), indent=2)
print('VF MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
