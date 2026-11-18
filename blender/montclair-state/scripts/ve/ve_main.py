"""Session ve (Nov 6 2026 ~3:18–~4:12 PM ET, MAIN, day-10 Freeman polish after vd).

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) W facade cream/glass grazing — soften striped interbay cream (W-only mat slot-swap
     on UY W cream skin; keep VB cream on N); improve VD glass/spandrel at grazing;
     keep vd pane grid + VC backplanes; no ub/uc delete.
  B) N cream eye depth — pier side returns, shadow grooves, storey belts on VC fills;
     do NOT cover va lettering GRACE H. FREEMAN HALL, terracotta bay, doors, glass, screen.
  C) Optional: S cream soft match + S/E glass cooler match; mild RTU tone. No apron.

Collection: VE_Freeman_polish_UNVERIFIED
Tags: ve_obj / ve_mat / ve_slot_restore / ve_hidden
REVERT=1 restores slots + unhides + removes ve objs/mats/colls + restores glass/spandrel/RTU stash
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json, copy
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/ve'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VE_Freeman_polish_UNVERIFIED'
COL_CAM = 'VE_Freeman_cams'
GLASS_STASH = DATA + '/ve_glass_stash.json'
SPAN_STASH = DATA + '/ve_spandrel_stash.json'
RTU_STASH = DATA + '/ve_rtu_stash.json'
SGLASS_STASH = DATA + '/ve_vb_glass_stash.json'

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
        raw = o.get('ve_slot_restore')
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
        del o['ve_slot_restore']
    for m in list(bpy.data.materials):
        if m.get('ve_kept_fake'):
            m.use_fake_user = False
            del m['ve_kept_fake']

def stash_principled(path, mat_name, keys=('Base Color','Roughness','Alpha','Coat Weight','Coat Roughness','Specular IOR Level','Transmission Weight')):
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
    print('VE restored', mat_name, 'from stash')

def unhide_ve_hidden():
    for o in bpy.data.objects:
        if o.get('ve_hidden'):
            o.hide_render = False
            o.hide_viewport = False
            del o['ve_hidden']

def revert():
    restore_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
    restore_principled(SPAN_STASH, 'VD_Freeman_W_spandrel_deep_UNVERIFIED')
    restore_principled(RTU_STASH, 'UY_Freeman_RTU_metal_UNVERIFIED')
    restore_principled(SGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')
    restore_slots()
    unhide_ve_hidden()
    for o in [o for o in list(bpy.data.objects) if o.get('ve_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('ve_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VE REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 've', 'fixes': [], 'GR': GR, 'UNVERIFIED': True}

# ---- materials ----
def make_cream_soft(name):
    """W/S facade cream: soft stucco noise (no brick) so interbay doesn't flute at eye."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m['ve_mat'] = 1
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (400, 200)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.location = (100, 200); b.name = 'Principled BSDF'
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.location = (-500, 200)
    noise.inputs['Scale'].default_value = 12.0
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = 0.55
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.location = (-250, 200)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.72, 0.66, 0.54, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.78, 0.72, 0.58, 1)
    bump = nt.nodes.new('ShaderNodeBump'); bump.location = (-50, 50)
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.002
    texcoord = nt.nodes.new('ShaderNodeTexCoord'); texcoord.location = (-700, 200)
    mapping = nt.nodes.new('ShaderNodeMapping'); mapping.location = (-600, 200)
    nt.links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    b.inputs['Roughness'].default_value = 0.90
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.18
    return m


def make_cream_depth_mat(name):
    """Slightly warmer/shadow cream for N pier depth overlays (stucco noise)."""
    m = make_cream_soft(name)
    nt = m.node_tree
    for n in nt.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (0.58, 0.52, 0.40, 1)
            n.color_ramp.elements[1].color = (0.70, 0.64, 0.50, 1)
        if n.type == 'BUMP':
            n.inputs['Strength'].default_value = 0.14
    return m


def make_shadow_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['ve_mat'] = 1
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.08, 0.07, 0.06, 1.0)
    b.inputs['Roughness'].default_value = 0.9
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.05
    return m

