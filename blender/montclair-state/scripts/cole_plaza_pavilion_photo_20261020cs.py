"""Session cs (Oct 20 ~5:35 AM ET). MAIN blend. REPLACES cr's cole_plaza_pavilion_photo_20261020cr.py (same idempotent rebuild; run this one,
not cr's). cs changes: (1) br's 0.15 m platform dropped: Commons 13252662863 shows the pavilion piers standing straight on the plaza
paving with their own square bases, so the plinth top now sits 3 cm under the COLE_plaza_deck_bs top (ray cast at the footprint; MEASURED
from the deck) and piers + bases start 5 cm under the deck top; springing/crown/eave/apex unchanged. (2) Long wall: Commons 12550692334
pier:opening ~0.28 and pier:wall-height ~0.24 (snow hides ~0.2-0.4 m) -> pier ~0.85 m, which fits 6 arches (span ~3.05) better than 5
(pier ~1.02, span ~3.6): keep 6 arches, piers 0.95 -> 0.85 (UNVERIFIED). (3) Long-wall frieze: the photo's band under the coping carries a
row of small dark rectangular recesses; modelled as shallow darker inset tiles every ~0.32 m on both faces (UNVERIFIED rhythm).
--- cr docstring follows ---
Session cr (Oct 20 ~4:40 AM ET). MAIN blend. Rebuilds the mesh of 'Cole Hall plaza pavilion (...) br' (the free-standing arched pergola
with the red-tile hip roof on the amphitheater plaza SE of Kasser) to match Commons File:Montclair State University (13252662863).jpg
(CC BY-SA 2.0, 2014) seen from the cr camera match. Idempotent (rebuilds the whole mesh). SAVE=1 saves. If br2
(cole_hall_west_portico_20261016br2.py) is ever re-run, run this after it.
Kept from br (MEASURED): LiDAR 5 x 5 m footprint at (-180, -72), rotation with Cole Hall, ground 130.25, eave 134.35, apex 135.79.
Changed (photo-scaled, UNVERIFIED): br's stepped 24-slice arches (they read as cusped/Moorish) -> smooth semicircular arches (32 segments,
real intrados); piers 0.75 -> 1.00 m (photo pier:side ~0.2); arch r 1.50 m springing 1.85 m above the plinth so ~0.6 m of wall shows above
the crown as in the photo; walls 0.60 m thick with their outer face on the footprint line (br centred them on it, so the cornice band sat
inside the wall face); square pier bases 0.60 m tall projecting 0.08 m (photo); cornice band + hip roof + ceiling as br."""
import bpy, bmesh, math, os
from mathutils import Vector, Matrix
SAVE = os.environ.get('SAVE', '0') == '1'
pav = [o for o in bpy.data.objects if o.name.startswith('Cole Hall plaza pavilion')][0]
rot = math.atan2(-104.247 + 98.217, -126.347 + 151.955)
cx, cy = -180.0, -72.0; zgp = 130.25; h = 2.5; ZEp = 134.35; ZA = 135.79
PW, TH, R, ZS = 1.00, 0.60, 1.50, zgp + 0.15 + 1.85
from mathutils.bvhtree import BVHTree
_dk = bpy.data.objects['COLE_plaza_deck_bs']; _b = bmesh.new(); _b.from_mesh(_dk.data); _b.transform(_dk.matrix_world); _dbv = BVHTree.FromBMesh(_b); _b.free()
_zs = []
for _dx in (-3.2, 0.0, 3.2):
    for _dy in (-3.2, 0.0, 3.2):
        _h = _dbv.ray_cast(Vector((cx + _dx, cy + _dy, 200)), Vector((0, 0, -1)))
        if _h[0] is not None: _zs.append(_h[0].z)
ZDK = float(min(_zs)) if _zs else zgp                                                  # lowest paving under the footprint
print('cs deck samples', [round(z, 3) for z in _zs], flush=True)
def dz(x, y):
    _h = _dbv.ray_cast(Vector((x, y, 200)), Vector((0, 0, -1))); return _h[0].z if _h[0] is not None else ZDK
