"""Session vb (Nov 6 2026 ~12:26–~1:12 PM ET, MAIN, day-10 Freeman polish).

Targets (ALL UNVERIFIED; photo language 1096/1114):
  A) Cooler/clearer W(+S/+N-bay) glass — Transmission glass mat; keep terracotta frames distinct
  B) Stronger cream brick mortar/scale on W/S skins + N lettering wing
  C) N wing blank grey fills — thin cream overlays in remaining N gaps (above screen; micro end strips)
     without covering lettering / terracotta bay / doors / glass / screen face
  D) Optional light screen lattice contrast punch (material only)

Collection: VB_Freeman_polish_UNVERIFIED
Tags: vb_obj / vb_mat / vb_slot_restore JSON on objects
REVERT=1 restores slots + removes vb objs/mats/colls (does NOT touch va lettering transform or ub/uc walls)
SAVE=1 saves mainfile.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vb'
os.makedirs(DATA, exist_ok=True)
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL = 'VB_Freeman_polish_UNVERIFIED'
COL_CAM = 'VB_Freeman_cams'

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
        raw = o.get('vb_slot_restore')
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
        del o['vb_slot_restore']
    # drop temporary fake users we added so mat count matches pre
    for m in list(bpy.data.materials):
        if m.get('vb_kept_fake'):
            m.use_fake_user = False
            del m['vb_kept_fake']

def revert():
    restore_slots()
    for o in [o for o in list(bpy.data.objects) if o.get('vb_obj')]:
        remove_obj(o)
    for m in [m for m in list(bpy.data.materials) if m.get('vb_mat')]:
        bpy.data.materials.remove(m)
    for cname in (COL, COL_CAM):
        c = bpy.data.collections.get(cname)
        if c: bpy.data.collections.remove(c)
    print('VB REVERTED')

if REV:
    revert()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# idempotent re-apply
revert()

log = {'session': 'vb', 'fixes': [], 'GR': GR, 'UNVERIFIED': True}

def mat_glass_cool(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vb_mat'] = 1
    m.blend_method = 'HASHED'
    try: m.shadow_method = 'HASHED'
    except Exception: pass
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    # cooler clear glass — sky-ish, not terracotta
    b.inputs['Base Color'].default_value = (0.78, 0.86, 0.92, 1.0)
    b.inputs['Roughness'].default_value = 0.04
    try: b.inputs['Specular IOR Level'].default_value = 0.55
    except Exception: pass
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = 0.92
    elif 'Transmission' in b.inputs:
        b.inputs['Transmission'].default_value = 0.92
    if 'IOR' in b.inputs:
        b.inputs['IOR'].default_value = 1.45
    b.inputs['Alpha'].default_value = 0.55
    if 'Metallic' in b.inputs:
        b.inputs['Metallic'].default_value = 0.0
    return m

def mat_cream_brick_strong(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vb_mat'] = 1
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = 0.92
    t = nt.nodes.new('ShaderNodeTexBrick')
    # cream / buff brick with stronger mortar contrast (slide 1096 language)
    t.inputs['Color1'].default_value = (0.78, 0.72, 0.58, 1)
    t.inputs['Color2'].default_value = (0.66, 0.60, 0.48, 1)
    t.inputs['Mortar'].default_value = (0.38, 0.34, 0.28, 1)  # darker mortar
    t.inputs['Brick Width'].default_value = 0.20
    t.inputs['Row Height'].default_value = 0.062
    t.inputs['Mortar Size'].default_value = 0.016  # was ~0.009
    t.inputs['Scale'].default_value = 1.35  # stronger brick scale at eye
    t.inputs['Bias'].default_value = 0.05
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['Object'], t.inputs['Vector'])
    # bump from brick for subtle relief
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.004
    # Fac of brick → bump height
    nt.links.new(t.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    return m

def mat_screen_punch(name, base_rgb=(0.55, 0.55, 0.52)):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['vb_mat'] = 1
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base_rgb, 1)
    b.inputs['Roughness'].default_value = 0.78
    # light noise for block cast
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = 18.0
    n.inputs['Detail'].default_value = 4
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = 0.35
    r.color_ramp.elements[0].color = (base_rgb[0]*0.72, base_rgb[1]*0.72, base_rgb[2]*0.70, 1)
    r.color_ramp.elements[1].color = (*base_rgb, 1)
    mix = nt.nodes.new('ShaderNodeMixRGB') if hasattr(bpy.types, 'ShaderNodeMixRGB') else nt.nodes.new('ShaderNodeMix')
    try:
        # Blender 4 Mix Color
        if mix.type == 'MIX':
            mix.data_type = 'RGBA'
            mix.inputs['Fac'].default_value = 0.55
            nt.links.new(n.outputs['Fac'], mix.inputs['Fac'])
            # A = base, B = ramp
            mix.inputs['A'].default_value = (*base_rgb, 1)
            nt.links.new(r.outputs['Color'], mix.inputs['B'])
            nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
        else:
            mix.inputs['Fac'].default_value = 0.55
            nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
            nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    except Exception:
        nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
        nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    else:
        # also drive ramp
        nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
    return m

M_glass = mat_glass_cool('VB_Freeman_glass_cool_clear_UNVERIFIED')
M_brick = mat_cream_brick_strong('VB_Freeman_cream_brick_strong_UNVERIFIED')
log['fixes'].append('mats_glass_cool_cream_strong')

def stash_and_replace_slot(obj, slot_idx, new_mat):
    if obj is None: return False
    if not obj.get('vb_slot_restore'):
        names = [s.material.name if s.material else None for s in obj.material_slots]
        obj['vb_slot_restore'] = json.dumps(names)
        # keep originals alive across save (Blender purges 0-user mats)
        for n in names:
            m = bpy.data.materials.get(n) if n else None
            if m is not None:
                m.use_fake_user = True
                m['vb_kept_fake'] = 1
    if slot_idx >= len(obj.material_slots):
        return False
    obj.material_slots[slot_idx].material = new_mat
    return True

# ---- A) Glass cooler on W / S / N bay / E / entrance curtain glass slot ----
glass_targets = [
    ('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED', 1),
    ('UY_Freeman_S_recessed_vertical_windows_UNVERIFIED', 1),
    ('UY_Freeman_N_terracotta_3panel_window_bay_UNVERIFIED', 1),
    ('UV_Freeman_E_recessed_vertical_windows_UNVERIFIED', 1),
    ('UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED', 1),
]
n_glass = 0
for name, si in glass_targets:
    o = bpy.data.objects.get(name)
    if o and stash_and_replace_slot(o, si, M_glass):
        n_glass += 1
log['fixes'].append(f'glass_cool_slots_x{n_glass}')
log['glass_targets'] = n_glass

# ---- B) Cream brick strong on skins + lettering wing ----
brick_targets = [
    ('UY_Freeman_W_cream_brick_skin_UNVERIFIED', 0),
    ('UY_Freeman_S_cream_brick_skin_UNVERIFIED', 0),
    ('UV_Freeman_N_lettering_brick_wing_UNVERIFIED', 0),
    # also cream slots used as surround on bay / W windows
    ('UY_Freeman_N_terracotta_3panel_window_bay_UNVERIFIED', 3),
    ('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED', 3),
    ('UV_Freeman_E_recessed_vertical_windows_UNVERIFIED', 2),
]
n_brick = 0
for name, si in brick_targets:
    o = bpy.data.objects.get(name)
    if o and stash_and_replace_slot(o, si, M_brick):
        n_brick += 1
log['fixes'].append(f'cream_brick_strong_slots_x{n_brick}')
log['brick_targets'] = n_brick

# ---- D) Optional screen lattice material punch ----
scr = bpy.data.objects.get('UV_Freeman_N_screen_block_breezeway_UNVERIFIED')
n_scr = 0
if scr and scr.material_slots:
    # keep geometry; punch first slot if screen_block
    M_scr = mat_screen_punch('VB_Freeman_screen_block_punch_UNVERIFIED', (0.52, 0.52, 0.49))
    if stash_and_replace_slot(scr, 0, M_scr):
        n_scr = 1
        log['fixes'].append('screen_lattice_mat_punch')
log['screen_punch'] = n_scr

# ---- C) N wing cream fill overlays (proud thin) ----
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
        o['vb_obj'] = 1
        o['UNVERIFIED'] = 'vb Freeman polish; sizes UNVERIFIED; photo 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

col = ensure_coll(COL)
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A = Vector((e6['a'][0], e6['a'][1], 0))
L6 = e6['len']

# Spans from probe (avoid covering lettering/bay/doors/glass/screen face):
# lettering wing t~0.09-3.41; bay 3.29-6.64; entrance 5.58-12.85; screen 11.98-15.03 z to 143.4
# Fill: (1) above screen to parapet; (2) thin west tip if any blank beside lettering start;
# (3) thin cream apron strip under lettering wing at grade if grey shows (skip — lettering wing already full height)
fills = []
# above screen: t 12.05 .. 14.95, z 143.25 .. TOPZ-0.12
t0, t1 = 12.05, 14.95
wc = A + U * ((t0 + t1) / 2)
mb = MB('VB_Freeman_N_cream_fill_above_screen_UNVERIFIED', [M_brick], col)
mb.box(wc + N * (OUT + 0.05), U, N, (t1 - t0), 0.06, 143.25, TOPZ - 0.12, 0)
mb.done(); fills.append('above_screen')

# micro east tip past screen outer if wall continues (screen ends ~15.03, face len 15.07)
if L6 - 14.95 > 0.08:
    t0e, t1e = 14.95, min(L6 - 0.05, 15.05)
    wce = A + U * ((t0e + t1e) / 2)
    mb2 = MB('VB_Freeman_N_cream_fill_east_tip_UNVERIFIED', [M_brick], col)
    mb2.box(wce + N * (OUT + 0.05), U, N, max(0.08, t1e - t0e), 0.06, GR - 0.02, TOPZ - 0.12, 0)
    mb2.done(); fills.append('east_tip')

# west tip before lettering wing (t 0 .. 0.12) if any
if 0.09 > 0.04:
    t0w, t1w = 0.02, 0.10
    wcw = A + U * ((t0w + t1w) / 2)
    mb3 = MB('VB_Freeman_N_cream_fill_west_tip_UNVERIFIED', [M_brick], col)
    mb3.box(wcw + N * (OUT + 0.05), U, N, max(0.06, t1w - t0w), 0.06, GR - 0.02, TOPZ - 0.12, 0)
    mb3.done(); fills.append('west_tip')

# Gap band between terracotta bay end and entrance curtain start at UPPER levels only?
# bay ends ~6.64, entrance starts ~5.58 (overlap). Lower grade under bay already terracotta.
# Instead: cream filler BETWEEN lettering wing end and bay start if tiny gap (3.41 vs 3.29 overlap).
# No horizontal gap. Add vertical cream returns on entrance recess side walls if blank —
# approximate as thin strips just west of entrance at t~5.9-6.2 OUTSIDE bay? Skip inventing recess returns without clear measure.
# Add cream fill on N face UNDER the canopy zone OUTSIDE door curtain width? Too risky.
# One more: blank grey often is ub wall visible ABOVE lettering brick wing where wing may not reach parapet —
# lettering wing z goes to 146.9 — full height. OK.

log['n_fills'] = fills
log['fixes'].append('N_cream_fills_' + '+'.join(fills))

# ---- Cams ----
cc = ensure_coll(COL_CAM)
def add_cam(name, loc, target, lens=32):
    existing = bpy.data.objects.get(name)
    if existing and existing.get('vb_obj'):
        remove_obj(existing)
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['vb_obj'] = 1
    o.location = loc
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# reuse UY NW oblique + UV N eye + UY W eye; add VB close-up on W glass/cream
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
mid_w = A1 + U1 * (L1 * 0.40)
add_cam('VB_CAM_closeup_Freeman_W_glass_cream',
        (mid_w.x + N1.x * 9.0, mid_w.y + N1.y * 9.0, GR + 3.2),
        (mid_w.x, mid_w.y, GR + 8.5), 45)
# N wing fill close-up near screen top
scr_c = A + U * 13.5
add_cam('VB_CAM_closeup_Freeman_N_wing_fill',
        (scr_c.x + N.x * 8.0 - U.x * 1.5, scr_c.y + N.y * 8.0 - U.y * 1.5, GR + 12.0),
        (scr_c.x, scr_c.y, GR + 15.5), 40)

log['cams'] = [o.name for o in cc.objects if o.get('vb_obj')]
log['n_objects'] = len(bpy.data.objects)
log['n_vb_obj'] = sum(1 for o in bpy.data.objects if o.get('vb_obj'))
log['n_vb_mat'] = sum(1 for m in bpy.data.materials if m.get('vb_mat'))
log['n_uy_obj'] = sum(1 for o in bpy.data.objects if o.get('uy_obj'))
log['n_uv_obj'] = sum(1 for o in bpy.data.objects if o.get('uv_obj'))
json.dump(log, open(DATA + '/vb_main.json', 'w'), indent=2)
print('VB MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
