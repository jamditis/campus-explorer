"""Session vd (Nov 6 2026 ~2:22–~3:12 PM ET, MAIN, day-10 Freeman polish).

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) W facade pane grid — hide UY W recessed windows; rebuild with clearer mullion/spandrel
     rhythm (split panes, darker reveals, glass proud of spandrel, frame depth).
  B) N mid-wall cream depth — stronger mortar bump/weather on VB cream; thin VD proud edge
     fillets on VC cream pier/return fills (no cover of lettering/bay/doors/glass/screen).
  C) Approach walks — Footpaths_OSM already drapes OSM centrelines near Freeman; do NOT
     invent N apron. Logged only (no new apron geometry).

Collection: VD_Freeman_polish_UNVERIFIED
Tags: vd_obj / vd_mat / vd_slot_restore / vd_hidden
REVERT=1 restores slots + unhides + removes vd objs/mats/colls
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vd'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VD_Freeman_polish_UNVERIFIED'
COL_CAM = 'VD_Freeman_cams'
CREAM_STASH = DATA + '/vd_cream_stash.json'
SPANDREL_STASH = DATA + '/vd_spandrel_stash.json'

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
        raw = o.get('vd_slot_restore')
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
        del o['vd_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('vd_kept_fake'):
            m.use_fake_user = False
            del m['vd_kept_fake']

def stash_cream():
    m = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
    if not m or not m.use_nodes: return
    if os.path.exists(CREAM_STASH): return
    nt = m.node_tree
    d = {'nodes': {}}
    b = nt.nodes.get('Principled BSDF')
    if b:
        d['rough'] = b.inputs['Roughness'].default_value
    # Brick + bump + mapping if present
    for n in nt.nodes:
        if n.type == 'TEX_BRICK':
            d['brick'] = {
                'Color1': list(n.inputs['Color1'].default_value),
                'Color2': list(n.inputs['Color2'].default_value),
                'Mortar': list(n.inputs['Mortar'].default_value),
                'Brick Width': n.inputs['Brick Width'].default_value,
                'Row Height': n.inputs['Row Height'].default_value,
                'Mortar Size': n.inputs['Mortar Size'].default_value,
                'Scale': n.inputs['Scale'].default_value,
            }
        if n.type == 'BUMP':
            d['bump'] = {
                'Strength': n.inputs['Strength'].default_value,
                'Distance': n.inputs['Distance'].default_value,
            }
        if n.type == 'MAPPING':
            d['map_scale'] = list(n.inputs['Scale'].default_value)
    json.dump(d, open(CREAM_STASH, 'w'), indent=2)

def restore_cream():
    m = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
    if not m or not m.use_nodes or not os.path.exists(CREAM_STASH): return
    d = json.load(open(CREAM_STASH))
    nt = m.node_tree
    b = nt.nodes.get('Principled BSDF')
    if b and 'rough' in d:
        b.inputs['Roughness'].default_value = d['rough']
    for n in nt.nodes:
        if n.type == 'TEX_BRICK' and 'brick' in d:
            br = d['brick']
            for k, v in br.items():
                if k in n.inputs:
                    n.inputs[k].default_value = v
        if n.type == 'BUMP' and 'bump' in d:
            n.inputs['Strength'].default_value = d['bump']['Strength']
            n.inputs['Distance'].default_value = d['bump']['Distance']
        if n.type == 'MAPPING' and 'map_scale' in d:
            n.inputs['Scale'].default_value = d['map_scale']
    print('VD restored VB cream from stash')

def stash_spandrel():
    m = bpy.data.materials.get('UY_Freeman_spandrel_reddish_UNVERIFIED')
    if not m or not m.use_nodes: return
    if os.path.exists(SPANDREL_STASH): return
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    json.dump({
        'Base Color': list(b.inputs['Base Color'].default_value),
        'Roughness': b.inputs['Roughness'].default_value,
    }, open(SPANDREL_STASH, 'w'), indent=2)


def restore_uy_frame():
    m = bpy.data.materials.get('UV_Freeman_window_frame_darkred_UNVERIFIED')
    stash = DATA + '/vd_uy_frame_stash.json'
    if not m or not m.use_nodes or not os.path.exists(stash): return
    d = json.load(open(stash))
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    b.inputs['Base Color'].default_value = d['Base Color']
    b.inputs['Roughness'].default_value = d['Roughness']
    print('VD restored UV frame from stash')

def restore_spandrel():
    m = bpy.data.materials.get('UY_Freeman_spandrel_reddish_UNVERIFIED')
    if not m or not m.use_nodes or not os.path.exists(SPANDREL_STASH): return
    d = json.load(open(SPANDREL_STASH))
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    b.inputs['Base Color'].default_value = d['Base Color']
    b.inputs['Roughness'].default_value = d['Roughness']
    print('VD restored UY spandrel from stash')

def unhide_vd_hidden():
    for o in bpy.data.objects:
        if o.get('vd_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['vd_hidden']

def revert():
    restore_cream()
    restore_spandrel()
    restore_uy_frame()
    restore_slots()
    unhide_vd_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('vd_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vd_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VD REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vd', 'fixes': [], 'GR': GR, 'UNVERIFIED': True}

# ---- materials ----
def mat_frame_dark(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vd_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.045, 0.035, 0.032, 1.0)
    b.inputs['Roughness'].default_value = 0.55
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.25
    return m

def mat_reveal(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vd_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.02, 0.018, 0.016, 1.0)
    b.inputs['Roughness'].default_value = 0.75
    return m

def mat_glass_vd(name):
    """Slightly cooler/clearer glass for W pane grid only (does not overwrite VB glass)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vd_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.68, 0.82, 0.94, 1.0)
    b.inputs['Roughness'].default_value = 0.015
    b.inputs['Alpha'].default_value = 0.32
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = 1.0
    elif 'Transmission' in b.inputs:
        b.inputs['Transmission'].default_value = 1.0
    if 'IOR' in b.inputs:
        b.inputs['IOR'].default_value = 1.45
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 0.35
        b.inputs['Coat Roughness'].default_value = 0.03
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.75
    m.blend_method = 'HASHED'
    try: m.shadow_method = 'HASHED'
    except Exception: pass
    return m