M_cream_soft = make_cream_soft('VE_Freeman_W_cream_soft_UNVERIFIED')
M_cream_depth = make_cream_depth_mat('VE_Freeman_N_cream_depth_UNVERIFIED')
M_shadow = make_shadow_mat('VE_Freeman_shadow_lip_UNVERIFIED')
log['fixes'].append('mats_cream_soft_depth_shadow')

# Stash + polish VD glass / spandrel for grazing
stash_principled(GLASS_STASH, 'VD_Freeman_W_glass_pane_UNVERIFIED')
stash_principled(SPAN_STASH, 'VD_Freeman_W_spandrel_deep_UNVERIFIED')
stash_principled(RTU_STASH, 'UY_Freeman_RTU_metal_UNVERIFIED')
stash_principled(SGLASS_STASH, 'VB_Freeman_glass_cool_clear_UNVERIFIED')

g = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b = g.node_tree.nodes.get('Principled BSDF')
    if b:
        # sky-read at grazing: cooler tint, higher alpha so BP doesn't dominate, coat punch
        b.inputs['Base Color'].default_value = (0.62, 0.78, 0.92, 1.0)
        b.inputs['Alpha'].default_value = 0.48
        b.inputs['Roughness'].default_value = 0.02
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value = 1.0
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.55
            b.inputs['Coat Roughness'].default_value = 0.025
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.95
        if 'IOR' in b.inputs:
            b.inputs['IOR'].default_value = 1.52
        log['fixes'].append('VD_W_glass_grazing_alpha0.48_coat0.55')

s = bpy.data.materials.get('VD_Freeman_W_spandrel_deep_UNVERIFIED')
if s and s.use_nodes:
    b = s.node_tree.nodes.get('Principled BSDF')
    if b:
        # terracotta a touch lighter so glass/spandrel alternate at grazing
        b.inputs['Base Color'].default_value = (0.68, 0.32, 0.16, 1.0)
        b.inputs['Roughness'].default_value = 0.70
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.22
        log['fixes'].append('VD_spandrel_terracotta_grazing')

# Optional C: S/E glass match via VB cool glass tweak (shared — mild)
vg = bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vg and vg.use_nodes:
    b = vg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.65, 0.80, 0.93, 1.0)
        if 'Alpha' in b.inputs:
            b.inputs['Alpha'].default_value = min(0.45, max(0.30, b.inputs['Alpha'].default_value))
            if b.inputs['Alpha'].default_value < 0.40:
                b.inputs['Alpha'].default_value = 0.42
        b.inputs['Roughness'].default_value = 0.02
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.45
            b.inputs['Coat Roughness'].default_value = 0.03
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.85
        log['fixes'].append('VB_glass_cool_SE_match_grazing')

# Mild RTU tone (C)
rtu = bpy.data.materials.get('UY_Freeman_RTU_metal_UNVERIFIED')
if rtu and rtu.use_nodes:
    b = rtu.node_tree.nodes.get('Principled BSDF')
    if b:
        # slightly warmer/darker grey metal so RTUs don't chalk against cream
        b.inputs['Base Color'].default_value = (0.28, 0.27, 0.26, 1.0)
        b.inputs['Roughness'].default_value = 0.55
        if 'Metallic' in b.inputs:
            b.inputs['Metallic'].default_value = 0.35
        log['fixes'].append('RTU_tone_warmer_darker')

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
        o['ve_obj'] = 1
        o['UNVERIFIED'] = 've Freeman polish; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)

# ---------- A) W cream soft slot-swap + interbay shadow lips ----------
def slot_swap(obj_name, new_mat):
    o = bpy.data.objects.get(obj_name)
    if not o: return False
    names = [s.material.name if s.material else None for s in o.material_slots]
    if not o.get('ve_slot_restore'):
        o['ve_slot_restore'] = json.dumps(names)
        for n in names:
            m = bpy.data.materials.get(n) if n else None
            if m:
                m.use_fake_user = True
                m['ve_kept_fake'] = 1
    # ensure at least one slot
    if len(o.material_slots) == 0:
        o.data.materials.append(new_mat)
    else:
        o.material_slots[0].material = new_mat
    return True

