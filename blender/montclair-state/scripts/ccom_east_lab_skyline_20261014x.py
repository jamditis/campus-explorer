"""2026-10-14 ~4:31 PM ET. CCOM east lab (former CCM office) + maroon window inserts
+ skyline calibration + middle-distance proxies. Tag 20261014x.

Joe refs: refs/joe_ccom_20261014/ (README authoritative).
  - ccom_back_window_view_east.jpg  -> maroon mullions, tall panes + transom row,
    roller shade, flat roof outside at floor level, yellow safety rail/ladder (left).
  - ccom_computer_lab_interior.jpg  -> white walls, drop ceiling + lay-in lights,
    round white column, striped multicolor carpet, white desks w/ maroon legs,
    monitors on arms. People-free here.
  - old_office_window_view_city.jpg -> skyline calibration (Midtown, apartment pair,
    red/white lattice mast at right edge).

Placement: lab = top-floor (L2, floor = sill_r2 - 0.9) behind the 4 SE-run bays
045/048/051/054 (x 25.4-27.8, y -16.9..-7.0). Floor level / bay choice UNVERIFIED
(Joe: lab is the former CCM office, back/east, facing city).
Window opening sizes are the existing 2.6 x 2.6 Wing_A openings (unchanged); this pass
adds maroon inner frames + transom + shade only. Terrace roof outside = photo-supported,
extent/depth UNVERIFIED. Yellow rail = photo-supported (Joe photo), exact spot UNVERIFIED.
Middle-distance apartment pair + lattice mast: placed on the PHOTO sightline using the
calibrated cam (pixel -> bearing); distances/sizes derived from apparent size; UNVERIFIED.

4a: room shell inset 0.35 m from the exterior wall plane (no doubled walls).
RERUNNABLE. Saves only with --save.
"""
import bpy, bmesh, math, sys, json, os, resource
from mathutils import Vector

