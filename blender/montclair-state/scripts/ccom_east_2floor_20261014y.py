"""2026-10-14 ~5:30 PM ET. CCOM east massing -> basement + G + 2nd ONLY.
Tag 20261014y. Joe FACT 4:57 PM: main building = 2 floors + basement (tower separate);
lab (former CCM office) on 2nd floor east; unhide terrace outside lab windows.

A) Inspect dump (always)
B) Collapse SE east from 3 window rows to 2 (keep r0=G, r1=2nd; hide r2)
   Lower SE east wall top + roof to eave just above r1 heads + parapet UNVERIFIED
C) Rebuild lab behind r1 SE bays; unhide/seat terrace at lab floor
D) Nudge east interior slabs if they assumed L2; west atrium untouched
E) --save to write blend; default dry-run prints plan

RERUNNABLE. Lettering untouched. No lamps.
"""
import bpy, bmesh, math, sys, json, os, resource
from mathutils import Vector
from collections import defaultdict

SAVE = '--save' in sys.argv
TAG = '20261014y'
TAG_OLD = '20261014x'
ROOT = bpy.path.abspath('//')
PARAPET = 0.45  # UNVERIFIED
TERRACE_DEPTH = 7.0  # UNVERIFIED (photo-supported presence)

def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def clear_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col

def hide_collection(name, hide=True):
    col = bpy.data.collections.get(name)
    if not col:
        return
    col.hide_render = hide
    col.hide_viewport = hide
    for o in col.objects:
        o.hide_render = hide
        o.hide_viewport = hide