if slot_swap('UY_Freeman_W_cream_brick_skin_UNVERIFIED', M_cream_soft):
    log['fixes'].append('W_cream_slot_soft')
if slot_swap('UY_Freeman_S_cream_brick_skin_UNVERIFIED', M_cream_soft):
    log['fixes'].append('S_cream_slot_soft_match')

# Interbay soft shadow lips between W bays (break continuous stripe without deleting grid)
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
pitch = 3.6
centers = []
for i in range(max(1, int((L1 - 4.0) / pitch))):
    t = 2.0 + pitch * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)

BAY_W = 1.22
interbay = []
# lips centered in gaps between adjacent bay outer edges
for i in range(len(centers) - 1):
    t_mid = (centers[i] + centers[i + 1]) / 2
    # gap width ≈ pitch - BAY_W
    gap_w = max(0.35, pitch - BAY_W - 0.15)
    c = A1 + U1 * t_mid
    mb = MB(f'VE_Freeman_W_interbay_soft_{i:02d}_UNVERIFIED', [M_cream_soft, M_shadow], col)
    # soft cream cover over stripey skin (slightly proud)
    mb.box(c + N1 * (OUT + 0.055), U1, N1, gap_w, 0.04, GR + 0.70, TOPZ - 0.30, 0)
    # thin dark vertical reveal at bay-adjacent edges
    for sgn in (-1, 1):
        rc = c + U1 * (sgn * (gap_w / 2 - 0.03))
        mb.box(rc + N1 * (OUT + 0.07), U1, N1, 0.04, 0.025, GR + 0.85, TOPZ - 0.40, 1)
    mb.done()
    interbay.append(i)
log['W_interbay'] = len(interbay)
log['fixes'].append(f'W_interbay_soft_lips_{len(interbay)}')

# ---------- B) N cream eye depth ----------
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

# Pier side returns (depth faces into recess) — do not invade curtain/glass
for t0, t1, tag, toward_curtain in (
    (6.68, 6.95, 'pierW', +1),   # east face of W pier toward curtain
    (11.70, 11.95, 'pierE', -1), # west face of E pier toward curtain
):
    # outer face already has VD edge; add SIDE return as thin slab along N into recess
    t_face = t1 if toward_curtain > 0 else t0
    mid = A + U * t_face
    # side return sits on pier flank facing curtain, extending into recess
    mb = MB(f'VE_Freeman_N_pier_sidereturn_{tag}_UNVERIFIED', [M_cream_depth], col)
    # center in recess along N; width along N = recess depth; thickness along U small
    cc = mid + N * (OUT - recess / 2)
    mb.box(cc, N, U, recess - 0.15, 0.06, GR - 0.02, TOPZ - 0.15, 0)
    mb.done()
    fills.append(f'sidereturn_{tag}')

# Shadow grooves between cream pier and terracotta bay / curtain
# pierW east edge ~6.95, terracotta bay starts ~7.45? midW is 7.00-7.45 above canopy
# Put thin dark lip just east of pierW and west of pierE (outside curtain glass zone)
for te, tag in ((6.96, 'pierW_E'), (11.69, 'pierE_W')):
    mid = A + U * te
    mb = MB(f'VE_Freeman_N_shadow_groove_{tag}_UNVERIFIED', [M_shadow], col)
    mb.box(mid + N * (OUT + 0.095), U, N, 0.035, 0.03, GR - 0.02, TOPZ - 0.20, 0)
    mb.done()
    fills.append(f'shadow_{tag}')

# Storey belt courses on pier outer faces + mid above-canopy fills (horizontal depth cues)
belt_zs = [GR + 3.55, GR + 6.95, GR + 10.35, TOPZ - 0.75]
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
            continue  # mid fills only above canopy
        mb = MB(f'VE_Freeman_N_belt_{tag}_{zi}_UNVERIFIED', [M_cream_depth, M_shadow], col)
        mb.box(mid + N * (OUT + 0.10), U, N, w - 0.01, 0.045, z, z + 0.07, 0)
        # thin shadow under belt
        mb.box(mid + N * (OUT + 0.105), U, N, w - 0.02, 0.02, z - 0.025, z, 1)
        mb.done()
        fills.append(f'belt_{tag}_{zi}')

