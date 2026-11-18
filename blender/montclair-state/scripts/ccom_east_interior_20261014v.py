"""2026-10-14 ~3:26 PM ET. CCOM east (back) facade pass + interior shell.

Joe TOP PRIORITY (3:14 PM): full CCOM — back (east, NYC-facing) facade with real
window geometry + begin interior (NJ PBS newsroom ground floor + floor above /
central offices + atrium/lounge if refs support it). Skyline must read east from
interior views. Refs: montclair-state/refs/ccom_google/ + ccom_x/.

THIS PASS (scoped ~45 min):
  A) East facade: existing 31 CCOM_Win_Wing_A openings (from ccom_windows.py) are
     kept. Adds a continuous exterior sill band on the two main east runs (SE + NE)
     so the punched openings read as a coherent back facade. No new street furniture.
     No arched east bays — no clean eye-level east photo (README gap); listed UNVERIFIED.
  B) Interior shell (collection CCOM_interior_20261014v):
     - West atrium/lounge G slab + double-height void volume (matches existing west
       arched atrium glass 137.6–146.2; Joe: lounge first floor, very high ceilings).
     - Newsroom G slab (central/east, light grey raised-access tone).
     - L1 office slab (central, directly above newsroom zone — Joe's office floor).
     - Red-framed interior glass partition (simplified) between lounge and newsroom
       (from mediashift_08 / njpbs_newsroom / wordcamp refs).
     - Clear interior glass panes on east openings (no room-box) so an interior cam
       looking east sees the NJ_NY backdrop; east window *instances* keep room boxes
       for exterior cams (hidden only at interior-render time via companion flag).
  C) Cameras: CAM_oblique_CCOM_east, CAM_eye_CCOM_east, CAM_eye_CCOM_interior_east,
     CAM_closeup_CCOM_east_detail.

Accurate: OSM footprint, existing east window instance positions, atrium glass z-range,
backdrop bearing (~ESE, Empire ~21.7 km @ −34.5°), lettering untouched.
UNVERIFIED: exact interior plan layout, partition placement, slab extents, sill-band
depth/profile, newsroom/office XY bounds (photo-composed, not surveyed), furniture
(list-only — not placed).

4a: slabs do not duplicate exterior wall planes (inset 0.35 m from wall centroid ring).
Lettering COLLEGE OF COMMUNICATION AND MEDIA left intact.

RERUNNABLE. Saves only with --save.
  ../../tools/blender_slot.sh -b montclair_state.blend --python scripts/ccom_east_interior_20261014v.py -- --save
"""
import bpy
import math
import os
import sys
import resource
from mathutils import Vector, Matrix

SAVE = '--save' in sys.argv
ROOT = bpy.path.abspath('//')
CN = 'CCOM_interior_20261014v'
CN_EAST = 'CCOM_east_facade_20261014v'
TAG = '20261014v'

def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def mat(name, rgba, rough=0.55, spec=0.2):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = spec
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

def mat_glass(name, rgba=(0.7, 0.85, 0.95, 1), rough=0.05):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = rgba
    bsdf.inputs['Roughness'].default_value = rough
    if 'Transmission Weight' in bsdf.inputs:
        bsdf.inputs['Transmission Weight'].default_value = 0.92
    elif 'Transmission' in bsdf.inputs:
        bsdf.inputs['Transmission'].default_value = 0.92
    bsdf.inputs['Alpha'].default_value = 0.15
    if 'IOR' in bsdf.inputs:
        bsdf.inputs['IOR'].default_value = 1.45
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    m.blend_method = 'HASHED'
    return m

def link(col, ob):
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    col.objects.link(ob)

