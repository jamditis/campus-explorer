"""Session er (Oct 22 ~7:40 AM ET). MAIN blend. Adds the permanent 'RED HAWK DECK' wall lettering above the glass door at the
WEST (deck) end of Kasser's level-4 open arcade, per Joe's photo refs/joe/kasser_level4_arcade_joe_20261019.jpg (crop data/er/sign_crop.png).
ck built that end wall with NO lettering under the old 2026-10-13 rule; Joe corrected it Oct 20 (permanent photo-backed signs go in).
Photo-scaled (door head = 2.30 m model): cap height ~0.16 m, text width ~1.44 m, baseline ~0.42 m above the door head, centre ~0.10 m
toward +u of the door centre, black flat letters on the white end wall; plus the thin horizontal reveal line ~1.02 m above the door head.
Separate object 'Kasser_arcade_RHD_sign_er' (+ 'Kasser_arcade_endwall_reveal_er') in the Kasser roof object's collection (north links it).
Placement is measured from the ck door-frame verts in the roof mesh (material Arcade_door_frame_white_ck). Idempotent. SAVE=1 saves; REVERT=1 removes."""
import bpy, os, numpy as np
from mathutils import Vector, Matrix
SAVE = os.environ.get('SAVE', '0') == '1'
for nm in ('Kasser_arcade_RHD_sign_er', 'Kasser_arcade_endwall_reveal_er'):
    o = bpy.data.objects.get(nm)
    if o: me = o.data; bpy.data.objects.remove(o); (bpy.data.meshes.remove(me) if me and me.users == 0 else None)
if os.environ.get('REVERT') == '1':
    if SAVE: bpy.ops.wm.save_mainfile(); print('er REVERTED + SAVED', flush=True)
    raise SystemExit
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; mw = ro.matrix_world; me = ro.data
mi = [i for i, m in enumerate(me.materials) if m and m.name.startswith('Arcade_door_frame_white_ck')]
pts = []
for p in me.polygons:
    if p.material_index in mi:
        for vi in p.vertices: pts.append(mw @ me.vertices[vi].co)
P = np.array([(*(np.array(v[:2]) - A) @ np.array([n, d]).T, v[2]) for v in pts])
s_face = P[:, 0].max(); u0, u1 = P[:, 1].min(), P[:, 1].max(); z0, zh = P[:, 2].min(), P[:, 2].max()
# the frames at the west end only (s < 3)
w = (P[:, 0] < 3.0) & (P[:, 2] > 131.0); s_face = P[w, 0].max(); u0, u1 = P[w, 1].min(), P[w, 1].max(); z0, zh = P[w, 2].min(), P[w, 2].max()
print('er door frame s_face %.3f u %.3f-%.3f z %.3f-%.3f' % (s_face, u0, u1, z0, zh), flush=True)
WALL_S = s_face - 0.02          # end-wall gallery face = ck S0 (frames stand 2 cm proud of it)
DOORH = zh - z0; k = DOORH / 2.30
CAP = 0.163 * k; WIDTH = 1.44 * k; BASE = zh + 0.42 * k; UC = (u0 + u1) / 2 + 0.10 * k
mat = bpy.data.materials.get('Sign_letters_black_matte_er') or bpy.data.materials.new('Sign_letters_black_matte_er')
mat.use_nodes = True; bs = mat.node_tree.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = (0.018, 0.018, 0.02, 1); bs.inputs['Roughness'].default_value = 0.55
font = bpy.data.fonts.load('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf', check_existing=True)
cu = bpy.data.curves.new('er_sign_txt', 'FONT'); cu.body = 'RED HAWK DECK'; cu.font = font; cu.size = 1.0
cu.align_x = 'CENTER'; cu.space_character = 0.92; cu.extrude = 0.0025; cu.resolution_u = 6
t = bpy.data.objects.new('er_tmp_txt', cu); bpy.context.scene.collection.objects.link(t)
dg = bpy.context.evaluated_depsgraph_get(); tm = bpy.data.meshes.new_from_object(t.evaluated_get(dg))
bpy.data.objects.remove(t); bpy.data.curves.remove(cu)
V = np.array([v.co[:] for v in tm.vertices]); w0, w1 = V[:, 0].min(), V[:, 0].max(); hz = V[:, 1].max()   # cap height ~ max y (no descenders in caps)
sc = WIDTH / (w1 - w0); SY = min(1.30, max(1.0, CAP / (hz * sc))); print('er text raw width %.3f cap %.3f -> scale %.3f, cap %.3f m (photo %.3f)' % (w1 - w0, hz, sc, hz * sc, CAP), flush=True)
# local text: x along reading, y up, z out of wall (extrude +-0.0025 about 0) -> world: x->+d, y->+z, z->+n
ex = Vector((d[0], d[1], 0)); ey = Vector((0, 0, 1)); ez = Vector((n[0], n[1], 0))
o3 = xy(WALL_S + 0.006, UC); org = Vector((o3[0], o3[1], BASE))
M = Matrix(((ex.x, ey.x, ez.x, org.x), (ex.y, ey.y, ez.y, org.y), (ex.z, ey.z, ez.z, org.z), (0, 0, 0, 1))) @ Matrix.Scale(sc, 4) @ Matrix.Diagonal((1, SY, 1, 1)) @ Matrix.Translation((-(w0 + w1) / 2, 0, 0))
tm.transform(M); tm.materials.clear(); tm.materials.append(mat); tm.name = 'Kasser_arcade_RHD_sign_er'
so = bpy.data.objects.new('Kasser_arcade_RHD_sign_er', tm)
col = ro.users_collection[0]; col.objects.link(so)
# reveal line across the end wall (photo: thin dark horizontal joint ~1.02 m above the door head)
rmat = bpy.data.materials.get('Reveal_joint_grey_er') or bpy.data.materials.new('Reveal_joint_grey_er')
rmat.use_nodes = True; rb = rmat.node_tree.nodes['Principled BSDF']; rb.inputs['Base Color'].default_value = (0.30, 0.30, 0.29, 1); rb.inputs['Roughness'].default_value = 0.8
zr = zh + 1.02 * k; UL0, UL1 = 0.30 + 0.02, 2.45 - 0.01
q = [xy(WALL_S + 0.0015, UL0), xy(WALL_S + 0.0015, UL1)]
rm_ = bpy.data.meshes.new('Kasser_arcade_endwall_reveal_er')
rm_.from_pydata([(q[0][0], q[0][1], zr - 0.006), (q[1][0], q[1][1], zr - 0.006), (q[1][0], q[1][1], zr + 0.006), (q[0][0], q[0][1], zr + 0.006)], [], [(0, 1, 2, 3)])
rm_.materials.append(rmat); r_o = bpy.data.objects.new('Kasser_arcade_endwall_reveal_er', rm_); col.objects.link(r_o)
for o in (so, r_o): o['er'] = 'RED HAWK DECK end-wall lettering/reveal per Joe photo 2026-10-19 (er); photo-scaled, UNVERIFIED size'
print('er sign verts', len(tm.vertices), 'ystretch %.2f' % SY, 'base z %.3f cap top %.3f u centre %.3f wall s %.3f reveal z %.3f' % (BASE, BASE + hz * sc * SY, UC, WALL_S, zr), 'collection', col.name, flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('er main: SAVED', flush=True)
