"""2026-10-14 ~6:25 PM ET. Tag 20261014z.
A) Clean SE eave topology after 20261014y vert-collapse (holes/gaps).
B) CCOM queue #2: first-floor double-height lounge fit-out at existing west atrium.
   Photo: refs/ccom_x/02_20241009_SCM_study_spot.jpg (Joe: 1st fl, double-height).
   Prefer existing west atrium glass — do NOT invent a second atrium.
   Facade which-side UNVERIFIED if photo's skyline implies east; we use west atrium.

RERUNNABLE. Lettering untouched. No lamps. --save to write.
"""
import bpy, bmesh, math, sys, json, os, resource
from mathutils import Vector, Matrix
from collections import defaultdict

SAVE = '--save' in sys.argv
TAG = '20261014z'
TAG_Y = '20261014y'
ROOT = bpy.path.abspath('//')
EAVE = 143.017
PARAPET = 0.45  # UNVERIFIED
G_WEST = 137.55
ATRIUM_TOP = 146.15

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

def mat(name, rgba, rough=0.55, emit=None, strength=0.0, spec=0.3):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = spec
    if emit:
        b.inputs['Emission Color'].default_value = emit
        b.inputs['Emission Strength'].default_value = strength
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def mat_terrazzo(name):
    """White speckled terrazzo-like floor (photo)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Roughness'].default_value = 0.18
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.55
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ns = nt.nodes.new('ShaderNodeTexNoise')
    ns.inputs['Scale'].default_value = 85.0
    ns.inputs['Detail'].default_value = 12.0
    ns.inputs['Roughness'].default_value = 0.65
    ns2 = nt.nodes.new('ShaderNodeTexNoise')
    ns2.inputs['Scale'].default_value = 220.0
    ns2.inputs['Detail'].default_value = 4.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.82, 0.82, 0.80, 1)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (0.92, 0.92, 0.90, 1)
    e = cr.elements.new(0.45); e.color = (0.88, 0.88, 0.86, 1)
    e2 = cr.elements.new(0.72); e2.color = (0.78, 0.78, 0.76, 1)  # dark flecks
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[0].default_value = 0.35
    nt.links.new(tc.outputs['Object'], ns.inputs['Vector'])
    nt.links.new(tc.outputs['Object'], ns2.inputs['Vector'])
    nt.links.new(ns.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], mix.inputs[6])
    # speckles from ns2
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.62
    nt.links.new(ns2.outputs['Fac'], gt.inputs[0])
    mix2 = nt.nodes.new('ShaderNodeMix'); mix2.data_type = 'RGBA'
    mix2.inputs[7].default_value = (0.55, 0.55, 0.53, 1)
    nt.links.new(gt.outputs[0], mix2.inputs[0])
    nt.links.new(mix.outputs[2], mix2.inputs[6])
    # first mix unused path — simplify: feed ramp to mix2 A
    nt.links.new(ramp.outputs['Color'], mix2.inputs[6])
    nt.links.new(mix2.outputs[2], b.inputs['Base Color'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def mat_glass(name, rgba=(0.7, 0.85, 0.95, 1), rough=0.03):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = rough
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = 0.94
    elif 'Transmission' in b.inputs:
        b.inputs['Transmission'].default_value = 0.94
    b.inputs['Alpha'].default_value = 0.12
    if 'IOR' in b.inputs:
        b.inputs['IOR'].default_value = 1.45
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    m.blend_method = 'HASHED'
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
    # u along local X, v along local Y
    ang = math.atan2(u.y, u.x) + rot_extra
    ob.rotation_euler = (0, 0, ang)
    col.objects.link(ob)
    return ob

def box_aa(name, loc, size, col, material):
    me = bpy.data.meshes.new(name)
    sx, sy, sz = [s / 2 for s in size]
    verts = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
             (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    me.from_pydata(verts, [], [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    me.update()
    if material: me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = loc
    col.objects.link(ob)
    return ob

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

print('=' * 60)
print(f'CCOM eave clean + lounge {TAG}  SAVE={SAVE}')
print('=' * 60)

wo = bpy.data.objects['School of Communication and Media walls']
mw = wo.matrix_world
imw = mw.inverted()

# =============================================================================
# A) SE EAVE CLEAN
# Strategy: (1) bmesh merge-by-distance in SE region at eave; dissolve degenerates;
#           (2) add clean exterior cladding + roof cap plugs so silhouette is solid.
# Keep eave ≈143.017; parapet 0.45 UNVERIFIED; no 3rd storey.
# =============================================================================
col_mass = clear_collection(f'CCOM_east_eave_clean_{TAG}')
m_wall = mat(f'CCOM_east_wall_cap_{TAG}', (0.88, 0.86, 0.80, 1), rough=0.55)
m_parapet = mat(f'CCOM_east_parapet_z_{TAG}', (0.85, 0.83, 0.78, 1), rough=0.6)
m_flat = mat(f'CCOM_east_flat_roof_z_{TAG}', (0.52, 0.51, 0.49, 1), rough=0.85)
m_soffit = mat(f'CCOM_east_soffit_z_{TAG}', (0.80, 0.78, 0.74, 1), rough=0.7)

# Keep prior y parapet/deck but we'll overlay cleaner larger caps
# Bmesh cleanup on walls
me = wo.data
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()

# Tag SE verts near/above eave-2
se_verts = []
for v in bm.verts:
    p = mw @ v.co
    if p.x > 17.5 and p.y < 12.5 and p.z > EAVE - 2.5:
        se_verts.append(v)
        # snap anything above EAVE back to EAVE (re-collapse cleanly)
        if p.z > EAVE + 0.01:
            p.z = EAVE
            v.co = imw @ p

# Merge by distance among SE verts (collapse duplicate XY stacks)
bmesh.ops.remove_doubles(bm, verts=se_verts, dist=0.08)
bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()

# Dissolve degenerate / zero-area faces in SE
deg = [f for f in bm.faces if f.calc_area() < 1e-5]
if deg:
    bmesh.ops.delete(bm, geom=deg, context='FACES')
    print(f'deleted {len(deg)} degenerate faces')

# Recalc normals
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

# Count remaining non-manifold in SE
bm.edges.ensure_lookup_table()
nm = 0
for e in bm.edges:
    if not e.is_manifold:
        pts = [mw @ v.co for v in e.verts]
        if all(p.x > 16 and p.y < 14 for p in pts) and any(p.z > EAVE - 2 for p in pts):
            nm += 1
print(f'SE non-manifold after merge: {nm}')

bm.to_mesh(me)
bm.free()
me.update()
print(f'walls mesh cleaned; rss={rss():.0f}')

# Clean cladding: SE east exterior face cover from ~r1 sill band to parapet top
# Lab SE run approx: find r1 SE window mid
wcol = bpy.data.collections.get('CCOM_windows_modelled')
se_r1 = []
for o in (wcol.objects if wcol else []):
    if not o.name.startswith('CCOM_win_'): continue
    n = o.matrix_world.to_3x3() @ Vector((0, 1, 0))
    if n.x <= 0.5: continue
    loc = o.matrix_world.translation.copy()
    row = int(o.get('row', o.name.rsplit('_r', 1)[-1]))
    if row == 1 and loc.y < 8:
        se_r1.append((o, loc, n.normalized()))
se_r1.sort(key=lambda t: t[1].y)
print(f'SE r1 bays for cladding: {len(se_r1)}')

if se_r1:
    n_out = sum((t[2] for t in se_r1), Vector()); n_out.z = 0; n_out.normalize()
    u = Vector((-n_out.y, n_out.x, 0)).normalized()
    if u.y < 0: u = -u
    v_in = -n_out
    locs = [t[1] for t in se_r1]
    mid_xy = sum((Vector((l.x, l.y, 0)) for l in locs), Vector()) / len(locs)
    bay_u = [(l - mid_xy).dot(u) for l in locs]
    U0, U1 = min(bay_u) - 1.8, max(bay_u) + 1.8
    ru = U1 - U0
    cu = (U0 + U1) / 2

    def Pw(uu, vv, zz):
        return mid_xy + u * uu + v_in * vv + Vector((0, 0, zz))

    # Exterior wall cap: thin panel outside wall, from head of G (r0) top of pier to EAVE
    # Actually cover from just above r1 head (~142.57) is already eave — cover full SE face
    # from z=139.0 (mid r1) to EAVE+parapet so any holes behind are occluded from exterior
    z0, z1 = 138.90, EAVE + PARAPET
    zh = z1 - z0
    # push slightly outside facade
    cap = frame_box(f'CCOM_east_wall_cap_{TAG}', Pw(cu, -0.08, (z0 + z1) / 2),
                    (ru + 0.4, 0.22, zh), u, v_in, col_mass, m_wall)
    cap['note'] = 'clean SE exterior wall cap after eave collapse; covers y-pass holes'
    cap['ccom_pass'] = TAG

    # Cut openings in cap for r1 windows: actually simpler — only cover ABOVE r1 heads
    # Replace tall cap with eave-band only (above window heads) so windows stay visible
    bpy.data.objects.remove(cap, do_unlink=True)
    z0b, z1b = EAVE - 0.02, EAVE + PARAPET
    eave_band = frame_box(f'CCOM_east_eave_band_{TAG}', Pw(cu, -0.10, (z0b + z1b) / 2),
                          (ru + 0.6, 0.28, z1b - z0b), u, v_in, col_mass, m_parapet)
    eave_band['UNVERIFIED'] = f'parapet {PARAPET}m; clean eave band replacing collapsed verts silhouette'
    eave_band['ccom_pass'] = TAG

    # Flat roof deck — larger clean plate over SE
    deck = frame_box(f'CCOM_east_flat_roof_clean_{TAG}', Pw(cu, 4.0, EAVE - 0.12),
                     (ru + 3.0, 16.0, 0.28), u, v_in, col_mass, m_flat)
    deck['UNVERIFIED'] = 'flat roof extent after 2-floor SE; UNVERIFIED'
    deck['ccom_pass'] = TAG

    # Interior-facing soffit under eave (hides holes from terrace/lab looking up)
    sof = frame_box(f'CCOM_east_eave_soffit_{TAG}', Pw(cu, 0.35, EAVE - 0.20),
                    (ru + 0.4, 1.2, 0.08), u, v_in, col_mass, m_soffit)
    sof['ccom_pass'] = TAG

    # Side returns (S and N ends of SE run) — vertical plugs
    for label, uu in (('S', U0 - 0.15), ('N', U1 + 0.15)):
        ret = frame_box(f'CCOM_east_eave_return_{label}_{TAG}', Pw(uu, 0.5, (EAVE + PARAPET / 2)),
                        (0.30, 2.5, PARAPET + 0.15), u, v_in, col_mass, m_wall)
        ret['ccom_pass'] = TAG

    print(f'eave clean plugs: {len(col_mass.objects)} eave={EAVE} parapet={PARAPET}')
else:
    print('WARNING: no SE r1 bays — skipped cladding plugs')

# Hide old y flat deck/parapet if present (superseded by cleaner z plugs) — keep visible
# Actually keep both; z plugs are larger. Hide y deck to avoid z-fight
for nm in (f'CCOM_east_flat_roof_deck_{TAG_Y}', f'CCOM_east_parapet_band_{TAG_Y}'):
    o = bpy.data.objects.get(nm)
    if o:
        o.hide_render = True; o.hide_viewport = True
        o['hidden_by'] = TAG
        print(f'hid superseded {nm}')

# =============================================================================
# B) LOUNGE queue #2 at existing west atrium
# =============================================================================
col_lng = clear_collection(f'CCOM_lounge_20261014z')
m_terr = mat_terrazzo(f'CCOM_lounge_terrazzo_{TAG}')
m_wall_w = mat(f'CCOM_lounge_wall_white_{TAG}', (0.94, 0.94, 0.92, 1), rough=0.65)
m_mull = mat(f'CCOM_lounge_mullion_dark_{TAG}', (0.22, 0.10, 0.10, 1), rough=0.35)  # dark burgundy
m_glass = mat_glass(f'CCOM_lounge_glass_{TAG}', (0.75, 0.88, 0.95, 1), rough=0.02)
m_blue = mat(f'CCOM_lounge_chair_blue_{TAG}', (0.08, 0.35, 0.72, 1), rough=0.45)
m_chrome = mat(f'CCOM_lounge_chrome_{TAG}', (0.75, 0.76, 0.78, 1), rough=0.15, spec=0.9)
m_table = mat(f'CCOM_lounge_table_white_{TAG}', (0.95, 0.95, 0.93, 1), rough=0.25)
m_sill = mat(f'CCOM_lounge_sill_wood_{TAG}', (0.72, 0.62, 0.48, 1), rough=0.4)
m_fill = mat(f'CCOM_lounge_fill_light_{TAG}', (1, 1, 1, 1), rough=0.5,
             emit=(1.0, 0.98, 0.95, 1), strength=1.8)

ag = bpy.data.objects.get('CCOM atrium glass (arched, 7x10 grid)')
if ag:
    bb = [ag.matrix_world @ Vector(c) for c in ag.bound_box]
    ag_min = Vector((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb)))
    ag_max = Vector((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
    ag_mid = (ag_min + ag_max) / 2
    # Facade tangent from atrium rotation (local +Y of glass ≈ along facade)
    # loc=(-20.057, 11.775, 137.612) rot z=1.337 → outward roughly -X / WNW
    ang = ag.rotation_euler.z
    # glass plane: along local X of object after rot — use bbox span
    span_y = ag_max.y - ag_min.y  # ~4.96
    span_z = ag_max.z - ag_min.z  # ~8.55
    span_x = ag_max.x - ag_min.x
    print(f'atrium bbox span x={span_x:.2f} y={span_y:.2f} z={span_z:.2f} mid={tuple(round(x,2) for x in ag_mid)}')

    # Direction: along facade (mostly Y), outward (toward more negative X / west)
    u_fac = Vector((0, 1, 0))  # along glass long axis in world (bbox is Y-major)
    # Actual glass is rotated; compute from corners
    # Use rotation: local +X after rot z
    u_fac = Vector((math.cos(ang), math.sin(ang), 0)).normalized()  # along glass width
    n_out = Vector((-math.sin(ang), math.cos(ang), 0)).normalized()  # outward (west-ish)
    # Flip so n_out points toward decreasing x (outside)
    if n_out.x > 0:
        n_out = -n_out
        u_fac = -u_fac
    v_in = -n_out  # into building (east)

    # Photo grid: 5 cols × 4 rows + transom (shorter top row) — overlay INSIDE atrium glass
    # Do not replace arched glass; add dark mullion overlay matching photo rhythm (UNVERIFIED fit to arched)
    COLS, ROWS = 5, 4
    # Use atrium glass footprint for overlay
    W = max(span_x, span_y) * 0.98  # along facade
    H = span_z * 0.98
    # Center of glass for overlay — slightly inside (v_in)
    origin = ag_mid + v_in * 0.08
    origin.z = ag_min.z

    def Pg(uu, zz, vv=0.0):
        # uu along u_fac centered, zz from glass bottom, vv into room
        return origin + u_fac * uu + Vector((0, 0, zz)) + v_in * vv

    # Glass clear pane (interior see-through reinforcement)
    glass_pane = frame_box(f'CCOM_lounge_glass_pane_{TAG}', Pg(0, H / 2, 0.02),
                           (W, 0.02, H), u_fac, v_in, col_lng, m_glass)
    glass_pane['note'] = 'interior clear pane at existing west atrium; photo grid overlay separate'
    glass_pane['UNVERIFIED'] = True
    glass_pane['ccom_pass'] = TAG

    # Mullion grid 5×4 + top transom bar
    mw_bar = 0.10
    # verticals
    for i in range(COLS + 1):
        uu = -W / 2 + i * W / COLS
        frame_box(f'CCOM_lounge_mv{i}_{TAG}', Pg(uu, H / 2, 0.05),
                  (mw_bar, 0.08, H), u_fac, v_in, col_lng, m_mull)
    # horizontals: 4 primary rows + transom near top
    # row lines at 0, 1/4, 2/4, 3/4 of primary, then transom at ~0.92 H, top at H
    primary_h = H * 0.88
    h_zs = [0.0] + [primary_h * (k / ROWS) for k in range(1, ROWS)] + [primary_h, H * 0.92, H]
    for j, zz in enumerate(h_zs):
        th = 0.08 if j < len(h_zs) - 2 else 0.07
        frame_box(f'CCOM_lounge_mh{j}_{TAG}', Pg(0, zz, 0.05),
                  (W, 0.08, th), u_fac, v_in, col_lng, m_mull)
    # sill strip (light wood/cream)
    frame_box(f'CCOM_lounge_sill_{TAG}', Pg(0, 0.04, 0.06),
              (W + 0.1, 0.12, 0.08), u_fac, v_in, col_lng, m_sill)

    print(f'lounge mullion overlay: {COLS}x{ROWS}+transom on west atrium (photo match UNVERIFIED vs arched glass)')
else:
    print('ERROR: atrium glass missing — lounge window wall skipped')
    u_fac = Vector((0, 1, 0))
    n_out = Vector((-1, 0, 0))
    v_in = Vector((1, 0, 0))
    ag_mid = Vector((-20.0, 12.0, 141.0))
    W, H = 5.0, 8.5

# Terrazzo floor — replace visual of lounge G slab by overlaying new slab
lounge_xy_c = Vector((-9.75, 13.25, G_WEST))  # center of prior lounge slab
# Prior lounge: x -17.5..-2, y 6..20.5
floor = box_aa(f'CCOM_lounge_floor_terrazzo_{TAG}',
               Vector((-9.75, 13.25, G_WEST + 0.01)),
               (15.2, 14.2, 0.04), col_lng, m_terr)
floor['note'] = 'white terrazzo-like floor from study_spot photo; extent matches prior lounge shell UNVERIFIED'
floor['ccom_pass'] = TAG
floor['UNVERIFIED'] = True

# Soft fill light emitters (ceiling plane emitters — not lamps/fixtures Joe banned for north;
# these are invisible ceiling wash for interior readability, same pattern as lab lay-ins)
for i, (lx, ly) in enumerate([(-14, 10), (-10, 10), (-6, 10), (-14, 16), (-10, 16), (-6, 16)]):
    box_aa(f'CCOM_lounge_ceil_wash_{i}_{TAG}',
           Vector((lx, ly, ATRIUM_TOP - 0.25)),
           (1.8, 1.8, 0.02), col_lng, m_fill)

# Blue lounge chairs — photo has 5; people-free. Faceted high-back shell + 4-star base (simplified).
def lounge_chair(name, loc, yaw):
    # seat
    seat = box_aa(f'{name}_seat', loc + Vector((0, 0, 0.42)), (0.55, 0.55, 0.08), col_lng, m_blue)
    seat.rotation_euler[2] = yaw
    # back (faceted approx as single tall slab)
    back = box_aa(f'{name}_back', loc + Vector((-math.sin(yaw) * 0.22, math.cos(yaw) * 0.22, 0.85)),
                  (0.55, 0.10, 0.75), col_lng, m_blue)
    back.rotation_euler[2] = yaw
    # side wings (faceted look)
    for side in (-1, 1):
        wing = box_aa(f'{name}_wing{side}',
                      loc + Vector((math.cos(yaw) * side * 0.28 - math.sin(yaw) * 0.05,
                                    math.sin(yaw) * side * 0.28 + math.cos(yaw) * 0.05, 0.70)),
                      (0.08, 0.40, 0.45), col_lng, m_blue)
        wing.rotation_euler[2] = yaw
    # chrome column + 4-star base
    col_ = box_aa(f'{name}_col', loc + Vector((0, 0, 0.22)), (0.06, 0.06, 0.36), col_lng, m_chrome)
    for k in range(4):
        a = yaw + k * math.pi / 2
        arm = box_aa(f'{name}_star{k}',
                     loc + Vector((math.cos(a) * 0.22, math.sin(a) * 0.22, 0.04)),
                     (0.28, 0.05, 0.04), col_lng, m_chrome)
        arm.rotation_euler[2] = a
    for o in (seat, back, col_):
        o['UNVERIFIED'] = 'chair style approximated from photo; people-free'
        o['ccom_pass'] = TAG

def bistro_table(name, loc):
    top = box_aa(f'{name}_top', loc + Vector((0, 0, 0.72)), (0.55, 0.55, 0.03), col_lng, m_table)
    # make circular-ish with cylinder
    # replace top with cylinder
    bpy.data.objects.remove(top, do_unlink=True)
    me = bpy.data.meshes.new(f'{name}_top')
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.28, radius2=0.28, depth=0.03)
    bm.to_mesh(me); bm.free()
    me.materials.append(m_table)
    top = bpy.data.objects.new(f'{name}_top', me)
    top.location = loc + Vector((0, 0, 0.72))
    col_lng.objects.link(top)
    ped = box_aa(f'{name}_ped', loc + Vector((0, 0, 0.36)), (0.05, 0.05, 0.70), col_lng, m_chrome)
    base = box_aa(f'{name}_base', loc + Vector((0, 0, 0.02)), (0.35, 0.35, 0.03), col_lng, m_chrome)
    for o in (top, ped, base):
        o['UNVERIFIED'] = True
        o['ccom_pass'] = TAG

# Arrange facing atrium glass (west): chairs in room looking toward glass (toward -X / n_out)
# Room center ~ (-10, 13), glass at x~-20
chair_specs = [
    # (x, y, yaw) — yaw 0 = +Y; face west ≈ yaw toward -X = pi/2 or -pi/2
    (-12.5, 10.5, math.radians(200)),
    (-11.0, 11.8, math.radians(170)),
    (-12.8, 14.0, math.radians(210)),
    (-11.2, 15.5, math.radians(160)),
    (-13.0, 17.0, math.radians(195)),
]
for i, (x, y, yaw) in enumerate(chair_specs):
    lounge_chair(f'CCOM_lounge_chair_{i}_{TAG}', Vector((x, y, G_WEST)), yaw)

bistro_table(f'CCOM_lounge_table_0_{TAG}', Vector((-11.8, 11.0, G_WEST)))
bistro_table(f'CCOM_lounge_table_1_{TAG}', Vector((-12.0, 15.8, G_WEST)))

# Hide old lounge G slab under terrazzo (avoid z-fight) — keep for structure but hide render
old_floor = bpy.data.objects.get('CCOM_int_lounge_G_20261014v')
if old_floor:
    old_floor.hide_render = True
    old_floor['hidden_by'] = TAG

for o in col_lng.objects:
    o['ccom_pass'] = TAG
    if 'UNVERIFIED' not in o:
        o['UNVERIFIED'] = True

# Cameras — lounge focus
# Interior looking west at atrium window wall
cam('CAM_eye_CCOM_lounge',
    Vector((-8.5, 13.5, G_WEST + 1.45)),
    Vector((-20.0, 12.0, G_WEST + 2.5)),
    hfov_deg=72)
# Oblique exterior from west showing atrium + lounge glow
cam('CAM_oblique_CCOM_lounge',
    Vector((-45.0, 8.0, 152.0)),
    Vector((-15.0, 12.0, 142.0)),
    lens=32)
# Eye-level exterior west atrium
cam('CAM_eye_CCOM_lounge_west',
    Vector((-32.0, 12.0, G_WEST + 1.6)),
    Vector((-20.0, 12.0, G_WEST + 3.5)),
    lens=35)
# Close-up mullion / chair detail
cam('CAM_closeup_CCOM_lounge_window',
    Vector((-14.0, 12.5, G_WEST + 1.5)),
    Vector((-20.0, 12.0, G_WEST + 2.8)),
    lens=40)
# Keep east oblique for WIP set variety — nudge slightly for eave band
cam('CAM_oblique_CCOM_east',
    Vector((78.0, -5.0, 158.0)),
    Vector((22.0, -5.0, EAVE)),
    lens=32)
cam('CAM_closeup_CCOM_eave',
    Vector((42.0, -12.0, EAVE + 1.5)),
    Vector((28.0, -8.0, EAVE)),
    lens=45)

# Note props
bpy.context.scene[f'ccom_{TAG}_lounge'] = 'west_atrium_existing'
bpy.context.scene[f'ccom_{TAG}_facade_note'] = (
    'Lounge fit-out at existing west atrium glass. Photo 02_study_spot shows NYC skyline '
    'through window wall (implies east-facing); west atrium used per instruction not to invent '
    'second atrium. Facade which-side UNVERIFIED.'
)

# Lettering check
for nm in ('CCOM tower 4a lettering COLLEGE OF',
           'CCOM tower 4a lettering COMMUNICATION AND MEDIA'):
    print('lettering', 'OK' if bpy.data.objects.get(nm) else 'MISSING', nm)

# Write session note
os.makedirs(os.path.join(ROOT, 'data/ccom_lounge'), exist_ok=True)
note = dict(
    tag=TAG,
    eave=EAVE,
    parapet_UNVERIFIED=PARAPET,
    lounge=dict(
        location='existing west atrium',
        G_WEST=G_WEST,
        ATRIUM_TOP=ATRIUM_TOP,
        photo='refs/ccom_x/02_20241009_SCM_study_spot.jpg',
        grid='5 cols x 4 rows + transom dark mullion overlay',
        chairs=5,
        tables=2,
        floor='white terrazzo-like',
        facade_UNVERIFIED='photo skyline implies east; used west atrium per no-second-atrium rule',
        people='omitted (people-free)',
    ),
    eave_clean=dict(
        method='bmesh remove_doubles SE + dissolve degenerates + clean eave band/roof/soffit plugs',
        superseded_hidden=[f'CCOM_east_flat_roof_deck_{TAG_Y}', f'CCOM_east_parapet_band_{TAG_Y}'],
    ),
)
with open(os.path.join(ROOT, 'data/ccom_lounge/notes_20261014z.json'), 'w') as f:
    json.dump(note, f, indent=1)

print(f'lounge objs={len(col_lng.objects)} eave_clean objs={len(col_mass.objects)} rss={rss():.0f}MB')

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
else:
    print('dry-run (pass --save to write)')
print('DONE rss', f'{rss():.0f}MB')