def box(name, loc, size, col, material):
    """Axis-aligned box centred at loc, size=(sx,sy,sz)."""
    mesh = bpy.data.meshes.new(name)
    sx, sy, sz = size
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    verts = [
        (-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
        (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz),
    ]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    ob.location = loc
    if material:
        mesh.materials.append(material)
    link(col, ob)
    return ob

def slab_poly(name, pts_xy, z_bot, thick, col, material):
    """Horizontal slab from XY polygon (ccw), bottom at z_bot, thickness up."""
    mesh = bpy.data.meshes.new(name)
    n = len(pts_xy)
    verts = [(p[0], p[1], z_bot) for p in pts_xy] + [(p[0], p[1], z_bot + thick) for p in pts_xy]
    faces = []
    # bottom (reversed), top
    faces.append(tuple(range(n - 1, -1, -1)))
    faces.append(tuple(range(n, 2 * n)))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    # triangulate via bmesh for ngons safety
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    if material:
        mesh.materials.append(material)
    link(col, ob)
    return ob

def clear_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    else:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    return col

def cam(name, loc, target, lens=35, clip_end=50000):
    o = bpy.data.objects.get(name)
    if o is None:
        data = bpy.data.cameras.new(name)
        o = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.data.lens = lens
    o.data.clip_end = clip_end
    # aim
    direction = (target - loc).normalized()
    # track -Z to direction, Y up
    o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return o

# ---- materials
m_slab = mat(f'CCOM_int_slab_G_{TAG}', (0.72, 0.72, 0.70, 1), rough=0.45)
m_slab_L1 = mat(f'CCOM_int_slab_L1_{TAG}', (0.78, 0.76, 0.72, 1), rough=0.5)
m_news = mat(f'CCOM_int_newsroom_floor_{TAG}', (0.62, 0.63, 0.64, 1), rough=0.4)  # raised-access grey
m_wall = mat(f'CCOM_int_wall_white_{TAG}', (0.90, 0.90, 0.88, 1), rough=0.6)
m_red = mat(f'CCOM_int_accent_red_{TAG}', (0.55, 0.05, 0.08, 1), rough=0.45)
m_frame = mat(f'CCOM_int_mullion_red_{TAG}', (0.28, 0.08, 0.08, 1), rough=0.35)
m_glass = mat_glass(f'CCOM_int_glass_clear_{TAG}', (0.75, 0.88, 0.95, 1), rough=0.02)
m_glass_ext = mat_glass(f'CCOM_east_glass_clear_{TAG}', (0.65, 0.80, 0.92, 1), rough=0.04)
m_sill = mat(f'CCOM_east_sill_stucco_{TAG}', (0.88, 0.86, 0.80, 1), rough=0.55)
m_void = mat(f'CCOM_int_void_dark_{TAG}', (0.08, 0.08, 0.09, 1), rough=0.9)  # ceiling of double-height

col_i = clear_collection(CN)
col_e = clear_collection(CN_EAST)

wo = bpy.data.objects['School of Communication and Media walls']
fh = float(wo['floor_h'])       # 4.2
wb = float(wo['win_bottom'])    # 0.9

# ---- Grade datums from east window sills (sill = floor + win_bottom)
# SE run r0 z≈135.6 → G_se = 134.7; NE run r0 z≈137.4 → G_ne = 136.5
# West atrium/entrance terrain ≈137.5
G_WEST = 137.55
G_EAST = 134.75
G_NE = 136.50
L1_EAST = G_EAST + fh          # 138.95
L1_WEST = G_WEST + fh          # 141.75
ATRIUM_TOP = 146.15            # matches existing atrium glass top
SLAB_T = 0.22

print(f'CCOM east+interior: G_WEST={G_WEST} G_EAST={G_EAST} L1_EAST={L1_EAST} atrium_top={ATRIUM_TOP}')

# ---- A) East sill bands on the two main east runs (from window instance positions)
east_wins = []
wcol = bpy.data.collections.get('CCOM_windows_modelled')
for o in (wcol.objects if wcol else []):
    n = o.matrix_world.to_3x3() @ Vector((0, 1, 0))
    if n.x > 0.5:
        east_wins.append((o.matrix_world.translation.copy(), n.normalized(), o.name))

# Cluster into SE (y < 8) and NE (y >= 8)
se = [w for w in east_wins if w[0].y < 8]
ne = [w for w in east_wins if w[0].y >= 8]

def sill_band(tag, wins, col):
    """One continuous sill under each floor row of a run."""
    if not wins:
        return 0
    # group by rounded z (floor row)
    from collections import defaultdict
    rows = defaultdict(list)
    for loc, n, nm in wins:
        rows[round(loc.z, 1)].append((loc, n))
    n_made = 0
    for z, items in rows.items():
        items.sort(key=lambda t: t[0].y)
        # run tangent ≈ average cross of n with Z
        n_avg = sum((t[1] for t in items), Vector()).normalized()
        t_dir = Vector((-n_avg.y, n_avg.x, 0)).normalized()
        # span along facade
        ys = [t[0].y for t in items]
        xs = [t[0].x for t in items]
        # place a thin box just outside the wall, under the sill
        mid = Vector((sum(xs) / len(xs), sum(ys) / len(ys), z - 0.08))
        # push outward 0.12 m
        mid = mid + n_avg * 0.12
        length = (max(ys) - min(ys)) + 2.8  # pad half window width
        # orient: local X along facade, Y out, Z up
        ob = box(f'CCOM_east_sill_{tag}_z{z}', mid, (length, 0.18, 0.10), col, m_sill)
        # rotate so local X follows t_dir
        ang = math.atan2(t_dir.y, t_dir.x)
        ob.rotation_euler = (0, 0, ang)
        n_made += 1
    return n_made

n_sill = sill_band('SE', se, col_e) + sill_band('NE', ne, col_e)
print(f'east sill bands: {n_sill} (SE wins {len(se)}, NE wins {len(ne)})')

# ---- B) Interior slabs
# West lounge/atrium slab — near entrance arch (x -18..2, y 4..22), inset from walls
lounge_xy = [(-17.5, 6.0), (-2.0, 6.0), (-2.0, 20.5), (-17.5, 20.5)]
slab_poly(f'CCOM_int_lounge_G_{TAG}', lounge_xy, G_WEST - SLAB_T, SLAB_T, col_i, m_slab)

# Double-height ceiling plane over lounge (underside of roof/upper slab)
slab_poly(f'CCOM_int_lounge_ceil_{TAG}', lounge_xy, ATRIUM_TOP - 0.15, 0.15, col_i, m_void)

# Soft white side walls for lounge shell (inset; do NOT coincide with exterior walls)
# South interior wall of lounge
box(f'CCOM_int_lounge_wall_S_{TAG}', Vector((-9.5, 6.15, (G_WEST + ATRIUM_TOP) / 2)),
    (14.5, 0.12, ATRIUM_TOP - G_WEST), col_i, m_wall)
box(f'CCOM_int_lounge_wall_N_{TAG}', Vector((-9.5, 20.35, (G_WEST + ATRIUM_TOP) / 2)),
    (14.5, 0.12, ATRIUM_TOP - G_WEST), col_i, m_wall)
# Red accent wall (from mediashift / wordcamp — east side of lounge toward newsroom)
box(f'CCOM_int_lounge_accent_red_{TAG}', Vector((-2.2, 13.25, (G_WEST + ATRIUM_TOP) / 2)),
    (0.12, 12.0, ATRIUM_TOP - G_WEST - 0.5), col_i, m_red)

# Newsroom G slab — central/east ground (photo-composed extents UNVERIFIED)
news_xy = [(-1.0, -8.0), (28.0, -8.0), (28.0, 12.0), (-1.0, 12.0)]
slab_poly(f'CCOM_int_newsroom_G_{TAG}', news_xy, G_EAST - SLAB_T, SLAB_T, col_i, m_news)

# L1 office slab — central, above newsroom north half (Joe: central offices above newsroom)
# Leaves south half of newsroom as double-height void toward east windows
office_xy = [(-1.0, 2.0), (22.0, 2.0), (22.0, 12.0), (-1.0, 12.0)]
slab_poly(f'CCOM_int_office_L1_{TAG}', office_xy, L1_EAST - SLAB_T, SLAB_T, col_i, m_slab_L1)
# L1 ceiling (simple)
slab_poly(f'CCOM_int_office_ceil_{TAG}', office_xy, L1_EAST + fh - 0.15, 0.15, col_i, m_void)

# Interior red-framed glass partition (lounge | newsroom) — simplified grid
# Plane at x≈-1.5, y 6..12, double height on lounge side / newsroom side
PART_X = -1.4
PART_Y0, PART_Y1 = 6.2, 11.8
PART_Z0, PART_Z1 = G_EAST, ATRIUM_TOP - 0.3
# glass pane
gw = PART_Y1 - PART_Y0
gh = PART_Z1 - PART_Z0
glass = box(f'CCOM_int_partition_glass_{TAG}',
            Vector((PART_X, (PART_Y0 + PART_Y1) / 2, (PART_Z0 + PART_Z1) / 2)),
            (0.02, gw, gh), col_i, m_glass)
# mullion grid (3 cols x 4 rows) — frame bars
nx, nz = 3, 4
for i in range(nx + 1):
    y = PART_Y0 + i * gw / nx
    box(f'CCOM_int_partition_mv{i}_{TAG}',
        Vector((PART_X, y, (PART_Z0 + PART_Z1) / 2)),
        (0.06, 0.06, gh), col_i, m_frame)
for j in range(nz + 1):
    z = PART_Z0 + j * gh / nz
    box(f'CCOM_int_partition_mh{j}_{TAG}',
        Vector((PART_X, (PART_Y0 + PART_Y1) / 2, z)),
        (0.06, gw, 0.06), col_i, m_frame)

# ---- Clear glass in east openings for interior see-through (siblings of instances;
#      instances keep room boxes for exterior). Place at each east win, flush to wall.
n_clear = 0
for loc, n, nm in east_wins:
    # glass just inside the wall (n points out, so -n is into building)
    p = loc - n * 0.05 + Vector((0, 0, 1.3))  # mid of 2.6 m window
    g = box(f'CCOM_east_clear_{nm}', p, (2.50, 0.02, 2.50), col_e, m_glass_ext)
    # orient: local X along facade, Y = n
    t = Vector((-n.y, n.x, 0)).normalized()
    # build basis
    g.rotation_euler = (0, 0, math.atan2(t.y, t.x))
    # also need to tip so local Z is world Z — box is axis-aligned then rotated around Z only; OK for vertical glass
    n_clear += 1
print(f'east clear glass panes: {n_clear}')

# Custom props for render helper
bpy.context.scene[f'ccom_{TAG}_east_win_count'] = len(east_wins)

# ---- C) Cameras
# Oblique from east looking west at back facade
cam('CAM_oblique_CCOM_east',
    Vector((78.0, -5.0, 162.0)),
    Vector((20.0, 0.0, 142.0)),
    lens=32)
# Eye-level east facade (outside, looking west at SE wing)
cam('CAM_eye_CCOM_east',
    Vector((48.0, -8.0, 137.5)),
    Vector((28.0, -5.0, 140.0)),
    lens=35)
# Interior looking east through SE wing windows toward NYC skyline
# Stand inside newsroom near east windows, look ESE (toward Empire bearing −34°)
cam('CAM_eye_CCOM_interior_east',
    Vector((22.0, -5.0, G_EAST + 1.55),),
    Vector((18000.0, -12000.0, 180.0),),  # toward Midtown cluster
    lens=28)
# Close-up: east window + sill band detail
cam('CAM_closeup_CCOM_east_detail',
    Vector((38.0, -10.0, 138.5)),
    Vector((27.0, -10.0, 140.0)),
    lens=50)

# Mark collections
for o in col_i.objects:
    o['ccom_pass'] = TAG
    o['UNVERIFIED'] = True
for o in col_e.objects:
    o['ccom_pass'] = TAG

print(f'collections: {CN}={len(col_i.objects)} {CN_EAST}={len(col_e.objects)} rss={rss():.0f}MB')

# Verify lettering still present
for nm in ('CCOM tower 4a lettering COLLEGE OF',
           'CCOM tower 4a lettering COMMUNICATION AND MEDIA'):
    o = bpy.data.objects.get(nm)
    print(f'lettering {"OK" if o else "MISSING"}: {nm}')

# Backdrop sanity: Empire bearing from interior cam
empire = None
deps = bpy.context.evaluated_depsgraph_get()
for ob_inst in deps.object_instances:
    obj = ob_inst.object
    if obj and obj.name == 'BD_Empire State Building':
        mw = ob_inst.matrix_world
        bb = [mw @ Vector(c) for c in obj.bound_box]
        empire = sum(bb, Vector()) / 8
        break
ic = bpy.data.objects['CAM_eye_CCOM_interior_east'].location
if empire:
    dx, dy = empire.x - ic.x, empire.y - ic.y
    bearing = math.degrees(math.atan2(dy, dx))
    dist = math.hypot(dx, dy)
    print(f'from interior cam -> Empire: dist={dist:.0f}m bearing={bearing:.1f}° (0=E)')

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
else:
    print('dry-run (pass --save to write)')
print('DONE rss', f'{rss():.0f}MB')
