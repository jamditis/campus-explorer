"""2026-10-14 ~3:53 PM ET continuation. CCOM interior readability + memory-prep notes.

Improves the too-dark interior shell without inventing furniture:
  - Lighter wall / ceiling albedo (bounce light)
  - Daylight portal AREA lights at east window openings (SE run)
  - Stronger soft fill (existing CCOM_int_fill_east_20261014v)
  - Interior cam exposure is set at render time (not saved)

Optional small east-side detail (aerial ccom_aerial_2026_05.jpeg): 3 RTU boxes on the
flat roof east of the tower / behind the hip roofs — clearly visible gray HVAC in the photo.

Does NOT delete or move trees. RERUNNABLE. Saves only with --save.
"""
import bpy, math, sys, shutil
from mathutils import Vector
from datetime import datetime

SAVE = '--save' in sys.argv
TAG = '20261014w'
G_EAST = 134.75
fh = 4.2

def mat_set_albedo(name, rgba, rough=None):
    m = bpy.data.materials.get(name)
    if m is None or not m.use_nodes:
        return False
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value = rgba
            if rough is not None:
                n.inputs['Roughness'].default_value = rough
            return True
    return False

def link(col, ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)

def box(name, loc, size, col, material):
    mesh = bpy.data.meshes.new(name)
    sx, sy, sz = size
    hx, hy, hz = sx/2, sy/2, sz/2
    verts = [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
             (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh.from_pydata(verts, [], faces); mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    ob.location = loc
    if material:
        mesh.materials.append(material)
    link(col, ob)
    return ob

# ---- A) Albedo bumps (honest daylight interiors: pale walls, soft ceiling)
# Previous void ceiling 0.08 killed GI; walls 0.90 already pale — nudge further.
mat_set_albedo('CCOM_int_wall_white_20261014v', (0.96, 0.96, 0.94, 1), rough=0.55)
mat_set_albedo('CCOM_int_void_dark_20261014v', (0.42, 0.42, 0.40, 1), rough=0.75)  # was 0.08 — too dark for bounce
mat_set_albedo('CCOM_int_slab_G_20261014v', (0.82, 0.82, 0.80, 1), rough=0.45)
mat_set_albedo('CCOM_int_slab_L1_20261014v', (0.86, 0.84, 0.80, 1), rough=0.5)
mat_set_albedo('CCOM_int_newsroom_floor_20261014v', (0.72, 0.73, 0.74, 1), rough=0.4)
print('albedo updated')

# ---- B) Daylight portals at east SE windows (AREA, sun-ish). One per floor row cluster.
col_i = bpy.data.collections.get('CCOM_interior_20261014v')
if col_i is None:
    col_i = bpy.data.collections.new('CCOM_interior_20261014v')
    bpy.context.scene.collection.children.link(col_i)

# Remove prior portals from this tag (rerunnable)
for o in list(col_i.objects):
    if o.name.startswith(f'CCOM_int_portal_east_{TAG}') or o.name.startswith('CCOM_int_portal_east_20261014w'):
        bpy.data.objects.remove(o, do_unlink=True)

east_wins = []
wcol = bpy.data.collections.get('CCOM_windows_modelled')
for o in (wcol.objects if wcol else []):
    n = o.matrix_world.to_3x3() @ Vector((0, 1, 0))
    if n.x > 0.5:
        east_wins.append((o.matrix_world.translation.copy(), n.normalized(), o.name))

# SE run only for the interior cam (y < 8) — portals just inside openings facing in
se = [w for w in east_wins if w[0].y < 8]
from collections import defaultdict
rows = defaultdict(list)
for loc, n, nm in se:
    rows[round(loc.z, 1)].append((loc, n, nm))

n_port = 0
for z, items in sorted(rows.items()):
    # one portal per row spanning the SE openings
    items.sort(key=lambda t: t[0].y)
    n_avg = sum((t[1] for t in items), Vector()).normalized()
    mid = sum((t[0] for t in items), Vector()) / len(items)
    # just inside the wall
    p = mid - n_avg * 0.35 + Vector((0, 0, 1.2))
    nm = f'CCOM_int_portal_east_{TAG}_z{z}'
    data = bpy.data.lights.new(nm, 'AREA')
    data.energy = 180.0 * max(1, len(items) / 3)  # scale with window count
    data.size = max(4.0, (max(t[0].y for t in items) - min(t[0].y for t in items)) + 1.5)
    data.size_y = 2.4
    data.shape = 'RECTANGLE'
    data.color = (1.0, 0.97, 0.92)  # daylight
    # Cycles portal helps light through openings
    if hasattr(data, 'cycles'):
        data.cycles.is_portal = False  # portal-only emits no light; we want fill emission
    o = bpy.data.objects.new(nm, data)
    o.location = p
    # aim inward (-n)
    direction = (-n_avg).normalized()
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    link(col_i, o)
    o['ccom_pass'] = TAG
    o['UNVERIFIED'] = False  # daylight through existing openings
    n_port += 1
print('portals', n_port, 'SE wins', len(se))

# ---- C) Stronger existing fill
fl = bpy.data.objects.get('CCOM_int_fill_east_20261014v')
if fl and fl.type == 'LIGHT':
    fl.data.energy = 900.0
    fl.data.size = 8.0
    fl.data.color = (1.0, 0.98, 0.95)
    fl.location = Vector((16.0, -3.0, G_EAST + 3.8))
    print('fill energy', fl.data.energy)

# ---- D) Small east-side roof RTUs from aerial (ccom_aerial_2026_05.jpeg)
# Gray HVAC sitting on flat roof east of tower / behind hip roofs. Positions
# photo-composed from aerial relative to tower — UNVERIFIED exact XY (±2 m).
col_e = bpy.data.collections.get('CCOM_east_facade_20261014v')
if col_e is None:
    col_e = bpy.data.collections.new('CCOM_east_facade_20261014v')
    bpy.context.scene.collection.children.link(col_e)
for o in list(col_e.objects):
    if o.name.startswith(f'CCOM_east_RTU_{TAG}'):
        bpy.data.objects.remove(o, do_unlink=True)

m_rtu = bpy.data.materials.get(f'CCOM_east_RTU_metal_{TAG}')
if m_rtu is None:
    m_rtu = bpy.data.materials.new(f'CCOM_east_RTU_metal_{TAG}')
    m_rtu.use_nodes = True
    nt = m_rtu.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.35, 0.36, 0.37, 1)
    bsdf.inputs['Roughness'].default_value = 0.45
    if 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value = 0.55
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

# Tower approx at ~(-6, 12); flat roof east of it toward city ~ x 8..22, y -2..10, z roof ~147–149
# LiDAR wing roofs vary; place RTUs on flat section between SE hip and tower
rtus = [
    # (name, loc, size) — sizes typical package RTU
    (f'CCOM_east_RTU_{TAG}_1', Vector((10.5, 4.0, 148.55)), (3.2, 2.0, 1.4)),
    (f'CCOM_east_RTU_{TAG}_2', Vector((14.0, 1.5, 148.55)), (2.8, 1.8, 1.2)),
    (f'CCOM_east_RTU_{TAG}_3', Vector((8.0, 7.5, 148.70)), (2.4, 1.6, 1.1)),
]
for nm, loc, sz in rtus:
    ob = box(nm, loc, sz, col_e, m_rtu)
    ob['ccom_pass'] = TAG
    ob['UNVERIFIED'] = True  # exact XY from aerial composition
    ob['source'] = 'ccom_aerial_2026_05.jpeg HVAC on flat roof E of tower'
print('RTUs', len(rtus))

# Mark interior collection objects
for o in col_i.objects:
    if 'ccom_pass' not in o:
        o['ccom_pass'] = TAG

if SAVE:
    src = bpy.data.filepath
    ts = datetime.now().strftime('%Y%m%d%H%M')
    bak = src.replace('.blend', f'_pre_interior_readability_{ts}.blend')
    shutil.copy2(src, bak)
    print('backup', bak)
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
else:
    print('dry-run')
print('DONE')