def mat(name, rgba, rough=0.55, emit=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = emit
        b.inputs['Emission Strength'].default_value = strength
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def mat_carpet(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.95
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.0, 9.0, 0.0)
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'Y'
    wv.inputs['Scale'].default_value = 1.0; wv.inputs['Distortion'].default_value = 2.0
    wv.inputs['Detail'].default_value = 3.0
    ns = nt.nodes.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value = 40.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cols = [(0.0, (0.13, 0.13, 0.15, 1)), (0.30, (0.16, 0.17, 0.20, 1)), (0.38, (0.10, 0.30, 0.45, 1)),
            (0.45, (0.18, 0.18, 0.21, 1)), (0.60, (0.45, 0.15, 0.30, 1)), (0.66, (0.15, 0.16, 0.19, 1)),
            (0.80, (0.45, 0.42, 0.12, 1)), (0.86, (0.14, 0.15, 0.18, 1)), (1.0, (0.12, 0.30, 0.20, 1))]
    cr.elements[0].position, cr.elements[0].color = cols[0]
    cr.elements[1].position, cr.elements[1].color = cols[-1]
    for p, c in cols[1:-1]:
        e = cr.elements.new(p); e.color = c
    mix = nt.nodes.new('ShaderNodeMath'); mix.operation = 'ADD'
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 0.15
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    nt.links.new(tc.outputs['Object'], ns.inputs['Vector'])
    nt.links.new(ns.outputs['Fac'], mul.inputs[0])
    nt.links.new(wv.outputs['Fac'], mix.inputs[0]); nt.links.new(mul.outputs['Value'], mix.inputs[1])
    nt.links.new(mix.outputs['Value'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def mat_lattice(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.5
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = 3.5
    fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.5
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    mx.inputs[6].default_value = (0.75, 0.75, 0.75, 1); mx.inputs[7].default_value = (0.70, 0.06, 0.04, 1)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0]); nt.links.new(sep.outputs['Z'], mth.inputs[0])
    nt.links.new(mth.outputs[0], fr.inputs[0]); nt.links.new(fr.outputs[0], gt.inputs[0])
    nt.links.new(gt.outputs[0], mx.inputs[0]); nt.links.new(mx.outputs[2], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def frame_box(name, center, size, u, v, col, material, rot_extra=0.0):
    me = bpy.data.meshes.new(name)
    sx, sy, sz = [s / 2 for s in size]
    verts = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
             (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    me.from_pydata(verts, [], [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    me.update()
    if material: me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = center
    ob.rotation_euler = (0, 0, math.atan2(u.y, u.x) + rot_extra)
    col.objects.link(ob)
    return ob

def cyl(name, loc, r, h, col, material, verts=24):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    bm.to_mesh(me); bm.free()
    if material: me.materials.append(material)
    ob = bpy.data.objects.new(name, me); ob.location = loc
    col.objects.link(ob); return ob

def cam(name, loc, target, lens=None, vfov_deg=None, hfov_deg=None, clip_end=60000):
    o = bpy.data.objects.get(name)
    if o is None:
        o = bpy.data.objects.new(name, bpy.data.cameras.new(name))
        bpy.context.scene.collection.objects.link(o)
    o.location = loc
    d = (Vector(target) - Vector(loc)).normalized()
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c = o.data; c.clip_start = 0.05; c.clip_end = clip_end; c.sensor_width = 36.0
    if hfov_deg:
        c.sensor_fit = 'HORIZONTAL'; c.lens_unit = 'FOV'; c.angle = math.radians(hfov_deg)
    elif vfov_deg:
        c.sensor_fit = 'VERTICAL'; c.lens_unit = 'FOV'; c.angle = math.radians(vfov_deg)
    elif lens:
        c.sensor_fit = 'AUTO'; c.lens_unit = 'MILLIMETERS'; c.lens = lens
    return o

# =============================================================================
# A) INSPECT
# =============================================================================
print('=' * 60)
print(f'CCOM east 2-floor rebuild {TAG}  SAVE={SAVE}')
print('=' * 60)
wo = bpy.data.objects['School of Communication and Media walls']
fh = float(wo['floor_h']); wb = float(wo['win_bottom']); wh = float(wo.get('win_h', 2.6))
print(f'walls floor_h={fh} win_bottom={wb} win_h={wh}')

wcol = bpy.data.collections.get('CCOM_windows_modelled')
east_by_row = defaultdict(list)
for o in (wcol.objects if wcol else []):
    if not o.name.startswith('CCOM_win_'): continue
    n = o.matrix_world.to_3x3() @ Vector((0, 1, 0))
    if n.x <= 0.5: continue
    loc = o.matrix_world.translation.copy()
    row = int(o.get('row', o.name.rsplit('_r', 1)[-1]))
    east_by_row[row].append((o, loc, n.normalized()))

for row in sorted(east_by_row):
    items = east_by_row[row]
    zs = [t[1].z for t in items]
    se = [t for t in items if t[1].y < 8]
    ne = [t for t in items if t[1].y >= 8]
    print(f'  east r{row}: n={len(items)} z={min(zs):.2f}..{max(zs):.2f}  SE={len(se)} NE={len(ne)}')

for nm in (f'CCOM_east_lab_{TAG_OLD}', f'CCOM_computer_lab_{TAG_OLD}',
           f'CCOM_east_terrace_{TAG_OLD}_UNVERIFIED', 'CCOM_interior_20261014v',
           'CCOM_east_facade_20261014v'):
    c = bpy.data.collections.get(nm)
    print(f'  col {nm}:', f'n={len(c.objects)} hide={c.hide_render}' if c else 'MISSING')

for o in bpy.data.objects:
    if o.name.startswith('CCOM_east_RTU_') or o.name.startswith('School of Communication and Media'):
        if any(k in o.name.lower() for k in ('roof', 'eave', 'rtu', 'walls', 'hip', 'barrel')):
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            print(f'  {o.name}: z={min(p.z for p in bb):.2f}..{max(p.z for p in bb):.2f}')

ag = bpy.data.objects.get('CCOM atrium glass (arched, 7x10 grid)')
if ag:
    bb = [ag.matrix_world @ Vector(c) for c in ag.bound_box]
    print(f'  atrium glass z={min(p.z for p in bb):.2f}..{max(p.z for p in bb):.2f}')

# SE r1 lab bays (mirror of prior r2 choice: skip end bays)
se_r1 = sorted([t for t in east_by_row.get(1, []) if t[1].y < 8], key=lambda t: t[1].y)
se_r2 = sorted([t for t in east_by_row.get(2, []) if t[1].y < 8], key=lambda t: t[1].y)
# Prior lab used middle 4 of 7 SE r2; same indices on r1
LAB_ITEMS = se_r1[1:5] if len(se_r1) >= 5 else se_r1
LAB_BAYS = [t[0].name for t in LAB_ITEMS]
print('LAB_BAYS (r1 2nd floor):', LAB_BAYS)

if not LAB_ITEMS:
    print('ERROR: no SE r1 bays'); raise SystemExit(1)

sill_r1 = sum(t[1].z for t in LAB_ITEMS) / len(LAB_ITEMS)
head_r1 = sill_r1 + wh
NEW_EAVE = round(head_r1 + PARAPET, 3)
FLOOR = round(sill_r1 - wb, 3)
CEIL = FLOOR + wb + wh  # drop ceiling at window head (photo)
print(f'PLAN: sill_r1={sill_r1:.3f} head_r1={head_r1:.3f} NEW_EAVE={NEW_EAVE} (parapet={PARAPET} UNVERIFIED)')
print(f'PLAN: lab FLOOR={FLOOR} CEIL={CEIL}')
print(f'PLAN: hide {len(se_r2)} SE r2 windows; lower SE east wall/roof to NEW_EAVE; rebuild lab+terrace {TAG}')

if not SAVE:
    print('dry-run only (pass --save to apply)'); raise SystemExit(0)

# =============================================================================
# B) MASSING: hide r2, lower SE east wall/roof, parapet, RTUs
# =============================================================================
col_mass = clear_collection(f'CCOM_east_massing_{TAG}')
m_wall = mat(f'CCOM_east_wall_plug_{TAG}', (0.88, 0.86, 0.80, 1), rough=0.55)
m_parapet = mat(f'CCOM_east_parapet_{TAG}', (0.85, 0.83, 0.78, 1), rough=0.6)
m_flat = mat(f'CCOM_east_flat_roof_{TAG}', (0.55, 0.54, 0.52, 1), rough=0.85)

# Hide ALL east r2 window instances + clear glass
n_hide = 0
for o, loc, n in east_by_row.get(2, []):
    o.hide_render = True; o.hide_viewport = True
    o['hidden_by'] = TAG; o['note'] = 'false 3rd storey removed (Joe 2-floor FACT)'
    g = bpy.data.objects.get('CCOM_east_clear_' + o.name)
    if g:
        g.hide_render = True; g.hide_viewport = True
    n_hide += 1
print(f'hidden east r2 windows: {n_hide}')

# Hide sill bands at r2 Z (~144.1)
fac = bpy.data.collections.get('CCOM_east_facade_20261014v')
if fac:
    for o in fac.objects:
        if 'sill' in o.name.lower() and abs(o.location.z - 144.0) < 1.5:
            o.hide_render = True; o.hide_viewport = True
            o['hidden_by'] = TAG

# Lower SE-east wall top vertices (x high, y < ~12, z > NEW_EAVE)
# Keep west atrium / tower / NE higher volumes intact: only verts with x > 18 and y < 12
me = wo.data
mw = wo.matrix_world
imw = mw.inverted()
n_lower = 0
# Also plug any r2 openings that remain as holes below old top: after lowering,
# verts above NEW_EAVE collapse to NEW_EAVE so holes above eave disappear from silhouette.
for v in me.vertices:
    p = mw @ v.co
    if p.x > 18.0 and p.y < 12.0 and p.z > NEW_EAVE + 0.02:
        p.z = NEW_EAVE
        v.co = imw @ p
        n_lower += 1
me.update()
print(f'lowered SE-east wall verts to z={NEW_EAVE}: {n_lower}')

# Lower SE-east portion of LiDAR roof + eave courses (same XY gate)
roof_names = [
    'School of Communication and Media roof (LiDAR)',
    'School of Communication and Media eave soffit + fascia + rafter',
    'School of Communication and Media barrel tile eave course',
    'School of Communication and Media hip + ridge cap tiles',
]
for rnm in roof_names:
    ro = bpy.data.objects.get(rnm)
    if not ro or not ro.data or not hasattr(ro.data, 'vertices'):
        continue
    rme = ro.data; rmw = ro.matrix_world; rimw = rmw.inverted()
    nl = 0
    for v in rme.vertices:
        p = rmw @ v.co
        if p.x > 18.0 and p.y < 12.0 and p.z > NEW_EAVE:
            # sit flat roof ~0.05 above eave; hide pitched look on SE east
            p.z = NEW_EAVE + 0.08
            v.co = rimw @ p
            nl += 1
    rme.update()
    print(f'  lowered {rnm}: {nl} verts')

# Visible parapet band + flat roof deck over SE east lab run (photo terrace relationship)
# Use lab bay frame for span
wobs = [t[0] for t in LAB_ITEMS]
locs = [t[1] for t in LAB_ITEMS]
n_out = sum((t[2] for t in LAB_ITEMS), Vector()); n_out.z = 0; n_out.normalize()
u = Vector((-n_out.y, n_out.x, 0)).normalized()
if u.y < 0: u = -u
v_in = -n_out
mid_xy = sum((Vector((l.x, l.y, 0)) for l in locs), Vector()) / len(locs)
bay_u = [(l - mid_xy).dot(u) for l in locs]
U0, U1 = min(bay_u) - 1.3 - 1.0, max(bay_u) + 1.3 + 1.0
# extend parapet across full SE east run (~7 bays)
if se_r1:
    all_u = [((t[1] - mid_xy).dot(u)) for t in se_r1]
    U0, U1 = min(all_u) - 1.5, max(all_u) + 1.5
ru = U1 - U0
cu = (U0 + U1) / 2

def P_world(uu, vv, zz):
    return mid_xy + u * uu + v_in * vv + Vector((0, 0, zz))

# flat roof deck (top = NEW_EAVE) spanning SE east, depth into building + out for terrace seat
deck = frame_box(f'CCOM_east_flat_roof_deck_{TAG}', P_world(cu, 3.0, NEW_EAVE - 0.15),
                 (ru + 2.0, 14.0, 0.30), u, v_in, col_mass, m_flat)
deck['UNVERIFIED'] = 'flat roof deck after 3->2 storey collapse; extent UNVERIFIED'
deck['ccom_pass'] = TAG
par = frame_box(f'CCOM_east_parapet_band_{TAG}', P_world(cu, -0.05, NEW_EAVE + PARAPET / 2 - 0.05),
                (ru + 1.5, 0.35, PARAPET), u, v_in, col_mass, m_parapet)
par['UNVERIFIED'] = f'parapet height {PARAPET}m guessed'
par['ccom_pass'] = TAG

# Basement plinth band: list-only unless we have photo — short implied band below G sill
# Photo support weak for east basement → list in custom prop, do not invent arched bays
print('basement: list-only (no clean east basement photo) — not modeled as volume')

# Lower RTUs onto new roof
for o in list(bpy.data.objects):
    if o.name.startswith('CCOM_east_RTU_'):
        # keep XY, set bottom just above NEW_EAVE
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        z0, z1 = min(p.z for p in bb), max(p.z for p in bb)
        h = z1 - z0
        o.location.z += (NEW_EAVE + 0.15 + h / 2) - (z0 + h / 2)
        o['moved_by'] = TAG
        print(f'  RTU {o.name} -> z≈{o.location.z:.2f}')

# =============================================================================
# C) Hide old x lab/terrace; rebuild lab on r1 + terrace visible
# =============================================================================
hide_collection(f'CCOM_east_lab_{TAG_OLD}', True)
hide_collection(f'CCOM_computer_lab_{TAG_OLD}', True)
# old terrace will be superseded by y terrace
hide_collection(f'CCOM_east_terrace_{TAG_OLD}_UNVERIFIED', True)

m_maroon = mat(f'CCOM_lab_mullion_maroon_{TAG}', (0.22, 0.05, 0.05, 1), rough=0.35)
m_shade = mat(f'CCOM_lab_shade_{TAG}', (0.55, 0.53, 0.50, 1), rough=0.9)
m_wall_w = mat(f'CCOM_lab_wall_white_{TAG}', (0.93, 0.93, 0.91, 1), rough=0.7)
m_ceil = mat(f'CCOM_lab_ceiling_tile_{TAG}', (0.90, 0.90, 0.88, 1), rough=0.85)
m_light = mat(f'CCOM_lab_layin_light_{TAG}', (1, 1, 1, 1), rough=0.5, emit=(1.0, 0.97, 0.92, 1), strength=3.5)
m_desk = mat(f'CCOM_lab_desk_white_{TAG}', (0.90, 0.90, 0.88, 1), rough=0.4)
m_leg = mat(f'CCOM_lab_desk_leg_maroon_{TAG}', (0.30, 0.05, 0.06, 1), rough=0.4)
m_mon = mat(f'CCOM_lab_monitor_{TAG}', (0.02, 0.02, 0.025, 1), rough=0.3)
m_arm = mat(f'CCOM_lab_monitor_arm_{TAG}', (0.75, 0.75, 0.73, 1), rough=0.4)
m_carpet = mat_carpet(f'CCOM_lab_carpet_striped_{TAG}')
m_roof = mat(f'CCOM_lab_terrace_roof_{TAG}', (0.62, 0.61, 0.58, 1), rough=0.8)
m_drain = mat(f'CCOM_lab_terrace_drain_{TAG}', (0.18, 0.18, 0.18, 1), rough=0.6)
m_yellow = mat(f'CCOM_lab_safety_rail_yellow_{TAG}', (0.85, 0.65, 0.08, 1), rough=0.4)

col_win = clear_collection(f'CCOM_east_lab_{TAG}')
col_lab = clear_collection(f'CCOM_computer_lab_{TAG}')
# Terrace now seated correctly with 2-floor massing — drop _UNVERIFIED from collection name;
# objects still tagged UNVERIFIED where depth/extent guessed.
col_ter = clear_collection(f'CCOM_east_terrace_{TAG}')

mid = sum(locs, Vector()) / len(locs); mid.z = FLOOR
W, H = 2.6, 2.6
print(f'LAB floor={FLOOR} ceil={CEIL} mid={tuple(round(x,2) for x in mid)}')

def P(uu, vv, zz):
    return mid + u * uu + v_in * vv + Vector((0, 0, zz))

bay_u = [(l - mid).dot(u) for l in locs]
for i, bu in enumerate(bay_u):
    base = locs[i] + v_in * 0.30
    def add(nm, du, dz, sx, sz, sy=0.10, _base=base, _i=i):
        c = _base + u * du + Vector((0, 0, dz))
        frame_box(f'CCOM_lab_frame_{_i}_{nm}_{TAG}', c, (sx, sy, sz), u, v_in, col_win, m_maroon)
    add('jambL', -W/2 + 0.05, H/2, 0.11, H)
    add('jambR',  W/2 - 0.05, H/2, 0.11, H)
    add('head', 0, H - 0.04, W, 0.08)
    add('sill', 0, 0.04, W, 0.08, sy=0.12)
    add('mull', 0, H/2, 0.08, H)
    add('transom', 0, H * 0.66, W, 0.08)
    sh = frame_box(f'CCOM_lab_shade_{i}_{TAG}',
                   base + v_in * 0.06 + Vector((0, 0, H * 0.66 + (H * 0.34) / 2)),
                   (W - 0.12, 0.01, H * 0.34 - 0.06), u, v_in, col_win, m_shade)
    sh['note'] = 'roller shade, photo-supported; drop height UNVERIFIED'
frame_box(f'CCOM_lab_shade_pocket_{TAG}', P(0, 0.30, CEIL - FLOOR - 0.06),
          (abs(bay_u[-1] - bay_u[0]) + W + 0.4, 0.22, 0.10), u, v_in, col_win, m_maroon)

U0b, U1b = min(bay_u) - W/2 - 1.0, max(bay_u) + W/2 + 1.0
V0, V1 = 0.35, 13.0
ru_lab, rv = (U1b - U0b), (V1 - V0)
cu_lab, cv = (U0b + U1b) / 2, (V0 + V1) / 2
frame_box(f'CCOM_lab_floor_{TAG}', P(cu_lab, cv, -0.06), (ru_lab, rv, 0.12), u, v_in, col_lab, m_carpet)
frame_box(f'CCOM_lab_ceiling_{TAG}', P(cu_lab, cv, CEIL - FLOOR + 0.03), (ru_lab, rv, 0.06), u, v_in, col_lab, m_ceil)
frame_box(f'CCOM_lab_wall_back_{TAG}', P(cu_lab, V1 + 0.06, (CEIL - FLOOR) / 2),
          (ru_lab, 0.12, CEIL - FLOOR + 0.1), u, v_in, col_lab, m_wall_w)
frame_box(f'CCOM_lab_wall_S_{TAG}', P(U0b - 0.06, cv, (CEIL - FLOOR) / 2),
          (0.12, rv, CEIL - FLOOR + 0.1), u, v_in, col_lab, m_wall_w)
frame_box(f'CCOM_lab_wall_N_{TAG}', P(U1b + 0.06, cv, (CEIL - FLOOR) / 2),
          (0.12, rv, CEIL - FLOOR + 0.1), u, v_in, col_lab, m_wall_w)
bs = sorted(bay_u)
edges = [U0b] + [x for b in bs for x in (b - W/2, b + W/2)] + [U1b]
for k in range(0, len(edges), 2):
    a_, b_ = edges[k], edges[k + 1]
    if b_ - a_ > 0.02:
        frame_box(f'CCOM_lab_lining_pier_{k}_{TAG}', P((a_ + b_) / 2, 0.36, (CEIL - FLOOR) / 2),
                  (b_ - a_, 0.04, CEIL - FLOOR), u, v_in, col_lab, m_wall_w)
frame_box(f'CCOM_lab_lining_sill_{TAG}', P(cu_lab, 0.36, 0.45), (ru_lab, 0.04, 0.9), u, v_in, col_lab, m_wall_w)
nl = 0
for lu in [U0b + 2.0 + k * 2.6 for k in range(int((ru_lab - 2.0) / 2.6) + 1)]:
    for lv in [2.5, 5.6, 8.7, 11.8]:
        if lu > U1b - 0.8: continue
        frame_box(f'CCOM_lab_light_{nl}_{TAG}', P(lu, lv, CEIL - FLOOR - 0.005),
                  (0.6, 1.2, 0.02), u, v_in, col_lab, m_light); nl += 1
cyl(f'CCOM_lab_column_{TAG}', P(U1b - 2.2, 6.5, (CEIL - FLOOR) / 2), 0.28, CEIL - FLOOR, col_lab, m_wall_w)

nd = nm_ = 0
row_us = [cu_lab - 3.4, cu_lab, cu_lab + 3.4]
for r, ru_ in enumerate(row_us):
    for seg in range(2):
        v0 = 2.2 + seg * 4.6; L = 4.2
        c = P(ru_, v0 + L / 2, 0.74)
        frame_box(f'CCOM_lab_desk_{nd}_top_{TAG}', c, (1.4, L, 0.04), u, v_in, col_lab, m_desk)
        for du in (-0.65, 0.65):
            for dv in (0.1, L - 0.1):
                frame_box(f'CCOM_lab_desk_{nd}_leg_{du}_{dv}_{TAG}', P(ru_ + du, v0 + dv, 0.36),
                          (0.04, 0.04, 0.72), u, v_in, col_lab, m_leg)
        for k in range(3):
            vv = v0 + 0.7 + k * 1.4
            frame_box(f'CCOM_lab_arm_{nm_}_{TAG}', P(ru_, vv, 0.98), (0.04, 0.04, 0.46), u, v_in, col_lab, m_arm)
            for side in (-1, 1):
                frame_box(f'CCOM_lab_mon_{nm_}_{side}_{TAG}', P(ru_ + side * 0.10, vv, 1.05),
                          (0.03, 0.56, 0.34), u, v_in, col_lab, m_mon)
            nm_ += 1
        nd += 1
for nm in LAB_BAYS:
    g = bpy.data.objects.get('CCOM_east_clear_' + nm)
    if g: g.hide_render = True
print(f'desks {nd} monitor arms {nm_} lights {nl}')

# Terrace: roof slab top ≈ lab floor / just below sill (photo)
TD = TERRACE_DEPTH
# world Z of terrace top ≈ FLOOR (lab floor) — slab thickness centered slightly below
ter_top_local = 0.0  # relative to mid.z=FLOOR
frame_box(f'CCOM_lab_terrace_roof_{TAG}', P(cu_lab, -TD / 2 - 0.15, -0.30),
          (ru_lab - 1.6, TD, 0.6), u, v_in, col_ter, m_roof)
frame_box(f'CCOM_lab_terrace_parapet_{TAG}', P(cu_lab, -TD - 0.05, 0.10),
          (ru_lab - 1.6, 0.25, 0.2), u, v_in, col_ter, m_roof)
for k, (du, dv) in enumerate([(-3.0, -2.0), (1.0, -2.5), (4.0, -1.5), (-1.0, -5.0), (3.5, -5.5)]):
    frame_box(f'CCOM_lab_terrace_drain_{k}_{TAG}', P(cu_lab + du, dv, 0.005),
              (0.5, 0.3, 0.01), u, v_in, col_ter, m_drain)
rb = P(U0b + 2.2, -1.6, 0.0)
for du in (0.0, 0.9):
    frame_box(f'CCOM_lab_rail_post_{du}_{TAG}', rb + u * du + Vector((0, 0, 0.55)),
              (0.05, 0.05, 1.1), u, v_in, col_ter, m_yellow)
frame_box(f'CCOM_lab_rail_top_{TAG}', rb + u * 0.45 + Vector((0, 0, 1.1)),
          (0.95, 0.05, 0.05), u, v_in, col_ter, m_yellow)
frame_box(f'CCOM_lab_rail_base_{TAG}', rb + u * 0.45 + Vector((0, 0, 0.03)),
          (1.1, 0.35, 0.06), u, v_in, col_ter, m_yellow)
col_ter.hide_render = False; col_ter.hide_viewport = False
for o in col_ter.objects:
    o['UNVERIFIED'] = 'terrace depth/extent guessed; yellow rail+drains photo-supported'
    o['ccom_pass'] = TAG
for o in list(col_win.objects) + list(col_lab.objects):
    o['ccom_pass'] = TAG; o['UNVERIFIED'] = True

# =============================================================================
# Cameras recalibrated to new lab Z
# =============================================================================
BU = sorted(bay_u)[1] if len(bay_u) > 1 else bay_u[0]
cam('CAM_eye_CCOM_lab_east', P(BU + 0.3, 2.4, 1.25), P(BU - 0.2, -12.0, 0.2), vfov_deg=72)
cam('CAM_eye_CCOM_lab_interior', P(U0b + 0.8, V1 - 0.6, 1.7), P(cu_lab + 1.0, 0.5, 1.0), hfov_deg=95)
cam('CAM_closeup_CCOM_lab_window', P(U0b + 3.6, -4.5, 1.6), P(U0b + 2.2, 0.0, 1.2), lens=28)
cam('CAM_closeup_CCOM_lab_window_terrace', P(U0b + 3.6, -4.5, 1.6), P(U0b + 2.2, 0.0, 1.2), lens=28)
# oblique slightly lower to show shortened mass + terrace
cam('CAM_oblique_CCOM_east', Vector((78.0, -5.0, 158.0)), Vector((22.0, -5.0, NEW_EAVE)), lens=32)
cam('CAM_eye_CCOM_east', Vector((48.0, -8.0, FLOOR + 1.6)), Vector((28.0, -5.0, FLOOR + 2.5)), lens=35)

def bd_center(name):
    o = bpy.data.objects.get('BD_' + name)
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(bb, Vector()) / 8, max(p.z for p in bb)
emp, _ = bd_center('Empire State Building')
cpt, _ = bd_center('Central Park Tower')
sky_loc = P(cu_lab - 1.0, -0.6, 1.55)
def bearing(p): return math.atan2(p.y - sky_loc.y, p.x - sky_loc.x)
be, bc = bearing(emp), bearing(cpt)
X_CPT, X_EMP = 0.388, 0.586
dth = bc - be
hfov = dth / (X_EMP - X_CPT)
aim = be + (X_EMP - 0.5) * hfov
def px_to_bearing(x): return aim - (x - 0.5) * hfov
vfov = 2 * math.atan(math.tan(hfov / 2) * 0.75)
d_emp = (emp.xy - sky_loc.xy).length
pitch = math.atan2(10.0 - sky_loc.z, d_emp) + (0.535 - 0.5) * vfov
tgt = sky_loc + Vector((math.cos(aim), math.sin(aim), 0)) * 1000 + Vector((0, 0, 1000 * math.tan(pitch)))
cam('CAM_eye_CCOM_lab_skyline', sky_loc, tgt, hfov_deg=math.degrees(hfov))
print(f'SKYCAL Empire={math.degrees(be):.2f} hfov={math.degrees(hfov):.2f} aim={math.degrees(aim):.2f} pitch={math.degrees(pitch):.2f}')

# Optional mid-distance polish: darken canopy carpet; nudge apartments up
m_carp = bpy.data.materials.get(f'MID_canopy_carpet_{TAG_OLD}')
if m_carp and m_carp.use_nodes:
    for n in m_carp.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value = (0.025, 0.05, 0.02, 1)
            print('darkened MID canopy carpet albedo')
for o in bpy.data.objects:
    if o.name.startswith(f'MID_apartment_pair_') and TAG_OLD in o.name:
        o.location.z += 8.0  # nudge up so pair reads in skyline frame
        o['nudged_by'] = TAG
        print(f'nudged {o.name} +8z')

# =============================================================================
# D) Interior slabs: hide/adjust any L2 assumption; lab = 2nd = L1 east
# Prior interior had L1_EAST = G_EAST+fh ≈ 138.95 — close to new FLOOR≈139.0. OK.
# Hide office ceiling that sat at L1+fh (would be 3rd-storey height) if above NEW_EAVE
# =============================================================================
col_i = bpy.data.collections.get('CCOM_interior_20261014v')
if col_i:
    for o in col_i.objects:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        zmax = max(p.z for p in bb)
        # Don't touch west lounge / atrium (x < 0-ish)
        cx = sum(p.x for p in bb) / 8
        if cx > 5 and zmax > NEW_EAVE + 0.5 and 'lounge' not in o.name.lower():
            # clamp or hide high east interior bits that assumed 3 floors
            if 'ceil' in o.name.lower() or 'office_ceil' in o.name.lower():
                # move ceiling underside to just below NEW_EAVE
                dz = (NEW_EAVE - 0.25) - zmax
                o.location.z += dz
                o['adjusted_by'] = TAG
                print(f'  adjusted interior {o.name} dz={dz:.2f}')

cal = dict(
    tag=TAG, floor=FLOOR, ceil=CEIL, new_eave=NEW_EAVE, parapet_UNVERIFIED=PARAPET,
    lab_bays=LAB_BAYS, sky_cam=list(sky_loc),
    empire_bearing_deg=math.degrees(be), cpt_bearing_deg=math.degrees(bc),
    hfov_deg=math.degrees(hfov), aim_deg=math.degrees(aim), pitch_deg=math.degrees(pitch),
    note='lab on 2nd floor (r1); east SE collapsed from 3 rows to 2; terrace unhidden',
    photo_px_assumptions=dict(X_CPT=X_CPT, X_EMP=X_EMP, note='tower IDs in photo UNVERIFIED'),
)
os.makedirs(os.path.join(ROOT, 'data/ccom_mid_distance'), exist_ok=True)
with open(os.path.join(ROOT, 'data/ccom_mid_distance/calibration_20261014y.json'), 'w') as f:
    json.dump(cal, f, indent=1)

for nm in ('CCOM tower 4a lettering COLLEGE OF', 'CCOM tower 4a lettering COMMUNICATION AND MEDIA'):
    print('lettering', 'OK' if bpy.data.objects.get(nm) else 'MISSING', nm)

print(f'objs win={len(col_win.objects)} lab={len(col_lab.objects)} ter={len(col_ter.objects)} '
      f'mass={len(col_mass.objects)} rss={rss():.0f}MB')
bpy.ops.wm.save_mainfile()
print('SAVED', bpy.data.filepath)
print('DONE rss', f'{rss():.0f}MB')
