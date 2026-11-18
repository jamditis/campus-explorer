"""Self-review: rebuild UF arches with closed apex + more segs; fix Normal Ave eye cam."""
import bpy, bmesh, os, json, math
from mathutils import Vector, Matrix

SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UF_day9_leftover_polish_UNVERIFIED'
TAG = 'uf_obj'
UF_ARCH = 'UF_Cole_east_arched_GF_UNVERIFIED'
GRADE = 131.61

def add_box(bm, cx, cy, z0, z1, hx, hy, rot, mi):
    R = Matrix.Rotation(rot, 4, 'Z')
    vs = []
    for z in (z0, z1):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(Vector((cx, cy, 0)) + (R @ Vector((sx * hx, sy * hy, 0))).to_3d() + Vector((0, 0, z))))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f]).material_index = mi

def add_arch_window_hi(bm, cx, cy, z0, z1, half_w, rot, mi_fr, mi_gl, mi_st, segs=28):
    R = Matrix.Rotation(rot, 4, 'Z')
    h_rect = (z1 - z0) * 0.58
    z_spring = z0 + h_rect
    r = half_w * 0.98
    g_off = 0.28
    gx = (R @ Vector((0, g_off, 0))).x
    gy = (R @ Vector((0, g_off, 0))).y
    # glass rect
    add_box(bm, cx + gx, cy + gy, z0 + 0.04, z_spring, half_w * 0.86, 0.035, rot, mi_gl)
    for i in range(segs):
        t0 = i / segs; t1 = (i + 1) / segs
        h0 = t0 * r; h1 = t1 * r
        hm = 0.5 * (h0 + h1)
        hw = math.sqrt(max(1e-6, r * r - hm * hm))
        add_box(bm, cx + gx, cy + gy, z_spring + h0, z_spring + h1 + 0.003, hw * 0.90, 0.032, rot, mi_gl)
    # frame jambs/sill/spring
    fx = (R @ Vector((0, 0.05, 0))).x
    fy = (R @ Vector((0, 0.05, 0))).y
    jamb = 0.055
    add_box(bm, cx + fx + (R @ Vector((-half_w + jamb * 0.5, 0, 0))).x,
                 cy + fy + (R @ Vector((-half_w + jamb * 0.5, 0, 0))).y,
                 z0, z_spring + r * 0.05, jamb * 0.5, 0.045, rot, mi_fr)
    add_box(bm, cx + fx + (R @ Vector((half_w - jamb * 0.5, 0, 0))).x,
                 cy + fy + (R @ Vector((half_w - jamb * 0.5, 0, 0))).y,
                 z0, z_spring + r * 0.05, jamb * 0.5, 0.045, rot, mi_fr)
    add_box(bm, cx + fx, cy + fy, z0, z0 + 0.06, half_w * 0.94, 0.05, rot, mi_fr)
    add_box(bm, cx + fx, cy + fy, z_spring - 0.035, z_spring + 0.035, half_w * 0.90, 0.045, rot, mi_fr)
    # arch rim — follow outer radius with overlapping boxes + APEX CAP
    for i in range(segs):
        t0 = i / segs; t1 = (i + 1) / segs
        ang0 = math.pi * (0.5 - t0)  # from left spring to right via top? better param by x
        # use x-parameterization: x from -r to +r
        x0 = -r + 2 * r * t0
        x1 = -r + 2 * r * t1
        xm = 0.5 * (x0 + x1)
        # outer y on circle: z = z_spring + sqrt(r^2 - x^2)
        def zz(x):
            return z_spring + math.sqrt(max(1e-6, r * r - x * x))
        z_lo = min(zz(x0), zz(x1)) - 0.01
        z_hi = max(zz(x0), zz(x1)) + 0.02
        # left and right rim pieces at |x| near outer
        for sign in (-1.0, 1.0):
            # only place rim near the outer edge of this slice
            pass
        # place a rim block at xm on the circle, thickness inward
        u = xm
        # skip near-zero width at apex handled by cap
        hw_slice = abs(x1 - x0) * 0.55 + 0.02
        add_box(bm,
                cx + fx + (R @ Vector((u, 0, 0))).x,
                cy + fy + (R @ Vector((u, 0, 0))).y,
                z_lo, z_hi, hw_slice, 0.045, rot, mi_fr)
    # APEX CAP — closes the crown gap
    add_box(bm, cx + fx, cy + fy, z_spring + r - 0.04, z_spring + r + 0.05, 0.12, 0.05, rot, mi_fr)
    # center mullion
    add_box(bm, cx + gx * 0.55, cy + gy * 0.55, z0 + 0.08, z_spring + r * 0.72,
            0.02, 0.028, rot, mi_fr)
    # cream lip
    sx = (R @ Vector((0, -0.01, 0))).x
    sy = (R @ Vector((0, -0.01, 0))).y
    add_box(bm, cx + sx, cy + sy, z0 - 0.04, z0 + 0.015, half_w + 0.07, 0.035, rot, mi_st)
    for sign in (-1.0, 1.0):
        u = sign * (half_w + 0.045)
        add_box(bm,
                cx + sx + (R @ Vector((u, 0, 0))).x,
                cy + sy + (R @ Vector((u, 0, 0))).y,
                z0, z_spring + r * 0.15, 0.035, 0.03, rot, mi_st)