def mat_spandrel_vd(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vd_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    # slightly darker / less chalky than UY reddish so glass reads brighter by contrast
    b.inputs['Base Color'].default_value = (0.42, 0.16, 0.10, 1.0)
    b.inputs['Roughness'].default_value = 0.78
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.15
    return m

M_frame = mat_frame_dark('VD_Freeman_W_frame_dark_UNVERIFIED')
M_reveal = mat_reveal('VD_Freeman_W_reveal_dark_UNVERIFIED')
M_glass = mat_glass_vd('VD_Freeman_W_glass_pane_UNVERIFIED')
M_span = mat_spandrel_vd('VD_Freeman_W_spandrel_deep_UNVERIFIED')
# Prefer existing dark frame if present for continuity
M_frame_uy = bpy.data.materials.get('UV_Freeman_window_frame_darkred_UNVERIFIED') or M_frame
log['fixes'].append('mats_W_pane_grid')

stash_cream()
stash_spandrel()

# Strengthen VB cream brick mortar/bump for N mid-wall depth (reused by VC fills)
cream = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
if cream and cream.use_nodes:
    nt = cream.node_tree
    for n in nt.nodes:
        if n.type == 'TEX_BRICK':
            n.inputs['Mortar'].default_value = (0.26, 0.22, 0.17, 1)
            n.inputs['Mortar Size'].default_value = max(n.inputs['Mortar Size'].default_value, 0.022)
            n.inputs['Color1'].default_value = (0.82, 0.76, 0.62, 1)
            n.inputs['Color2'].default_value = (0.68, 0.62, 0.50, 1)
            n.inputs['Scale'].default_value = max(n.inputs['Scale'].default_value, 4.5)
        if n.type == 'BUMP':
            n.inputs['Strength'].default_value = max(n.inputs['Strength'].default_value, 0.42)
            n.inputs['Distance'].default_value = 0.0065
        if n.type == 'MAPPING':
            n.inputs['Scale'].default_value = (2.6, 2.6, 2.6)
    log['fixes'].append('VB_cream_mortar_bump_stronger')

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
        o['vd_obj'] = 1
        o['UNVERIFIED'] = 'vd Freeman polish; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- A) W pane grid ----------
# Hide (not delete) prior UY W windows
uy_w = bpy.data.objects.get('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED')
if uy_w:
    uy_w.hide_render = True
    uy_w.hide_viewport = True
    uy_w['vd_hidden'] = 1
    log['fixes'].append('hide_UY_W_recessed_windows')

e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
pitch = 3.6
centers = []
n_bays = max(1, int((L1 - 4.0) / pitch))
for i in range(n_bays):
    t = 2.0 + pitch * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)