# Return wall shelves thicker / more proud than vd (additional depth on entrance returns)
for sgn, tag in ((-1, 'W'), (1, 'E')):
    rc = ec + U * (sgn * ew / 2) + U * (-sgn * 0.05)
    cc = rc + N * (OUT - recess / 2)
    for zi, z in enumerate((GR + 3.5, GR + 6.9, GR + 10.3)):
        mb = MB(f'VE_Freeman_N_return_belt_{tag}_{zi}_UNVERIFIED', [M_cream_depth, M_shadow], col)
        mb.box(cc + N * 0.03, N, U, recess - 0.18, 0.06, z, z + 0.08, 0)
        mb.box(cc + N * 0.035, N, U, recess - 0.22, 0.025, z - 0.03, z, 1)
        mb.done()
        fills.append(f'return_belt_{tag}_{zi}')

# Soft quoin / corner depth on west tip cream (BELOW lettering z≈137.95 — stay under 137.5)
# west tip fill exists as VB_Freeman_N_cream_fill_west_tip — add vertical corner lip near NW
# Lettering roughly spans ~2.93 m along facade near west tip; keep z < 137.5 and don't cover sign band
let_z0 = 137.55  # leave clear band for lettering
# west tip along edge 6: roughly t near 0..5.5 before entrance
for t0, t1, tag in ((1.2, 1.55, 'Wtip_outer'), (4.85, 5.20, 'Wtip_near_ent')):
    w = t1 - t0
    mid = A + U * ((t0 + t1) / 2)
    mb = MB(f'VE_Freeman_N_quoin_{tag}_UNVERIFIED', [M_cream_depth, M_shadow], col)
    # full-height corner lip but STOP below lettering band and resume above
    mb.box(mid + N * (OUT + 0.09), U, N, w, 0.05, GR - 0.02, let_z0 - 0.15, 0)
    mb.box(mid + N * (OUT + 0.09), U, N, w, 0.05, let_z0 + 0.55, TOPZ - 0.18, 0)
    # shadow edge
    mb.box(mid + U * (w / 2) + N * (OUT + 0.095), U, N, 0.03, 0.025, GR + 0.2, let_z0 - 0.2, 1)
    mb.done()
    fills.append(f'quoin_{tag}')

log['n_cream_fills'] = fills
log['fixes'].append('N_cream_depth_' + '+'.join(fills[:5]) + f'_plus{max(0,len(fills)-5)}')

# ---------- Cams ----------
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('ve_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['ve_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# W close-up: mid bay, catch glass+spandrel+soft interbay
t_mid = centers[len(centers)//3] if centers else L1 * 0.4
c_mid = A1 + U1 * t_mid
add_cam('VE_CAM_closeup_Freeman_W_cream_glass',
        (c_mid.x + N1.x * 7.0 - U1.x * 0.4, c_mid.y + N1.y * 7.0 - U1.y * 0.4, GR + 5.9),
        (c_mid.x + N1.x * (OUT + 0.22), c_mid.y + N1.y * (OUT + 0.22), GR + 7.6), 48)

# N cream depth close-up on pier W + return
scr = A + U * 6.85
add_cam('VE_CAM_closeup_Freeman_N_cream_depth',
        (scr.x + N.x * 9.0 - U.x * 1.5, scr.y + N.y * 9.0 - U.y * 1.5, GR + 3.0),
        (scr.x, scr.y, GR + 6.0), 40)

log['cams'] = [o.name for o in cc.objects if o.get('ve_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_ve_obj'] = sum(1 for o in bpy.data.objects if o.get('ve_obj'))
log['n_ve_mat'] = sum(1 for m in bpy.data.materials if m.get('ve_mat'))
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }
# confirm vd pane grid + vc backplanes still present
log['kept_vd_grid'] = bpy.data.objects.get('VD_Freeman_W_pane_grid_UNVERIFIED') is not None
log['kept_vc_W_bp'] = bpy.data.objects.get('VC_Freeman_W_glass_backplanes_UNVERIFIED') is not None
json.dump(log, open(DATA + '/ve_main.json', 'w'), indent=2)
print('VE MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
