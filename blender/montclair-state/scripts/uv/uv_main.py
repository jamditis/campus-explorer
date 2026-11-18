"""Session uv (Nov 6 2026 ~7:23–~8:12 AM ET, MAIN, day-10 OPEN): Freeman Hall hero first build.

Photo language from Digital Commons slides #1096 (entrance) + #1114 (side). Sizes UNVERIFIED.
OSM way 312845860 footprint MATCHES MAIN 'Freeman Hall walls' (delta 0). Keep ub wall-tops 147.05
and UC_Freeman_parapet_UNVERIFIED. Do NOT delete ub/uc LiDAR walls — overlays / hide conflicting
blank north-face panels only.

North face (edge 6, ~15.1 m, outward n≈(+0.23,+0.97)): photo-facing entrance composition
  left (east, viewer-left when approaching from lawn): cream brick + GRACE H. FREEMAN HALL lettering
    + large window bay with lower reddish-orange solid panels
  centre: recessed glass curtain + 4 white-framed doors under flat concrete canopy + 2 globe pendants
  right (west): decorative concrete breezeway/screen block (geometric)
  steps (~4 risers) + orange square-profile handrails

Long east face (edge 5): start recessed vertical window rhythm (1114) if built.

Entrances only where OSM footways meet footprint + 1096 composition. No invented street furniture
beyond photo-backed rails/globes/lettering/screen.

REVERT=1 removes uv_obj / uv_mat / UV_* collections and unhides any uv_hid faces.
Tag uv_obj; collection UV_Freeman_*_UNVERIFIED.
"""
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/uv'
os.makedirs(DATA, exist_ok=True)
COLN = 'UV_Freeman_entrance_1096_UNVERIFIED'
COLN2 = 'UV_Freeman_side_windows_1114_UNVERIFIED'
OSM = json.load(open(DATA + '/freeman_osm_probe.json'))