# mats: 0 frame, 1 glass, 2 spandrel, 3 reveal
mb = MB('VD_Freeman_W_pane_grid_UNVERIFIED',
        [M_frame_uy, M_glass, M_span, M_reveal], col)

# glass / spandrel bands (same storeys as uy/vc)
# each glass band split into 2 panes with center mullion
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
PANE_GAP = 0.06  # mullion thickness
PANE_INSET = 0.06  # from frame inner

n_panes = 0
for t in centers:
    c = A1 + U1 * t
    # outer dark frame box (proud)
    mb.box(c + N1 * (OUT + 0.12), U1, N1, BAY_W, FRAME_DEP, GR + 0.75, TOPZ - 0.35, 0)
    # side reveals inside frame (darker vertical)
    for sgn in (-1, 1):
        rc = c + U1 * (sgn * (BAY_W / 2 - 0.05))
        mb.box(rc + N1 * (OUT + 0.20), U1, N1, 0.05, REVEAL_DEP, GR + 0.95, TOPZ - 0.50, 3)
    # glass panes + mullions + spandrels
    inner_w = BAY_W - 0.18
    pane_w = (inner_w - PANE_GAP) / 2
    for z0, z1 in glass_bands:
        if z1 <= z0 + 0.08: continue
        # horizontal reveal under/over glass into spandrel
        mb.box(c + N1 * (OUT + 0.16), U1, N1, inner_w + 0.02, REVEAL_DEP, z0 - 0.015, z0 + 0.02, 3)
        mb.box(c + N1 * (OUT + 0.16), U1, N1, inner_w + 0.02, REVEAL_DEP, z1 - 0.02, z1 + 0.015, 3)
        # two panes
        for sgn in (-1, 1):
            pc = c + U1 * (sgn * (pane_w / 2 + PANE_GAP / 2))
            mb.box(pc + N1 * (OUT + 0.22), U1, N1, pane_w - PANE_INSET, GLASS_DEP, z0 + 0.025, z1 - 0.025, 1)
            n_panes += 1
        # center mullion (vertical)
        mb.box(c + N1 * (OUT + 0.20), U1, N1, PANE_GAP + 0.02, 0.08, z0 + 0.01, z1 - 0.01, 0)
        # optional mid horizontal muntin on tall bands (>2.0 m)
        if (z1 - z0) > 2.0:
            midz = (z0 + z1) / 2
            mb.box(c + N1 * (OUT + 0.205), U1, N1, inner_w - 0.04, 0.06, midz - 0.025, midz + 0.025, 0)
    for z0, z1 in span_bands:
        if z1 <= z0 + 0.02: continue
        # spandrel recessed relative to glass
        mb.box(c + N1 * (OUT + 0.14), U1, N1, inner_w - 0.04, SPAN_DEP, z0 + 0.01, z1 - 0.01, 2)
        # dark reveal lip above/below spandrel already partially covered; side lips
        for sgn in (-1, 1):
            sc = c + U1 * (sgn * (inner_w / 2 - 0.02))
            mb.box(sc + N1 * (OUT + 0.15), U1, N1, 0.04, REVEAL_DEP, z0, z1, 3)

mb.done()
log['fixes'].append(f'W_pane_grid_bays{len(centers)}_panes{n_panes}')
log['W_bays'] = len(centers)
log['W_panes'] = n_panes

# ---------- B) N cream depth — thin proud edge fillets on VC fills ----------
M_cream = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
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
# Edge fillets: thin vertical strips at outer corners of pier fills (proud of VC piers)
for t0, t1, tag in ((6.68, 6.95, 'pierW'), (11.70, 11.95, 'pierE')):
    # outer edge of pier (away from curtain)
    if tag == 'pierW':
        t_edge = t0 + 0.02
        # also inner edge toward curtain
        edges_t = [t0 + 0.02, t1 - 0.02]
    else:
        edges_t = [t0 + 0.02, t1 - 0.02]
    for te in edges_t:
        mid = A + U * te
        mb2 = MB(f'VD_Freeman_N_cream_edge_{tag}_{te:.2f}_UNVERIFIED', [M_cream], col)
        # thin proud fillet on outer face
        mb2.box(mid + N * (OUT + 0.085), U, N, 0.04, 0.04, GR - 0.02, TOPZ - 0.12, 0)
        mb2.done()
        fills.append(f'edge_{tag}_{te:.2f}')

