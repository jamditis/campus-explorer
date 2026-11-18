"""2026-10-15 ~7:30 AM ET (tag 20261015al). CCOM east lounge photo-match pass against refs/ccom_x/02_20241009_SCM_study_spot.jpg
(CCOM X post, 2024-10-09): the window sits on a low sill wall with a wood-tone ledge and dark base; mullions are dark maroon-brown,
not bright red; chairs are blue high-back swivel lounge chairs on chrome 4-star bases; tables are small round white pedestal tables;
floor is glossy pale-grey terrazzo/VCT. Replaces the jf block chairs + square tables (hidden, not deleted). Sizes UNVERIFIED (photo eye-scale).
Run: ../tools/blender_slot.sh -b montclair_state.blend --python scripts/ccom_lounge_photo_20261015al.py -- --save"""
import bpy, bmesh, sys, math, random
from mathutils import Vector, Matrix
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = '20261015al'; random.seed(15)
A = Vector((23.45, -24.78)); B = Vector((25.0, -18.76))     # lounge glass line (from CCOM_lounge_east_glass_20261014jf bbox + jambs)
T = (B - A).normalized(); N = Vector((T.y, -T.x))           # N points outward (east), interior is -N
L = (B - A).length; FLOOR = 134.85
col = bpy.data.collections.get('CCOM_lounge_photo_' + TAG) or bpy.data.collections.new('CCOM_lounge_photo_' + TAG)
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in list(col.objects): bpy.data.objects.remove(o)

def mat(name, rgb, rough, metal=0.0, spec=0.5):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*rgb, 1)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    b.inputs['Specular IOR Level'].default_value = spec; return m
M_sill = mat('CCOM_lounge_sill_wall_' + TAG, (0.62, 0.63, 0.64), 0.6)
M_wood = mat('CCOM_lounge_sill_wood_' + TAG, (0.30, 0.16, 0.07), 0.38)
M_base = mat('CCOM_lounge_baseboard_' + TAG, (0.05, 0.05, 0.055), 0.5)
M_blue = mat('CCOM_lounge_swivel_blue_' + TAG, (0.010, 0.13, 0.55), 0.62, spec=0.3)
M_chrome = bpy.data.materials.get('CCOM_lounge_chrome_20261014z') or mat('CCOM_lounge_chrome_' + TAG, (0.8, 0.8, 0.82), 0.12, 1.0)
M_top = bpy.data.materials.get('CCOM_lounge_table_20261014jf')

def box(name, cx, cy, cz, sx, sy, sz, m, yaw=0.0, bevel=0.0, rotx=0.0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((sx, sy, sz, 1)))
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); col.objects.link(o)
    o.matrix_world = Matrix.Translation((cx, cy, cz)) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Rotation(rotx, 4, 'X')
    me.materials.append(m)
    if bevel > 0:
        md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 3; md.limit_method = 'NONE'
        for p in me.polygons: p.use_smooth = True
    return o

def cyl(name, cx, cy, z0, z1, r, m, verts=20):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=z1 - z0)
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); col.objects.link(o)
    o.location = (cx, cy, (z0 + z1) / 2); me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    return o

def along(t, s):   # wall coords -> world xy (s<0 = inside)
    return A + T * t + N * s
yaw_wall = math.atan2(T.y, T.x)
# 1. sill wall + wood ledge + dark base (inside) and a matching dark spandrel band outside
SILL_H = 0.48; c = along(L / 2, -0.17)
box('CCOM_lounge_sill_wall_' + TAG, c.x, c.y, FLOOR + SILL_H / 2, L - 0.08, 0.30, SILL_H, M_sill, yaw_wall)
c = along(L / 2, -0.19); box('CCOM_lounge_sill_ledge_' + TAG, c.x, c.y, FLOOR + SILL_H + 0.018, L - 0.04, 0.36, 0.036, M_wood, yaw_wall, bevel=0.006)
c = along(L / 2, -0.33); box('CCOM_lounge_sill_base_' + TAG, c.x, c.y, FLOOR + 0.05, L - 0.08, 0.02, 0.10, M_base, yaw_wall)
frame = None
for o in bpy.data.objects:   # lounge mullions: anything in the lounge/glazing collections near the glass line that isn't glass/pier
    if o.type != 'MESH' or o.hide_render: continue
    if not any(cc.name in ('CCOM_lounge_east_20261014jf', 'CCOM_east_glazing_20261014jf') for cc in o.users_collection): continue
    p = o.matrix_world.to_translation() if o.data.vertices and o.location.length > 1 else sum((o.matrix_world @ Vector(v) for v in o.bound_box), Vector()) / 8
    s = (p.xy - A).dot(N); t = (p.xy - A).dot(T)
    if abs(s) < 0.4 and -0.3 < t < L + 0.3 and o.material_slots and o.material_slots[0].material:
        mn = o.material_slots[0].material.name
        if 'glass' in mn or 'terrazzo' in mn or 'wall' in mn: continue
        frame = frame or o.material_slots[0].material
        print('FRAME obj', o.name, mn, flush=True)
if frame is not None:
    b = frame.node_tree.nodes.get('Principled BSDF')
    print('FRAME mat', frame.name, 'old', tuple(round(x, 3) for x in b.inputs['Base Color'].default_value), flush=True)
    b.inputs['Base Color'].default_value = (0.105, 0.028, 0.022, 1); b.inputs['Roughness'].default_value = 0.42