def revert():
    # restore hidden wall faces
    for o in bpy.data.objects:
        me = o.data
        if me is None or not hasattr(me, 'polygons'): continue
        if me.get('uv_hid_faces'):
            for fi in me['uv_hid_faces']:
                if 0 <= int(fi) < len(me.polygons):
                    me.polygons[int(fi)].hide = False
            del me['uv_hid_faces']
    for o in [o for o in list(bpy.data.objects) if o.get('uv_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            if t == 'MESH': bpy.data.meshes.remove(me)
            elif t == 'CAMERA': bpy.data.cameras.remove(me)
            elif t == 'FONT':
                try: bpy.data.curves.remove(me)
                except Exception: pass
            elif t == 'CURVE':
                try: bpy.data.curves.remove(me)
                except Exception: pass
    for m in [m for m in list(bpy.data.materials) if m.get('uv_mat')]:
        bpy.data.materials.remove(m)
    for c in (COLN, COLN2, 'UV_Freeman_cams'):
        col = bpy.data.collections.get(c)
        if col: bpy.data.collections.remove(col)
    print('UV REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

# ---------- helpers ----------
def ensure_coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c

def mat(name, rgb, rough=0.85, metal=0.0, spec=0.5, alpha=1.0, noise=0.0, brick=False, brick_mortar=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; m['uv_mat'] = 1
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    try: b.inputs['Specular IOR Level'].default_value = spec
    except Exception: pass
    if alpha < 1.0:
        m.blend_method = 'HASHED'
        try: b.inputs['Alpha'].default_value = alpha
        except Exception: pass
    if brick:
        t = nt.nodes.new('ShaderNodeTexBrick')
        t.inputs['Color1'].default_value = (*rgb, 1)
        t.inputs['Color2'].default_value = (rgb[0]*0.88, rgb[1]*0.86, rgb[2]*0.82, 1)
        mort = brick_mortar or (0.55, 0.52, 0.46)
        t.inputs['Mortar'].default_value = (*mort, 1)
        t.inputs['Brick Width'].default_value = 0.21
        t.inputs['Row Height'].default_value = 0.065
        t.inputs['Mortar Size'].default_value = 0.009
        t.inputs['Scale'].default_value = 1.0
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Object'], t.inputs['Vector'])
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    elif noise:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.2; n.inputs['Detail'].default_value = 6
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].color = (rgb[0]*(1-noise), rgb[1]*(1-noise), rgb[2]*(1-noise), 1)
        r.color_ramp.elements[1].color = (*rgb, 1)
        nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*rgb, 1)
    return m

M = dict(
    brick=mat('UV_Freeman_cream_brick_UNVERIFIED', (0.72, 0.66, 0.54), 0.9, brick=True, brick_mortar=(0.50, 0.46, 0.40)),
    conc=mat('UV_Freeman_concrete_canopy_UNVERIFIED', (0.62, 0.60, 0.56), 0.88, noise=0.12),
    glass=mat('UV_Freeman_curtain_glass_UNVERIFIED', (0.55, 0.62, 0.68), 0.05, 0.0, spec=0.85, alpha=0.35),
    white=mat('UV_Freeman_white_frame_UNVERIFIED', (0.92, 0.92, 0.90), 0.45, 0.15),
    orange=mat('UV_Freeman_orange_panel_rail_UNVERIFIED', (0.72, 0.28, 0.10), 0.55, 0.05),
    darkred=mat('UV_Freeman_window_frame_darkred_UNVERIFIED', (0.28, 0.10, 0.07), 0.5, 0.2),
    screen=mat('UV_Freeman_screen_block_UNVERIFIED', (0.70, 0.68, 0.62), 0.82, noise=0.08),
    letter=mat('UV_Freeman_lettering_dark_UNVERIFIED', (0.05, 0.05, 0.05), 0.55, 0.1),
    globe=mat('UV_Freeman_globe_pendant_UNVERIFIED', (0.95, 0.94, 0.90), 0.25, 0.0, spec=0.9),
    step=mat('UV_Freeman_step_concrete_UNVERIFIED', (0.58, 0.56, 0.52), 0.9, noise=0.1),
)

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
        o = bpy.data.objects.new(s.name, me); s.coll.objects.link(o); o['uv_obj'] = 1
        o['UNVERIFIED'] = 'uv Freeman Hall day-10; sizes UNVERIFIED; photo language 1096/1114'
        for p in me.polygons: p.use_smooth = False
        return o

# North face frame
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U = Vector((e6['u'][0], e6['u'][1], 0)).normalized()   # west along face (a→b)
N = Vector((e6['n'][0], e6['n'][1], 0)).normalized()   # outward north
A = Vector((e6['a'][0], e6['a'][1], 0))  # east end
B = Vector((e6['b'][0], e6['b'][1], 0))  # west end
MID = (A + B) / 2
FACE_LEN = (B - A).length  # ~15.07

# Grade at north face from wall verts near edge
wo = bpy.data.objects['Freeman Hall walls']
mw = wo.matrix_world
base_zs = []
for v in wo.data.vertices:
    p = mw @ v.co
    # near north face
    if p.y > -174 and p.z < 132:
        base_zs.append(p.z)
GR = sorted(base_zs)[len(base_zs)//2] if base_zs else 128.5
# wall face plane offset: overlays sit just outside
OUT = 0.08  # m proud of wall
TOPZ = 147.05
ROOFZ = 147.023

col = ensure_coll(COLN)
log = {'session': 'uv', 'GR': round(GR, 3), 'face_len': round(FACE_LEN, 3), 'mid': [round(MID.x, 2), round(MID.y, 2)]}

# Note: do NOT destroy ub/uc LiDAR walls. Overlays sit proud of the north face
# (OUT≈0.08–0.30 m) so they cover blank stucco without deleting faces.
# (MeshPolygon has .hide but no .hide_render in Blender 4.5; overlays preferred.)
log['hid_north_faces'] = 0
log['approach'] = 'overlays_proud_of_walls_no_delete'

# Layout along face from east (t=0 at A) to west (t=FACE_LEN at B), viewer-left=east:
# 0–3.4m brick lettering wing; 3.4–6.6m orange-panel window; 6.6–12.0m glass entrance; 12.0–15.07m screen
T_LET0, T_LET1 = 0.15, 3.35
T_WIN0, T_WIN1 = 3.35, 6.55
T_ENT0, T_ENT1 = 6.55, 12.05
T_SCR0, T_SCR1 = 12.05, FACE_LEN - 0.10

def along(t):
    return A + U * t

# ---- 1) Cream brick lettering wing (left / east) ----
bw = T_LET1 - T_LET0
bc = along((T_LET0 + T_LET1) / 2)
mb = MB('UV_Freeman_N_lettering_brick_wing_UNVERIFIED', [M['brick'], M['letter']], col)
mb.box(bc + N * (OUT + 0.10), U, N, bw, 0.28, GR - 0.05, TOPZ - 0.15, 0)
# lettering plate (dark block letters as a flat relief plate — text mesh separate)
mb.box(bc + N * (OUT + 0.26), U, N, bw * 0.88, 0.04, GR + 8.2, GR + 9.6, 1)
ob_brick = mb.done()

# Text object for GRACE H. FREEMAN HALL
def add_lettering():
    curve = bpy.data.curves.new('UV_Freeman_lettering_curve', 'FONT')
    curve.body = 'GRACE H. FREEMAN HALL'
    curve.size = 0.42
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    curve.extrude = 0.02
    o = bpy.data.objects.new('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED', curve)
    col.objects.link(o); o['uv_obj'] = 1
    o.data.materials.append(M['letter'])
    # place on brick face, reading left-to-right when viewed from north (looking south)
    # Font local +X is text direction; map to -U (east→west is wrong for reading — want east to west = -U? 
    # Approaching from north looking south: text should read left→right = east→west = +U direction? 
    # A is east, B is west, U points A→B = east→west. Viewer's left=east=A, right=west=B.
    # Text left-to-right for viewer = east to west = +U. Font +X → +U.
    # Font +Y is up → +Z. Font faces +Z by default for 2D; for wall we need text facing +N (outward).
    # Default font is in XY plane facing +Z. Rotate so local +Z → +N, local +Y → +Z, local +X → +U.
    # Basis: X→U, Y→Z, Z→N
    R = Matrix((
        (U.x, 0, N.x, 0),
        (U.y, 0, N.y, 0),
        (0, 1, 0, 0),
        (0, 0, 0, 1),
    ))
    o.matrix_world = Matrix.Translation(Vector((bc.x, bc.y, GR + 8.9)) + N * (OUT + 0.30)) @ R
    return o
o_let = add_lettering()

# ---- 2) Orange-panel window bay ----
ww = T_WIN1 - T_WIN0
wc = along((T_WIN0 + T_WIN1) / 2)
mw_ = MB('UV_Freeman_N_orange_panel_window_bay_UNVERIFIED', [M['white'], M['glass'], M['orange'], M['brick']], col)
# outer brick surround strip
mw_.box(wc + N * (OUT + 0.10), U, N, ww, 0.28, GR - 0.05, TOPZ - 0.15, 3)
# upper clear glass panes (multi)
n_cols = 3
pane_w = (ww - 0.25) / n_cols
for i in range(n_cols):
    pc = along(T_WIN0 + 0.12 + pane_w * (i + 0.5))
    # upper glass
    mw_.box(pc + N * (OUT + 0.18), U, N, pane_w - 0.06, 0.06, GR + 4.6, TOPZ - 0.6, 1)
    # lower orange solid panel
    mw_.box(pc + N * (OUT + 0.18), U, N, pane_w - 0.06, 0.08, GR + 0.4, GR + 4.5, 2)
    # white mullion between (except last)
    if i < n_cols - 1:
        mc = along(T_WIN0 + 0.12 + pane_w * (i + 1))
        mw_.box(mc + N * (OUT + 0.20), U, N, 0.08, 0.10, GR + 0.35, TOPZ - 0.55, 0)
# white frame border
mw_.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, GR + 0.35, GR + 0.50, 0)
mw_.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, TOPZ - 0.70, TOPZ - 0.55, 0)
mw_.box(wc + N * (OUT + 0.22), U, N, ww - 0.15, 0.05, GR + 4.45, GR + 4.65, 0)  # mid rail
ob_win = mw_.done()

# ---- 3) Recessed glass curtain entrance + 4 doors + canopy + globes ----
ew = T_ENT1 - T_ENT0
ec = along((T_ENT0 + T_ENT1) / 2)
recess = 0.85  # recessed into building
me = MB('UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED',
        [M['white'], M['glass'], M['conc'], M['globe'], M['orange'], M['step']], col)
# recessed curtain wall plane (tall multi-pane)
me.box(ec + N * (OUT - recess), U, N, ew - 0.2, 0.08, GR + 0.05, TOPZ - 0.2, 1)
# white mullions vertical ×5 (4 door bays)
door_w = (ew - 0.35) / 4
for i in range(5):
    mc = along(T_ENT0 + 0.18 + door_w * i)
    me.box(mc + N * (OUT - recess + 0.04), U, N, 0.07, 0.10, GR + 0.05, TOPZ - 0.25, 0)
# horizontal mullions
for z in (GR + 2.55, GR + 5.5, GR + 8.5, GR + 11.5, TOPZ - 1.5):
    me.box(ec + N * (OUT - recess + 0.04), U, N, ew - 0.25, 0.08, z - 0.04, z + 0.04, 0)
# 4 white-framed glass doors at ground
for i in range(4):
    dc = along(T_ENT0 + 0.18 + door_w * (i + 0.5))
    me.box(dc + N * (OUT - recess + 0.06), U, N, door_w - 0.12, 0.06, GR + 0.05, GR + 2.45, 1)
    # white door frame
    me.box(dc + N * (OUT - recess + 0.09), U, N, door_w - 0.08, 0.04, GR + 0.05, GR + 0.12, 0)
    me.box(dc + N * (OUT - recess + 0.09), U, N, door_w - 0.08, 0.04, GR + 2.38, GR + 2.50, 0)
    me.box(dc + N * (OUT - recess + 0.09) + U * ((door_w - 0.12) / 2), U, N, 0.05, 0.04, GR + 0.05, GR + 2.50, 0)
    me.box(dc + N * (OUT - recess + 0.09) - U * ((door_w - 0.12) / 2), U, N, 0.05, 0.04, GR + 0.05, GR + 2.50, 0)
    # horizontal push bar
    me.box(dc + N * (OUT - recess + 0.12), U, N, door_w - 0.22, 0.03, GR + 1.05, GR + 1.12, 0)
# side returns of recess (brick-toned concrete)
for t in (T_ENT0, T_ENT1):
    rc = along(t)
    me.box(rc + N * (OUT - recess / 2), N, U, recess, 0.20, GR - 0.05, TOPZ - 0.15, 2)
# flat concrete canopy
can_dep = 2.2; can_z0 = GR + 3.55; can_z1 = GR + 3.85
me.box(ec + N * (OUT + can_dep / 2 - 0.15), U, N, ew + 0.6, can_dep, can_z0, can_z1, 2)
# canopy edge fascia
me.box(ec + N * (OUT + can_dep - 0.15), U, N, ew + 0.65, 0.12, can_z0 - 0.08, can_z1 + 0.02, 2)
# two white globe pendants under canopy
for sgn in (-1, 1):
    gc = ec + U * (sgn * ew * 0.22) + N * (OUT + can_dep * 0.45)
    # stem
    me.box(gc, U, N, 0.04, 0.04, can_z0 - 0.55, can_z0, 0)
    # globe (approx box → will look ok at mid distance; sphere via icosphere below)
ob_ent = me.done()

# actual globe spheres
def add_globe(c, z):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.18)
    me = bpy.data.meshes.new('UV_Freeman_globe_mesh')
    bm.to_mesh(me); bm.free()
    me.materials.append(M['globe'])
    o = bpy.data.objects.new('UV_Freeman_N_globe_pendant_UNVERIFIED', me)
    col.objects.link(o); o['uv_obj'] = 1
    o.location = (c.x, c.y, z)
    # emission-ish: raise value via principled
    return o