# Soft base weathering band on pier outer faces (dirt wash strip)
for t0, t1, tag in ((6.68, 6.95, 'pierW'), (11.70, 11.95, 'pierE'),
                    (7.00, 7.45, 'midW'), (11.35, 11.70, 'midE')):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    z0 = GR - 0.02
    z1 = GR + 1.35
    if tag.startswith('mid'):
        z0 = can_z1 + 0.05  # mid strips only above canopy — skip base dirt there
        continue  # mid above-canopy: add thin top drip instead
    mb3 = MB(f'VD_Freeman_N_cream_basewash_{tag}_UNVERIFIED', [M_cream], col)
    # slightly proud dirty lip — reuse cream mat (weather already in shader)
    mb3.box(mid + N * (OUT + 0.09), U, N, w - 0.02, 0.035, z0, z1, 0)
    mb3.done()
    fills.append(f'basewash_{tag}')

# Thin cornice-ish shadow strip under top of above-canopy mid fills (depth cue)
for t0, t1, tag in ((7.00, 7.45, 'midW'), (11.35, 11.70, 'midE')):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    mb4 = MB(f'VD_Freeman_N_cream_topshadow_{tag}_UNVERIFIED', [M_reveal], col)
    mb4.box(mid + N * (OUT + 0.09), U, N, w - 0.02, 0.03, TOPZ - 0.55, TOPZ - 0.42, 0)
    mb4.done()
    fills.append(f'topshadow_{tag}')

# Return depth: thin horizontal shelf lines on entrance returns (3 storeys)
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U * (sgn * ew / 2) + U * (-sgn * 0.04)
    cc = rc + N * (OUT - recess / 2)
    for z in (GR + 3.6, GR + 7.0, GR + 10.4):
        mb5 = MB(f'VD_Freeman_N_cream_return_shelf_{tag}_{int(z)}_UNVERIFIED', [M_cream], col)
        mb5.box(cc + N * 0.02, N, U, recess - 0.20, 0.05, z, z + 0.06, 0)
        mb5.done()
        fills.append(f'return_shelf_{tag}_{int(z)}')

log['n_cream_fills'] = fills
log['fixes'].append('N_cream_depth_' + '+'.join(fills[:6]) + f'_plus{max(0,len(fills)-6)}')

# ---------- C) Approach walks note (no invented apron) ----------
# Footpaths_OSM already covers OSM ways 312845863/877/312847969/312932147/148 near Freeman
# (probed: cov_fp high; draped ~6 cm above DTM). UA has 312845863 south band only.
# No OSM centreline terminates at N entrance doors on edge 6 — parallel walk ~4.6 m north.
# Do NOT invent N apron. Record for LOG.
walk_note = {
    'action': 'none_no_invented_apron',
    'reason': 'Footpaths_OSM already drapes OSM approach centrelines near Freeman; no OSM way ends at N entrance doors (edge 6); parallel 312845863 ~4.6m north',
    'osm_ways_near': ['312845863', '312845877', '312847969', '312932147', '312932148'],
}
json.dump(walk_note, open(DATA + '/approach_walks_note.json', 'w'), indent=2)
log['approach_walks'] = walk_note
log['fixes'].append('approach_walks_note_Footpaths_OSM_covers_no_apron')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vd_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vd_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

t_mid = centers[len(centers)//3] if centers else L1 * 0.4
c_mid = A1 + U1 * t_mid
add_cam('VD_CAM_closeup_Freeman_W_pane_grid',
        (c_mid.x + N1.x * 5.0, c_mid.y + N1.y * 5.0, GR + 5.6),
        (c_mid.x + N1.x * (OUT + 0.22), c_mid.y + N1.y * (OUT + 0.22), GR + 7.2), 55)

# N cream depth close-up (pier W + return)
scr = A + U * 6.85
add_cam('VD_CAM_closeup_Freeman_N_cream_depth',
        (scr.x + N.x * 8.5 - U.x * 1.2, scr.y + N.y * 8.5 - U.y * 1.2, GR + 2.6),
        (scr.x, scr.y, GR + 5.2), 42)

log['cams'] = [o.name for o in cc.objects if o.get('vd_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vd_obj'] = sum(1 for o in bpy.data.objects if o.get('vd_obj'))
log['n_vd_mat'] = sum(1 for m in bpy.data.materials if m.get('vd_mat'))
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }
json.dump(log, open(DATA + '/vd_main.json', 'w'), indent=2)
print('VD MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