print('cs deck top at the pavilion: n %d median %.3f min %.3f max %.3f' % (len(_zs), ZDK, min(_zs) if _zs else -1, max(_zs) if _zs else -1), flush=True)
bm = bmesh.new(); Rm = Matrix.Rotation(rot, 4, 'Z')
def add_box(cx_, cy_, z0, z1, hx, hy, rot_, mi):
    Rr = Matrix.Rotation(rot_, 4, 'Z')
    vs = [bm.verts.new(Vector((cx_, cy_, 0)) + (Rr @ Vector((sx * hx, sy * hy, 0))).to_3d() + Vector((0, 0, z))) for z in (z0, z1) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([vs[i] for i in f]).material_index = mi
def F(*vs, mi=0):
    bm.faces.new([bm.verts.new(v) for v in vs]).material_index = mi
def sbox(w0, t, nn, a0, a1, o0, o1, z0, z1, mi=0):   # box in side coords: a along t, o along outward normal
    P = lambda a, o, z: Vector((w0.x + t.x * a + nn.x * o, w0.y + t.y * a + nn.y * o, z))
    c = [P(a, o, z) for z in (z0, z1) for o in (o0, o1) for a in (a0, a1)]
    for ix in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)): F(*[c[i] for i in ix], mi=mi)
add_box(cx, cy, zgp - 2.0, ZDK - 0.03, h + 0.25, h + 0.25, rot, 0)                     # plinth: top 3 cm under the deck (cs; br's platform dropped)
ZT = ZEp - 0.22; corners = [(-h, -h), (h, -h), (h, h), (-h, h)]; N = 32
for s in range(4):
    c0 = Vector(corners[s]); c1 = Vector(corners[(s + 1) % 4])
    w0 = Vector((cx, cy)) + (Rm @ c0.to_3d()).to_2d(); w1 = Vector((cx, cy)) + (Rm @ c1.to_3d()).to_2d()
    t = w1 - w0; L = t.length; t /= L; nn = Vector((t.y, -t.x))                         # CCW -> outward normal
    ev = s % 2 == 0
    a_in0 = 0.0 if ev else TH; a_in1 = L if ev else L - TH                               # even sides own the corners
    zb = ZDK - 0.05                                                                       # cs: piers start under the paving
    sbox(w0, t, nn, a_in0, PW, -TH, 0.0, zb, ZT); sbox(w0, t, nn, L - PW, a_in1, -TH, 0.0, zb, ZT)    # piers
    _pa = w0 + t * (PW / 2) - nn * (TH / 2); _pb = w0 + t * (L - PW / 2) - nn * (TH / 2)       # cs: per-pier bases 0.55 m above the LOCAL paving
    _za = dz(_pa.x, _pa.y) + 0.55; _zb2 = dz(_pb.x, _pb.y) + 0.55
    sbox(w0, t, nn, (-0.08 if ev else TH), PW + 0.08, -TH - 0.08, 0.08, zb, _za)               # pier bases
    sbox(w0, t, nn, L - PW - 0.08, (L + 0.08 if ev else L - TH), -TH - 0.08, 0.08, zb, _zb2)
    ac = L / 2
    P = lambda a, o, z: Vector((w0.x + t.x * a + nn.x * o, w0.y + t.y * a + nn.y * o, z))
    arc = [(ac - R * math.cos(math.pi * i / N), ZS + R * math.sin(math.pi * i / N)) for i in range(N + 1)]
    for i in range(N):
        (a0, z0), (a1, z1) = arc[i], arc[i + 1]
        F(P(a0, 0, z0), P(a1, 0, z1), P(a1, 0, ZT), P(a0, 0, ZT))                        # outer spandrel strip
        F(P(a0, -TH, ZT), P(a1, -TH, ZT), P(a1, -TH, z1), P(a0, -TH, z0))                # inner spandrel strip
        F(P(a1, 0, z1), P(a0, 0, z0), P(a0, -TH, z0), P(a1, -TH, z1))                    # intrados
    F(P(PW, 0, ZS), P(PW, 0, zb), P(PW, -TH, zb), P(PW, -TH, ZS))                        # pier inner jambs are the pier box faces; nothing else
    F(P(PW, 0, ZT), P(L - PW, 0, ZT), P(L - PW, -TH, ZT), P(PW, -TH, ZT))                # top of the spandrel (under the cornice)