for sgn in (-1, 1):
    gc = ec + U * (sgn * ew * 0.22) + N * (OUT + can_dep * 0.45)
    add_globe(gc, can_z0 - 0.72)

# steps (~4 risers) + orange handrails
n_risers = 4
riser = 0.155; tread = 0.32
ms = MB('UV_Freeman_N_entrance_steps_handrails_UNVERIFIED', [M['step'], M['orange']], col)
for i in range(n_risers):
    z0 = GR - (n_risers - i) * riser
    z1 = z0 + riser
    depth_i = (n_risers - i) * tread
    sc = ec + N * (OUT + recess * 0.1 + depth_i / 2 + 0.15)
    ms.box(sc, U, N, ew + 0.5, depth_i + 0.05, z0, z1, 0)
# landing at door sill
ms.box(ec + N * (OUT - recess * 0.3), U, N, ew + 0.3, recess * 0.7, GR - 0.02, GR + 0.05, 0)
# orange square-profile handrails flanking steps
for sgn in (-1, 1):
    hc = ec + U * (sgn * (ew / 2 + 0.35)) + N * (OUT + 1.0)
    # posts
    for d in (0.3, 1.0, 1.7):
        pc = ec + U * (sgn * (ew / 2 + 0.35)) + N * (OUT + d)
        ms.box(pc, U, N, 0.05, 0.05, GR - n_risers * riser, GR - n_risers * riser + 0.95, 1)
    # top rail
    ms.box(ec + U * (sgn * (ew / 2 + 0.35)) + N * (OUT + 1.0), N, U, 1.5, 0.05, GR - n_risers * riser + 0.92, GR - n_risers * riser + 0.98, 1)