c = along(L / 2, 0.025); box('CCOM_lounge_spandrel_ext_' + TAG, c.x, c.y, FLOOR + (SILL_H + 0.04) / 2, L - 0.08, 0.02, SILL_H + 0.04, frame or M_base, yaw_wall)
# 2. hide block chairs + square tables, rebuild as swivel lounge chairs + round pedestal tables
seats, tables = [], []
for o in bpy.data.collections['CCOM_lounge_east_20261014jf'].objects:
    n = o.name
    if '_chair' in n or '_table' in n or '_tleg' in n:
        o.hide_render = True; o.hide_viewport = True
        ctr = sum((o.matrix_world @ Vector(v) for v in o.bound_box), Vector()) / 8
        if n.endswith('_seat_20261014jf'): seats.append((n, ctr))
        if '_table' in n: tables.append(ctr)
backs = {o.name.replace('_back_', '_seat_'): sum((o.matrix_world @ Vector(v) for v in o.bound_box), Vector()) / 8
         for o in bpy.data.collections['CCOM_lounge_east_20261014jf'].objects if '_back_' in o.name}
def shell_back(name, x, y, yaw):
    """Tapered high back that flares to pointed shoulders (photo: Catifa-style lounge shell; UNVERIFIED model)."""
    out = [(-0.21, 0.0), (0.21, 0.0), (0.27, 0.30), (0.33, 0.52), (0.0, 0.57), (-0.33, 0.52), (-0.27, 0.30)]
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vf = [bm.verts.new((u, 0.0, v)) for u, v in out]; vb = [bm.verts.new((u, -0.07, v)) for u, v in out]
    bm.faces.new(vf); bm.faces.new(list(reversed(vb)))
    n = len(out)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((vf[i], vb[i], vb[j], vf[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); me.materials.append(M_blue)
    o.matrix_world = Matrix.Translation((x, y, FLOOR + 0.46)) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Translation((0, -0.25, 0)) @ Matrix.Rotation(math.radians(-14), 4, 'X')
    md = o.modifiers.new('bev', 'BEVEL'); md.width = 0.03; md.segments = 3; md.limit_method = 'NONE'
    for p in me.polygons: p.use_smooth = True
    return o
def chair(i, x, y, yaw):
    pre = 'CCOM_lounge_swivel%02d_' % i
    R = Matrix.Rotation(yaw, 4, 'Z')
    def P(lx, ly): v = R @ Vector((lx, ly, 0)); return x + v.x, y + v.y
    cx, cy = P(0, 0.02); box(pre + 'seat_' + TAG, cx, cy, FLOOR + 0.43, 0.56, 0.54, 0.10, M_blue, yaw, bevel=0.045)
    shell_back(pre + 'back_' + TAG, x, y, yaw)
    for sx in (-1, 1):
        cx, cy = P(sx * 0.27, -0.06); box(pre + 'wing%+d_' % sx + TAG, cx, cy, FLOOR + 0.55, 0.06, 0.34, 0.20, M_blue, yaw, bevel=0.025, rotx=math.radians(-10))
    cyl(pre + 'stem_' + TAG, x, y, FLOOR + 0.06, FLOOR + 0.38, 0.028, M_chrome)
    for k in range(4):
        a = yaw + math.pi / 4 + k * math.pi / 2; d = Vector((math.cos(a), math.sin(a)))
        c2 = Vector((x, y)) + d * 0.19
        box(pre + 'star%d_' % k + TAG, c2.x, c2.y, FLOOR + 0.045, 0.38, 0.035, 0.022, M_chrome, a, bevel=0.008)
        f = Vector((x, y)) + d * 0.37; cyl(pre + 'foot%d_' % k + TAG, f.x, f.y, FLOOR, FLOOR + 0.02, 0.022, M_chrome, 10)
for i, (n, ctr) in enumerate(sorted(seats)):
    bk = backs.get(n); d = (ctr.xy - bk.xy) if bk else -N   # face away from the old back
    yaw = math.atan2(d.y, d.x) - math.pi / 2 + math.radians(random.uniform(-25, 25))
    chair(i, ctr.x, ctr.y, yaw)
for j, ctr in enumerate(tables):
    cyl('CCOM_lounge_rtable%d_top_' % j + TAG, ctr.x, ctr.y, FLOOR + 0.60, FLOOR + 0.625, 0.36, M_top, 32)
    cyl('CCOM_lounge_rtable%d_post_' % j + TAG, ctr.x, ctr.y, FLOOR + 0.03, FLOOR + 0.60, 0.03, M_chrome)
    cyl('CCOM_lounge_rtable%d_base_' % j + TAG, ctr.x, ctr.y, FLOOR, FLOOR + 0.03, 0.24, M_chrome, 32)
# 3. floor: glossier pale grey (photo shows window reflections in the floor)
fm = bpy.data.materials.get('CCOM_lounge_terrazzo_20261014z')
if fm:
    b = fm.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.56, 0.58, 0.60, 1); b.inputs['Roughness'].default_value = 0.14
print('LOUNGE', TAG, 'chairs', len(seats), 'tables', len(tables), 'frame', frame.name if frame else None, flush=True)
if '--save' in ARGV:
    bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath, flush=True)