SAVE = '--save' in sys.argv
TAG = '20261014x'
ROOT = bpy.path.abspath('//')
def rss(): return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def clear_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    return col

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
    """Multicolor striped carpet (lab + office photos): dark grey base + thin colored stripes."""
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
    """Red/white banded lattice mast (aviation paint)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.5
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; mth.inputs[1].default_value = 7.0 / 2.0
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
    """Box with local X along u (facade tangent), Y along v (inward), Z up."""
    me = bpy.data.meshes.new(name)
    sx, sy, sz = [s / 2 for s in size]
    verts = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),(-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
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

# ---------------- materials
m_maroon = mat(f'CCOM_lab_mullion_maroon_{TAG}', (0.22, 0.05, 0.05, 1), rough=0.35)
m_shade = mat(f'CCOM_lab_shade_{TAG}', (0.55, 0.53, 0.50, 1), rough=0.9)
m_wall = mat(f'CCOM_lab_wall_white_{TAG}', (0.93, 0.93, 0.91, 1), rough=0.7)
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
m_tan = mat(f'MID_apartment_tan_{TAG}', (0.62, 0.52, 0.38, 1), rough=0.8)
m_lat = mat_lattice(f'MID_mast_redwhite_{TAG}')

col_win = clear_collection(f'CCOM_east_lab_{TAG}')
col_lab = clear_collection(f'CCOM_computer_lab_{TAG}')
col_mid = clear_collection(f'MID_distance_proxies_{TAG}')
col_ter = clear_collection(f'CCOM_east_terrace_{TAG}_UNVERIFIED')

# ---------------- facade frame from the 4 lab bays (top row r2)
LAB_BAYS = ['CCOM_win_054_r2', 'CCOM_win_051_r2', 'CCOM_win_048_r2', 'CCOM_win_045_r2']
wobs = [bpy.data.objects[n] for n in LAB_BAYS]
locs = [o.matrix_world.translation.copy() for o in wobs]
n_out = sum(((o.matrix_world.to_3x3() @ Vector((0, 1, 0))) for o in wobs), Vector()); n_out.z = 0; n_out.normalize()
u = Vector((-n_out.y, n_out.x, 0)).normalized()   # facade tangent
if u.y < 0: u = -u                                 # u points north-ish
v = -n_out                                         # inward
sill_z = sum(l.z for l in locs) / len(locs)
FLOOR = round(sill_z - 0.9, 3)                     # win_bottom 0.9
CEIL = FLOOR + 0.9 + 2.6                       # drop ceiling meets window head (photo); height UNVERIFIED
mid = sum(locs, Vector()) / len(locs); mid.z = FLOOR
W, H = 2.6, 2.6
print(f'LAB floor={FLOOR} ceil={CEIL} mid={tuple(round(x,2) for x in mid)} n_out={tuple(round(x,3) for x in n_out)}')

def P(uu, vv, zz):
    return mid + u * uu + v * vv + Vector((0, 0, zz))

# maroon inner frame per bay: 2 jambs, head, sill, centre mullion, transom at 2/3
bay_u = [(l - mid).dot(u) for l in locs]
for i, bu in enumerate(bay_u):
    # window instance origin = sill centre on the wall face; inner frame 0.10 m inside
    base = locs[i] + v * 0.30   # just inside the inner wall face (reads from the lab)
    def add(nm, du, dz, sx, sz, sy=0.10):
        c = base + u * du + Vector((0, 0, dz))
        frame_box(f'CCOM_lab_frame_{i}_{nm}_{TAG}', c, (sx, sy, sz), u, v, col_win, m_maroon)
    add('jambL', -W/2 + 0.05, H/2, 0.11, H)
    add('jambR',  W/2 - 0.05, H/2, 0.11, H)
    add('head', 0, H - 0.04, W, 0.08)
    add('sill', 0, 0.04, W, 0.08, sy=0.12)
    add('mull', 0, H/2, 0.08, H)
    add('transom', 0, H * 0.66, W, 0.08)
    # roller shade pulled ~down to transom (photo); semi-translucent look via grey diffuse
    sh = frame_box(f'CCOM_lab_shade_{i}_{TAG}', base + v * 0.06 + Vector((0, 0, H * 0.66 + (H * 0.34) / 2)),
                   (W - 0.12, 0.01, H * 0.34 - 0.06), u, v, col_win, m_shade)
    sh['note'] = 'roller shade, photo-supported; drop height UNVERIFIED'
# shade box head
frame_box(f'CCOM_lab_shade_pocket_{TAG}', P(0, 0.30, CEIL - 0.06), (abs(bay_u[-1] - bay_u[0]) + W + 0.4, 0.22, 0.10), u, v, col_win, m_maroon)

# ---------------- room shell (inset 0.35 m; 4a)
U0, U1 = min(bay_u) - W/2 - 1.0, max(bay_u) + W/2 + 1.0
V0, V1 = 0.35, 13.0
ru, rv = (U1 - U0), (V1 - V0)
cu, cv = (U0 + U1) / 2, (V0 + V1) / 2
frame_box(f'CCOM_lab_floor_{TAG}', P(cu, cv, -0.06), (ru, rv, 0.12), u, v, col_lab, m_carpet)
frame_box(f'CCOM_lab_ceiling_{TAG}', P(cu, cv, CEIL - FLOOR + 0.03), (ru, rv, 0.06), u, v, col_lab, m_ceil)
frame_box(f'CCOM_lab_wall_back_{TAG}', P(cu, V1 + 0.06, (CEIL - FLOOR) / 2), (ru, 0.12, CEIL - FLOOR + 0.1), u, v, col_lab, m_wall)
frame_box(f'CCOM_lab_wall_S_{TAG}', P(U0 - 0.06, cv, (CEIL - FLOOR) / 2), (0.12, rv, CEIL - FLOOR + 0.1), u, v, col_lab, m_wall)
frame_box(f'CCOM_lab_wall_N_{TAG}', P(U1 + 0.06, cv, (CEIL - FLOOR) / 2), (0.12, rv, CEIL - FLOOR + 0.1), u, v, col_lab, m_wall)

# interior white lining on the east wall: piers between bays + below-sill band (v=0.36, inside wall face)
bs = sorted(bay_u)
edges = [U0] + [x for b in bs for x in (b - W/2, b + W/2)] + [U1]
for k in range(0, len(edges), 2):
    a_, b_ = edges[k], edges[k + 1]
    if b_ - a_ > 0.02:
        frame_box(f'CCOM_lab_lining_pier_{k}_{TAG}', P((a_ + b_) / 2, 0.36, (CEIL - FLOOR) / 2), (b_ - a_, 0.04, CEIL - FLOOR), u, v, col_lab, m_wall)
frame_box(f'CCOM_lab_lining_sill_{TAG}', P(cu, 0.36, 0.45), (ru, 0.04, 0.9), u, v, col_lab, m_wall)
# lay-in lights 0.6 x 1.2 grid (simple emitters)
nl = 0
for lu in [U0 + 2.0 + k * 2.6 for k in range(int((ru - 2.0) / 2.6) + 1)]:
    for lv in [2.5, 5.6, 8.7, 11.8]:
        if lu > U1 - 0.8: continue
        frame_box(f'CCOM_lab_light_{nl}_{TAG}', P(lu, lv, CEIL - FLOOR - 0.005), (0.6, 1.2, 0.02), u, v, col_lab, m_light); nl += 1
# round white column (photo); position UNVERIFIED
cyl(f'CCOM_lab_column_{TAG}', P(U1 - 2.2, 6.5, (CEIL - FLOOR) / 2), 0.28, CEIL - FLOOR, col_lab, m_wall)

# ---------------- desks: rows run toward the windows (photo), people-free
nd = nm_ = 0
row_us = [cu - 3.4, cu, cu + 3.4]
for r, ru_ in enumerate(row_us):
    for seg in range(2):
        v0 = 2.2 + seg * 4.6; L = 4.2
        c = P(ru_, v0 + L / 2, 0.74)
        frame_box(f'CCOM_lab_desk_{nd}_top_{TAG}', c, (1.4, L, 0.04), u, v, col_lab, m_desk)
        for du in (-0.65, 0.65):
            for dv in (0.1, L - 0.1):
                frame_box(f'CCOM_lab_desk_{nd}_leg_{du}_{dv}_{TAG}', P(ru_ + du, v0 + dv, 0.36), (0.04, 0.04, 0.72), u, v, col_lab, m_leg)
        # monitors back-to-back down the spine on arms
        for k in range(3):
            vv = v0 + 0.7 + k * 1.4
            frame_box(f'CCOM_lab_arm_{nm_}_{TAG}', P(ru_, vv, 0.98), (0.04, 0.04, 0.46), u, v, col_lab, m_arm)
            for side in (-1, 1):
                frame_box(f'CCOM_lab_mon_{nm_}_{side}_{TAG}', P(ru_ + side * 0.10, vv, 1.05), (0.03, 0.56, 0.34), u, v, col_lab, m_mon)
            nm_ += 1
        nd += 1
for nm in LAB_BAYS:  # single glass layer at lab bays (instance glass stays) -> fewer reflections
    g = bpy.data.objects.get('CCOM_east_clear_' + nm)
    if g: g.hide_render = True
print(f'desks {nd} monitor arms {nm_} lights {nl}')

# ---------------- terrace roof outside (photo) + drains + yellow rail
TD = 7.0  # depth UNVERIFIED
frame_box(f'CCOM_lab_terrace_roof_{TAG}', P(cu, -TD / 2 - 0.15, -0.30), (ru - 1.6, TD, 0.6), u, v, col_ter, m_roof)
frame_box(f'CCOM_lab_terrace_parapet_{TAG}', P(cu, -TD - 0.05, 0.10), (ru - 1.6, 0.25, 0.2), u, v, col_ter, m_roof)
for k, (du, dv) in enumerate([(-3.0, -2.0), (1.0, -2.5), (4.0, -1.5), (-1.0, -5.0), (3.5, -5.5)]):
    frame_box(f'CCOM_lab_terrace_drain_{k}_{TAG}', P(cu + du, dv, 0.005), (0.5, 0.3, 0.01), u, v, col_ter, m_drain)
# yellow rail (ladder/hatch guard) – left of view in photo => south (−u) side
rb = P(U0 + 2.2, -1.6, 0.0)
for du in (0.0, 0.9):
    frame_box(f'CCOM_lab_rail_post_{du}_{TAG}', rb + u * du + Vector((0, 0, 0.55)), (0.05, 0.05, 1.1), u, v, col_ter, m_yellow)
frame_box(f'CCOM_lab_rail_top_{TAG}', rb + u * 0.45 + Vector((0, 0, 1.1)), (0.95, 0.05, 0.05), u, v, col_ter, m_yellow)
frame_box(f'CCOM_lab_rail_base_{TAG}', rb + u * 0.45 + Vector((0, 0, 0.03)), (1.1, 0.35, 0.06), u, v, col_ter, m_yellow)
# Joe's photo shows a flat roof at lab-floor level outside these windows, but our OSM+LiDAR massing has a
# straight 3-storey east wall here -> terrace kept as geometry but HIDDEN until Joe confirms floor/bay.
col_ter.hide_render = True; col_ter.hide_viewport = True
for o in col_ter.objects: o['UNVERIFIED'] = 'photo-supported terrace; conflicts with current massing'
for o in list(col_win.objects) + list(col_lab.objects):
    o['ccom_pass'] = TAG; o['UNVERIFIED'] = True

# ---------------- cameras
# back-window (photo 1080x1920 portrait): seated ~1.2 m, ~3 m back, looking out normal, slightly down
BU = sorted(bay_u)[1]
cam('CAM_eye_CCOM_lab_east', P(BU + 0.3, 2.4, 1.25), P(BU - 0.2, -12.0, 0.2), vfov_deg=72)
# lab overview matching ccom_computer_lab_interior.jpg (looking toward windows)
cam('CAM_eye_CCOM_lab_interior', P(U0 + 0.8, V1 - 0.6, 1.7), P(cu + 1.0, 0.5, 1.0), hfov_deg=95)
# close-up: maroon window + terrace/rail from outside on the terrace
cam('CAM_closeup_CCOM_lab_window_terrace', P(U0 + 3.6, -4.5, 1.6), P(U0 + 2.2, 0.0, 1.2), lens=28)

# skyline cam calibration from the photo (normalised x positions, Joe photo 1600x1200)
def bd_center(name):
    o = bpy.data.objects.get('BD_' + name)
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return sum(bb, Vector()) / 8, max(p.z for p in bb)
emp, emp_top = bd_center('Empire State Building')
cpt, cpt_top = bd_center('Central Park Tower')
sky_loc = P(cu - 1.0, -0.6, 1.55)   # just outside the glass (avoids reflections)
def bearing(p): return math.atan2(p.y - sky_loc.y, p.x - sky_loc.x)
be, bc = bearing(emp), bearing(cpt)
X_CPT, X_EMP = 0.388, 0.586
dth = bc - be                                  # +ve: CPT left (CCW) of Empire
hfov = dth / (X_EMP - X_CPT)                   # radians across full width
aim = be + (X_EMP - 0.5) * hfov                # centre bearing
def px_to_bearing(x): return aim - (x - 0.5) * hfov
dpp = hfov                                     # per normalised unit
vfov = 2 * math.atan(math.tan(hfov / 2) * 0.75)
# horizon: skyline base in photo y≈0.535; elev of Empire base from cam
d_emp = (emp.xy - sky_loc.xy).length
pitch = math.atan2(10.0 - sky_loc.z, d_emp) + (0.535 - 0.5) * vfov  # put Midtown base at y=0.535
tgt = sky_loc + Vector((math.cos(aim), math.sin(aim), 0)) * 1000 + Vector((0, 0, 1000 * math.tan(pitch)))
cam('CAM_eye_CCOM_lab_skyline', sky_loc, tgt, hfov_deg=math.degrees(hfov))
print(f'SKYCAL Empire bearing={math.degrees(be):.2f} CPT={math.degrees(bc):.2f} hfov={math.degrees(hfov):.2f} aim={math.degrees(aim):.2f} pitch={math.degrees(pitch):.2f} d_emp={d_emp:.0f}')

def elev_at_y(y):  # photo y (0 top) -> elevation angle
    return pitch - (y - 0.5) * vfov

# middle-distance: apartment pair (x≈0.518, w≈0.107, top y≈0.566, visible base y≈0.654)
APT_H = 45.0        # UNVERIFIED
GROUND = 40.0       # UNVERIFIED local ground elev near Clifton/Nutley
ang_top = elev_at_y(0.566)
# solve distance so top (GROUND+APT_H) sits at ang_top
d_apt = (GROUND + APT_H - sky_loc.z) / math.tan(ang_top) if ang_top < 0 else 4500.0
d_apt = max(1500.0, min(8000.0, d_apt))
b_apt = px_to_bearing(0.518)
w_apt = d_apt * 0.107 * hfov
c_apt = sky_loc.xy + Vector((math.cos(b_apt), math.sin(b_apt))) * d_apt
deps0 = bpy.context.evaluated_depsgraph_get()
def ground_at(xy):
    hit, loc, *_ = bpy.context.scene.ray_cast(deps0, Vector((xy.x, xy.y, 600.0)), Vector((0, 0, -1)))
    return loc.z if hit else GROUND
GROUND = ground_at(c_apt); print('apt ground', round(GROUND, 1))
tdir = Vector((-math.sin(b_apt), math.cos(b_apt), 0))
for k, off in enumerate((-0.27, 0.27)):
    cc = Vector((c_apt.x, c_apt.y, GROUND + APT_H / 2)) + tdir * (off * w_apt)
    ob = frame_box(f'MID_apartment_pair_{k}_{TAG}', cc, (w_apt * 0.42, 22.0, APT_H + 4 * k), tdir, Vector((math.cos(b_apt), math.sin(b_apt), 0)), col_mid, m_tan)
    ob['UNVERIFIED'] = 'apartment pair placed on photo sightline; identity/location unknown'
print(f'MID apt bearing={math.degrees(b_apt):.2f} dist={d_apt:.0f} width={w_apt:.0f}')
# mast at right edge (x≈0.985), top y≈0.443
b_m = px_to_bearing(0.985)
d_m = 3000.0  # UNVERIFIED
cm0 = sky_loc.xy + Vector((math.cos(b_m), math.sin(b_m))) * d_m
GROUND = ground_at(cm0); print('mast ground', round(GROUND, 1))
top_z = sky_loc.z + d_m * math.tan(elev_at_y(0.443))
h_m = max(60.0, top_z - GROUND)
cm = sky_loc.xy + Vector((math.cos(b_m), math.sin(b_m))) * d_m
mast = cyl(f'MID_lattice_mast_{TAG}', Vector((cm.x, cm.y, GROUND + h_m / 2)), 1.6, h_m, col_mid, m_lat, verts=3)
mast['UNVERIFIED'] = 'red/white lattice mast at right of Joe photo; ID (WPAT?) and position unknown'
print(f'MID mast bearing={math.degrees(b_m):.2f} dist={d_m:.0f} h={h_m:.0f}')
for o in col_mid.objects: o['ccom_pass'] = TAG


# ---------------- middle-distance canopy (low-poly) in the skyline wedge; ground by ray-cast on farfield
col_can = clear_collection(f'MID_canopy_{TAG}')
import random
random.seed(1014)
ff = bpy.data.objects.get('BD_farfield_3DEP_ortho')
deps = bpy.context.evaluated_depsgraph_get()
m_can = [mat(f'MID_canopy_green_{k}_{TAG}', c, rough=0.9) for k, c in enumerate(
    [(0.035, 0.07, 0.025, 1), (0.05, 0.09, 0.03, 1), (0.03, 0.055, 0.025, 1)])]
bm = bmesh.new()
nt_ = 0; miss = 0
half = hfov / 2 + math.radians(2)
for i in range(16000):
    d = 400.0 * (5000.0 / 400.0) ** random.random()  # log-uniform 400 m .. 5 km
    b = aim + random.uniform(-half, half)
    x = sky_loc.x + math.cos(b) * d; y = sky_loc.y + math.sin(b) * d
    hit, loc, nrm, idx, ob_, mw = bpy.context.scene.ray_cast(deps, Vector((x, y, 400.0)), Vector((0, 0, -1)))
    if not hit: miss += 1; continue
    if ob_ is None or not (ob_.name.startswith('BD_farfield') or ob_.name.startswith('Terrain') or 'terrain' in ob_.name.lower()):
        continue
    r = (5.0 + random.random() * 5.0) * (1.0 + d / 5000.0)
    ret = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    sz = 0.55 + random.random() * 0.25
    for vv in ret['verts']:
        vv.co.z *= sz
        vv.co += Vector((x, y, loc.z + r * sz * 0.85))
    mi = random.randrange(3)
    for f in {f for vv in ret['verts'] for f in vv.link_faces}:
        f.material_index = mi
    nt_ += 1
me = bpy.data.meshes.new(f'MID_canopy_{TAG}')
bm.to_mesh(me); bm.free()
for mm in m_can: me.materials.append(mm)
ob = bpy.data.objects.new(f'MID_canopy_{TAG}', me); col_can.objects.link(ob)
ob['UNVERIFIED'] = 'procedural low-poly canopy in the ESE skyline wedge (ground = farfield ortho ray-cast); stands for real tree cover, not surveyed'
# draped canopy carpet (dense cover read) ground+4 m, wedge 450 m .. 6 km
m_carp = mat(f'MID_canopy_carpet_{TAG}', (0.04, 0.075, 0.03, 1), rough=0.95)
NR, NA = 36, 28
grid = []
for ir in range(NR):
    d = 450.0 * (6000.0 / 450.0) ** (ir / (NR - 1))
    row = []
    for ia in range(NA):
        b = aim - half + 2 * half * ia / (NA - 1)
        x = sky_loc.x + math.cos(b) * d; y = sky_loc.y + math.sin(b) * d
        hit, loc, *_ = bpy.context.scene.ray_cast(deps, Vector((x, y, 400.0)), Vector((0, 0, -1)))
        row.append((x, y, (loc.z if hit else 30.0) + 4.0))
    grid.append(row)
verts = [p for row in grid for p in row]
faces = [(ir * NA + ia, ir * NA + ia + 1, (ir + 1) * NA + ia + 1, (ir + 1) * NA + ia) for ir in range(NR - 1) for ia in range(NA - 1)]
mc = bpy.data.meshes.new(f'MID_canopy_carpet_{TAG}'); mc.from_pydata(verts, [], faces); mc.update(); mc.materials.append(m_carp)
oc = bpy.data.objects.new(f'MID_canopy_carpet_{TAG}', mc); col_can.objects.link(oc)
oc['UNVERIFIED'] = 'stand-in for continuous tree cover east of campus'
print(f'MID canopy trees={nt_} miss={miss} faces={len(me.polygons)}')

cal = dict(tag=TAG, floor=FLOOR, ceil=CEIL, sky_cam=list(sky_loc), empire_bearing_deg=math.degrees(be),
           cpt_bearing_deg=math.degrees(bc), hfov_deg=math.degrees(hfov), aim_deg=math.degrees(aim),
           pitch_deg=math.degrees(pitch), apt=dict(bearing=math.degrees(b_apt), dist=d_apt, width=w_apt, xy=list(c_apt)),
           mast=dict(bearing=math.degrees(b_m), dist=d_m, h=h_m, xy=list(cm)),
           photo_px_assumptions=dict(X_CPT=X_CPT, X_EMP=X_EMP, note='tower IDs in photo UNVERIFIED'))
with open(os.path.join(ROOT, 'data/ccom_mid_distance/calibration_20261014x.json'), 'w') as f:
    json.dump(cal, f, indent=1)
for nm in ('CCOM tower 4a lettering COLLEGE OF', 'CCOM tower 4a lettering COMMUNICATION AND MEDIA'):
    print('lettering', 'OK' if bpy.data.objects.get(nm) else 'MISSING', nm)
print(f'objs win={len(col_win.objects)} lab={len(col_lab.objects)} mid={len(col_mid.objects)} rss={rss():.0f}MB')
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