ob_steps = ms.done()

# ---- 4) Decorative concrete screen block (right / west) ----
sw = T_SCR1 - T_SCR0
sc_ = along((T_SCR0 + T_SCR1) / 2)
msc = MB('UV_Freeman_N_screen_block_breezeway_UNVERIFIED', [M['screen'], M['conc']], col)
# outer frame
msc.box(sc_ + N * (OUT + 0.12), U, N, sw, 0.30, GR - 0.05, TOPZ - 0.2, 1)
# geometric star/floral screen: grid of rotated diamond/cross openings as solid blocks with gaps
cell = 0.55
n_u = max(2, int(sw / cell))
n_z = max(4, int((TOPZ - GR - 0.5) / cell))
for iu in range(n_u):
    for iz in range(n_z):
        # checkerboard solid cells → star-like voids between
        if (iu + iz) % 2 == 0: continue
        uc = T_SCR0 + (iu + 0.5) * (sw / n_u)
        zc = GR + 0.4 + (iz + 0.5) * ((TOPZ - GR - 0.8) / n_z)
        pc = along(uc)
        # small rotated square approx as axis-aligned block (reads as breezeway pattern mid-distance)
        msc.box(pc + N * (OUT + 0.18), U, N, sw / n_u * 0.72, 0.22, zc - cell * 0.32, zc + cell * 0.32, 0)