add_box(cx, cy, ZEp - 0.32, ZEp - 0.22, h - TH, h - TH, rot, 3)                          # ceiling slab inside the walls
add_box(cx, cy, ZEp - 0.22, ZEp, h + 0.10, h + 0.10, rot, 0)                             # cornice band (0.10 proud of the walls)
b = [bm.verts.new(Vector((cx, cy, ZEp)) + (Rm @ Vector((sx * (h + 0.55), sy * (h + 0.55), 0))).to_3d()) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
a = bm.verts.new((cx, cy, ZA))
for i in range(4): bm.faces.new([b[i], b[(i + 1) % 4], a]).material_index = 1
bm.faces.new(b[::-1]).material_index = 3
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
bm.transform(pav.matrix_world.inverted()); bm.to_mesh(pav.data); bm.free(); pav.data.update()
for p in pav.data.polygons: p.use_smooth = False
pav['cs_platform'] = 'cs: br platform dropped, plinth top %.3f (deck %.3f - 0.03)' % (ZDK - 0.03, ZDK)
pav['cr_photo_rebuild'] = 'cr: semicircular arches r %.2f spring %.2f, piers %.2f, walls %.2f outer on the footprint, pier bases; Commons 13252662863' % (R, ZS, PW, TH)
print('cr pavilion rebuilt faces', len(pav.data.polygons), 'mats', [m.name for m in pav.data.materials], flush=True)
# ---------- pavilion + long wall material: cast stone (beige) like both Commons photos; per-mesh slot, Cole Hall's own material untouched
CS = bpy.data.materials.get('Plaza_cast_stone_cr') or bpy.data.materials.new('Plaza_cast_stone_cr'); CS.use_nodes = True
bs = CS.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value = (0.74, 0.70, 0.62, 1); bs.inputs['Roughness'].default_value = 0.85
pav.data.materials[0] = CS
# ---------- the long arched wall (Commons 12550692334 + 13252662863): LiDAR thin unclassified line, flat top 133.94 (p90, every 2 m), ground
# 130.24, from the pavilion (s 73.09, u -11.23) to (s 87.09, u -28.79) [Kasser s/u frame] = world (-182.01,-75.54) -> (-172.75,-96.01).
# Form from 12550692334: round arches on square piers, pier:opening ~0.3, crown ~0.74 of the height, flat coping with a band. Arch count,
# spans, pier size and thickness = UNVERIFIED (photo-scaled).
WN = 'Plaza long arched wall (LiDAR line/top MEASURED; arches UNVERIFIED) cr'
for old in [o for o in bpy.data.objects if o.name.startswith('Plaza long arched wall') and o.library is None]:   # cs: WN > 63 chars, so .get(WN) never matched (cr's rerun left duplicates)
    me_old = old.data; bpy.data.objects.remove(old)
    if me_old.users == 0: bpy.data.meshes.remove(me_old)
for _m in [m for m in bpy.data.meshes if m.name.startswith('Plaza long arched wall') and m.users == 0]: bpy.data.meshes.remove(_m)
mw = bpy.data.meshes.new(WN); ow = bpy.data.objects.new(WN, mw); pav.users_collection[0].objects.link(ow); mw.materials.append(CS)
bm = bmesh.new()
e1 = Vector((-182.01, -75.54)); e0 = Vector((-172.75, -96.01))
# start at the pavilion's outer wall face: walk from e1 toward e0 until outside the pavilion square (|local| > h)
tt = (e0 - e1).normalized(); Ri = Rm.inverted()
def inside(a):
    lq = Ri @ (e1 + tt * a - Vector((cx, cy))).to_3d(); return max(abs(lq.x), abs(lq.y)) <= h
a_st = 0.0
if inside(0.0):
    while inside(a_st) and a_st < 8: a_st += 0.01                     # walk out to the pavilion face
else:
    while not inside(a_st) and a_st > -4: a_st -= 0.01                # LiDAR end short of the pavilion: walk back to its face
    a_st += 0.01
a_st -= 0.05                                                            # 5 cm into the pavilion pier (joint hidden)
print('cr long wall start offset from the LiDAR end %.2f m' % a_st, flush=True)
w0 = e1 + tt * a_st; L = (e0 - w0).length; nn = Vector((tt.y, -tt.x))
ZG, ZTOP = 130.24, 133.94; TH2 = 0.55; PW2 = 0.85
nb = 6  # cs: 6 arches (12550692334 proportions)
bw = (L - PW2) / nb; R2 = (bw - PW2) / 2; ZS2 = ZG + 2.73 - R2
P = lambda a, o, z: Vector((w0.x + tt.x * a + nn.x * o, w0.y + tt.y * a + nn.y * o, z))
def sb(a0, a1, o0, o1, z0, z1, mi=0):
    c = [P(a, o, z) for z in (z0, z1) for o in (o0, o1) for a in (a0, a1)]
    for ix in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)): F(*[c[i] for i in ix], mi=mi)
