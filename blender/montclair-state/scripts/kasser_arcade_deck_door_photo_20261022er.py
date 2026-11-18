"""Session er (Oct 22 ~7:45 AM ET). MAIN blend. Rebuilds the white door frames at the WEST (deck) end of Kasser's level-4 arcade to match
Joe's photo refs/joe/kasser_level4_arcade_joe_20261019.jpg (crop data/er/sign_crop.png): a fixed glass SIDELIGHT on the left (~43% of the
opening, as seen from the gallery) and a single glazed DOOR on the right with a top rail, a mid rail at ~1.04 m, a 0.23 m kick rail and a
dark lever handle by the mullion; the sidelight has a matching mid rail. ck had a symmetric double door (2 leaves, centre mullion).
Deletes the ck door-frame faces (material Arcade_door_frame_white_ck, s < 3, z > 131) from the Kasser roof (LiDAR) mesh (a rerun of the
ck/cl Kasser chain brings them back -> rerun this script after it) and adds object 'Kasser_arcade_deck_door_er' (same collection).
Opening size/glass kept from ck (1.80 x 2.30 m; photo-scaled, UNVERIFIED). Idempotent. SAVE=1 saves."""
import bpy, bmesh, os, numpy as np
from mathutils import Vector
SAVE = os.environ.get('SAVE', '0') == '1'
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def xy(s, u): return A + n * s + d * u
def su(co): p = np.array(co[:2]) - A; return float(p @ n), float(p @ d)
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; mw = ro.matrix_world
DFI = [i for i, m in enumerate(me.materials) if m and m.name.startswith('Arcade_door_frame_white_ck')]
dfm = me.materials[DFI[0]]
bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw)
dele = [f for f in bm.faces if f.material_index in DFI and su(f.calc_center_median())[0] < 3.0 and f.calc_center_median().z > 131.0]
print('er door: ck frame faces deleted', len(dele), flush=True)
bmesh.ops.delete(bm, geom=dele, context='FACES'); bm.transform(mw.inverted()); bm.to_mesh(me); bm.free(); me.update()
o = bpy.data.objects.get('Kasser_arcade_deck_door_er')
if o: m_ = o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m_)
S0 = 1.95; U0, U1 = 0.475, 2.275; Z0 = 131.40; ZH = 133.70; W = U1 - U0
SA, SB = S0 - 0.06, S0 + 0.02
lev = bpy.data.materials.get('Door_lever_dark_bronze_er') or bpy.data.materials.new('Door_lever_dark_bronze_er')
lev.use_nodes = True; b = lev.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.05, 0.045, 0.04, 1); b.inputs['Metallic'].default_value = 0.8; b.inputs['Roughness'].default_value = 0.35
bm = bmesh.new()
def box(s0, s1, u0, u1, z0, z1, mi=0):
    c = [Vector((*xy(s, u), z)) for s in (s0, s1) for u in (u0, u1) for z in (z0, z1)]
    v = [bm.verts.new(p) for p in c]
    for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        f = bm.faces.new([v[i] for i in q]); f.material_index = mi
F = 0.07; UM = U0 + 0.43 * W            # outer frame width; sidelight/door mullion (photo 105/245 px)
box(SA, SB, U0, U0 + F, Z0, ZH); box(SA, SB, U1 - F, U1, Z0, ZH); box(SA, SB, U0, U1, ZH - F, ZH)        # jambs + head
box(SA, SB, UM - 0.05, UM + 0.05, Z0, ZH - F)                                                             # mullion
box(SA, SB, U0 + F, UM - 0.05, Z0, Z0 + 0.10)                                                            # sidelight sill rail
box(SA, SB, U0 + F, UM - 0.05, Z0 + 0.96, Z0 + 1.12)                                                     # sidelight mid rail (photo)
DA, DB = SA - 0.01, SB + 0.005                                                                           # door leaf a touch proud of the frame
box(DA, DB, UM + 0.05, UM + 0.15, Z0, ZH - F); box(DA, DB, U1 - F - 0.10, U1 - F, Z0, ZH - F)           # door stiles
box(DA, DB, UM + 0.15, U1 - F - 0.10, ZH - F - 0.20, ZH - F)                                              # top rail
box(DA, DB, UM + 0.15, U1 - F - 0.10, Z0 + 0.96, Z0 + 1.12)                                              # mid rail ~1.04 m
box(DA, DB, UM + 0.15, U1 - F - 0.10, Z0, Z0 + 0.23)                                                     # kick rail
uh = UM + 0.10
box(DB, DB + 0.012, uh - 0.035, uh + 0.035, Z0 + 0.98, Z0 + 1.10, 1)                                    # rose
box(DB + 0.012, DB + 0.06, uh + 0.0, uh + 0.15, Z0 + 1.03, Z0 + 1.055, 1)                                # lever (gallery side)
dm = bpy.data.meshes.new('Kasser_arcade_deck_door_er'); bm.to_mesh(dm); bm.free()
dm.materials.append(dfm); dm.materials.append(lev)
do = bpy.data.objects.new('Kasser_arcade_deck_door_er', dm); ro.users_collection[0].objects.link(do)
do['er'] = 'deck door per Joe photo 2026-10-19: sidelight + single door, rails, lever (er); photo-scaled, UNVERIFIED'
print('er door object faces', len(dm.polygons), 'mullion u %.3f' % UM, flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('er door main: SAVED', flush=True)