ob_scr = msc.done()

# ---- 5) Side elevation vertical window rhythm on long EAST face (edge 5) — start ----
e5 = [e for e in OSM['edges'] if e['i'] == 5][0]
U5 = Vector((e5['u'][0], e5['u'][1], 0)).normalized()  # along face NE
N5 = Vector((e5['n'][0], e5['n'][1], 0)).normalized()  # outward east
A5 = Vector((e5['a'][0], e5['a'][1], 0))
L5 = e5['len']
col2 = ensure_coll(COLN2)
# Recessed vertical strips every ~3.6 m (UNVERIFIED pitch from 1114 rhythm)
pitch = 3.6
n_bays = max(1, int((L5 - 4.0) / pitch))
msw = MB('UV_Freeman_E_recessed_vertical_windows_UNVERIFIED', [M['darkred'], M['glass'], M['brick']], col2)
built = 0
for i in range(n_bays):
    t = 2.0 + pitch * (i + 0.5)
    if t > L5 - 2.0: break
    c = A5 + U5 * t
    # recessed dark frame strip full height
    msw.box(c + N5 * (OUT - 0.12), U5, N5, 1.15, 0.30, GR + 0.8, TOPZ - 0.4, 0)
    # glass panes stacked
    for zi, (z0, z1) in enumerate([(GR+1.0, GR+3.6), (GR+3.9, GR+6.5), (GR+6.8, GR+9.4), (GR+9.7, GR+12.3), (GR+12.6, TOPZ-0.6)]):
        if z1 <= z0: continue
        msw.box(c + N5 * (OUT - 0.05), U5, N5, 0.95, 0.06, z0, z1, 1)
    built += 1
ob_side = msw.done()
log['east_window_bays'] = built

# ---- cameras ----
cc = ensure_coll('UV_Freeman_cams')
def add_cam(name, loc, target, lens=32):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 5000
    o = bpy.data.objects.new(name, cd); cc.objects.link(o); o['uv_obj'] = 1
    o.location = loc
    # point at target
    direction = Vector(target) - Vector(loc)
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# aerial/oblique overview
add_cam('UV_CAM_oblique_Freeman_from_NE',
        (MID.x + 35, MID.y + 40, GR + 28),
        (MID.x - 5, MID.y - 25, GR + 10), 28)
# eye-level entrance (from north lawn)
add_cam('UV_CAM_eye_Freeman_N_entrance',
        (ec.x + N.x * 14, ec.y + N.y * 14, GR + 1.65),
        (ec.x, ec.y, GR + 2.5), 32)
# eye-level side (from east)
add_cam('UV_CAM_eye_Freeman_E_side',
        (A5.x + N5.x * 22 + U5.x * L5 * 0.45, A5.y + N5.y * 22 + U5.y * L5 * 0.45, GR + 1.7),
        (A5.x + U5.x * L5 * 0.45, A5.y + U5.y * L5 * 0.45, GR + 8), 30)
# close-up entrance detail
add_cam('UV_CAM_closeup_Freeman_N_entrance_doors',
        (ec.x + N.x * 6.5, ec.y + N.y * 6.5, GR + 1.55),
        (ec.x - recess * N.x * 0.3, ec.y - recess * N.y * 0.3, GR + 2.0), 40)

log['objects'] = [o.name for o in list(col.objects) + list(col2.objects) + list(cc.objects)]
log['n_uv_obj'] = sum(1 for o in bpy.data.objects if o.get('uv_obj'))
json.dump(log, open(DATA + '/uv_main.json', 'w'), indent=2)
print('UV MAIN', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