ZC = ZTOP - 0.20
for k in range(nb + 1):
    a = k * bw; sb(a, a + PW2, -TH2 / 2, TH2 / 2, ZG - 0.6, ZC)                                   # piers (0.6 m into the ground)
    sb(a - 0.05, a + PW2 + 0.05, -TH2 / 2 - 0.05, TH2 / 2 + 0.05, ZG - 0.6, ZG + 0.45)              # plinths
for k in range(nb):
    ac = k * bw + PW2 + R2
    arc = [(ac - R2 * math.cos(math.pi * i / N), ZS2 + R2 * math.sin(math.pi * i / N)) for i in range(N + 1)]
    for i in range(N):
        (a0, z0), (a1, z1) = arc[i], arc[i + 1]
        F(P(a0, -TH2 / 2, z0), P(a1, -TH2 / 2, z1), P(a1, -TH2 / 2, ZC), P(a0, -TH2 / 2, ZC))
        F(P(a0, TH2 / 2, ZC), P(a1, TH2 / 2, ZC), P(a1, TH2 / 2, z1), P(a0, TH2 / 2, z0))
        F(P(a1, -TH2 / 2, z1), P(a0, -TH2 / 2, z0), P(a0, TH2 / 2, z0), P(a1, TH2 / 2, z1))
    F(P(k * bw + PW2, -TH2 / 2, ZC), P(k * bw + PW2, TH2 / 2, ZC), P(ac + R2, TH2 / 2, ZC), P(ac + R2, -TH2 / 2, ZC))
sb(-0.02, L + 0.06, -TH2 / 2 - 0.06, TH2 / 2 + 0.06, ZC, ZTOP)                                   # coping (flat top = LiDAR 133.94)
sb(-0.02, L + 0.03, -TH2 / 2 - 0.025, TH2 / 2 + 0.025, ZC - 0.18, ZC)                            # band under the coping
SHD = bpy.data.materials.get('Plaza_cast_stone_shadow_cs') or bpy.data.materials.new('Plaza_cast_stone_shadow_cs'); SHD.use_nodes = True
_bs = SHD.node_tree.nodes['Principled BSDF']; _bs.inputs['Base Color'].default_value = (0.42, 0.39, 0.33, 1); _bs.inputs['Roughness'].default_value = 0.9
mw.materials.append(SHD)
nfr = 0
for side in (-1, 1):
    o_face = side * (TH2 / 2 + 0.025)
    a = 0.20
    while a < L - 0.15:
        o0, o1 = (o_face, o_face + side * 0.003) if side > 0 else (o_face + side * 0.003, o_face)
        sb(a, a + 0.14, o0, o1, ZC - 0.135, ZC - 0.045, mi=1); nfr += 1; a += 0.32
print('cs long-wall frieze tiles', nfr, flush=True)
print('cs long walls now', [o.name for o in bpy.data.objects if o.name.startswith('Plaza long arched wall')], flush=True)
bm.to_mesh(mw); bm.free()
ow['cs_long_wall'] = 'cs: 6 arches, piers 0.85, frieze tiles %d' % nfr
ow['cr_long_wall'] = 'L %.2f from the pavilion face, %d arches span %.2f r %.2f spring %.2f, piers %.2f, top 133.94 MEASURED' % (L, nb, bw - PW2, R2, ZS2, PW2)
print('cr long wall', ow['cr_long_wall'], 'faces', len(mw.polygons), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cs plaza main: SAVED', flush=True)