# rebuild mesh in place
win = bpy.data.objects.get(UF_ARCH)
if not win:
    raise SystemExit('missing UF arch')
M_fr = win.data.materials[0]
M_gl = win.data.materials[1]
M_st = win.data.materials[2]
# darken glass again
b = M_gl.node_tree.nodes.get('Principled BSDF')
if b:
    b.inputs['Base Color'].default_value = (0.015, 0.02, 0.025, 1)
    b.inputs['Roughness'].default_value = 0.1
    if 'Transmission Weight' in b.inputs:
        b.inputs['Transmission Weight'].default_value = 0.35  # less wash-out

ring = json.load(open(D + 'north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
P = [Vector((x, y)) for x, y in ring]
if P[0] == P[-1]:
    P = P[:-1]
area = sum(P[i].x * P[(i + 1) % len(P)].y - P[(i + 1) % len(P)].x * P[i].y for i in range(len(P))) / 2
EAST_EDGES = {18, 19, 20}
bm = bmesh.new()
narch = 0
arch_half_w = 0.78
arch_sill = GRADE + 1.15
arch_top = GRADE + 4.10
for i in range(len(P)):
    a, b = P[i], P[(i + 1) % len(P)]
    d = b - a
    L = d.length
    if L < 5.0: continue
    t = d / L
    n = Vector((t.y, -t.x)) if area > 0 else Vector((-t.y, t.x))
    if n.x <= 0.55: continue
    if i not in EAST_EDGES and L < 12: continue
    edge_rot = math.atan2(t.y, t.x)
    margin = 1.6
    usable = L - 2 * margin
    if usable < 3.4: continue
    nb = {18: 3, 19: 3, 20: 2}.get(i, max(1, int(round(usable / 3.4))))
    for k in range(nb):
        u = margin + (k + 0.5) * (usable / nb)
        cx = a.x + t.x * u + n.x * 0.10
        cy = a.y + t.y * u + n.y * 0.10
        add_arch_window_hi(bm, cx, cy, arch_sill, arch_top, arch_half_w, edge_rot, 0, 1, 2, segs=28)
        narch += 1
old = win.data
me = bpy.data.meshes.new(UF_ARCH + '_v2')
bm.to_mesh(me); bm.free()
me.materials.append(M_fr); me.materials.append(M_gl); me.materials.append(M_st)
win.data = me
if old.users == 0:
    bpy.data.meshes.remove(old)
print('UF rebuilt arches', narch, 'segs=28 apex-cap')

# Fix Normal Ave eye: stand on north sidewalk looking WSW along asphalt
def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
cam = bpy.data.objects.get('UF_CAM_eye_NormalAve_from_N')
if cam:
    # reuse UA cam pose if present
    ua = bpy.data.objects.get('UA_CAM_eye_NormalAve_from_N')
    if ua:
        cam.location = ua.location.copy()
        cam.rotation_euler = ua.rotation_euler.copy()
        cam.data.lens = ua.data.lens
        print('UF eye copied from UA_CAM_eye_NormalAve_from_N', tuple(round(x,2) for x in cam.location))
    else:
        cam.location = Vector((-120.0, -240.0, 121.0))
        aim(cam, (-200.0, -290.0, 117.0))
        cam.data.lens = 32
        print('UF eye manual', tuple(round(x,2) for x in cam.location))

# Soften fade more aggressively on material
m = bpy.data.materials.get('UF_asphalt_softfade_UNVERIFIED')
if m and m.node_tree:
    for n in m.node_tree.nodes:
        if n.type == 'MATH' and n.operation == 'POWER':
            # tip clearer sooner
            if n.inputs[1].default_value >= 1.0:
                n.inputs[1].default_value = 1.2
            else:
                n.inputs[1].default_value = 0.7
    print('UF softfade powers nudged')

if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
print('DONE')
