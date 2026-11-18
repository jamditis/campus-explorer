"""Session ch (Oct 19 ~6:30 PM ET). MAIN blend (Kasser's owner). NEW KASSER ENTRY POINT (supersedes the cg script as entry; SAVE=1 saves).
RUN ORDER: this script runs scripts/kasser_roof_step_tone_20261019cg.py first (SAVE forced 0; which itself re-runs the cf trim from the
cf_orig_* copies and redoes the cg step box + Kasser-only *__kasser_cg materials), THEN replaces the LiDAR-draped tile/membrane surface of
'Alexander Kasser Theater roof (LiDAR)' with clean planes. Idempotent (each run starts from the cg state). The pre-ch (cg-state) roof mesh is
kept as fake-user mesh 'ch_orig_kasser_roof_cg_state' (restorable: assign it to the roof object).
ch rebuild:
 1) Least-squares planes z = a + b x + c y (area-weighted, face corner points) per tile plane class from the LiDAR facets (normal azimuth in
    the deck frame s/u): S (faces -u), N (+u), E (hip end, +s), SE (diagonal hip, az ~ -48). Membrane strip = flat plane at the MEASURED
    median 138.151 m. Tile surface = lower envelope min(S,N,E,SE) (convex hip roof -> straight ridge and hips).
 2) Strip/tile boundary = one straight line in plan s = L0 + L1*u (fitted to the F/tile transition per 1 m u bin, rms 0.33 m); strip side
    flattened to 138.151, tile side on the envelope, mesh bisected along L and every plane-pair intersection (ridge/hips) so creases are
    straight; split along L and bridged with vertical stucco step faces (straight step edge, no scallop).
 3) The cg step box and the old vertical LiDAR step faces are removed (box hole refilled before re-projection).
 4) Deck-side flashing upstand: open roof edges within 2.3 m of the shared OSM edge are extruded UP by UPST (0.30 m) in stucco (parapet /
    flashing line; gap to the deck/core faces kept by the cf INSET 0.25 / NOTCH 1.80).
 5) roofc point colour (shader tile/membrane read) set to the median strip / tile values on each side of L. 4a BVH check printed."""
import bpy, bmesh, os, runpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
UPST = float(os.environ.get('UPST', '0.30'))
L0, L1 = float(os.environ.get('L0', '0.752')), float(os.environ.get('L1', '0.5555'))
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_roof_step_tone_20261019cg.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(x, y): p = np.array([x, y]) - A; return float(p @ n), float(p @ d)
def xy(s, u): p = A + n * s + d * u; return float(p[0]), float(p[1])
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']
on = 'ch_orig_kasser_roof_cg_state'
old = bpy.data.meshes.get(on)
if old: bpy.data.meshes.remove(old)
keep = ro.data.copy(); keep.name = on; keep.use_fake_user = True
M = ro.matrix_world.copy(); Mi = M.inverted()
bm = bmesh.new(); bm.from_mesh(ro.data); bm.transform(M); bm.normal_update()
mats = [m.name if m else '' for m in ro.data.materials]
MI_ST = mats.index('Wall_stucco_mission')
ZSTRIP = 138.151
rc = bm.verts.layers.float_color.get('roofc')
# ---- classify + fit planes (before edits)
def azsu(f):
    ns = f.normal.x * n[0] + f.normal.y * n[1]; nu = f.normal.x * d[0] + f.normal.y * d[1]; return np.degrees(np.arctan2(nu, ns))
cls = {'S': (-112, -68), 'N': (68, 112)}   # E/SE (east hip end over the curved/diagonal footprint) are not single planes in the data (offset spread 50-70 m): kept as-is
pts = {k: [] for k in cls}
stripc = []; tilec = []
for f in bm.faces:
    if f.material_index != 0: continue
    c = f.calc_center_median(); s, u = su(c.x, c.y)
    if f.normal.z > 0.99 and abs(c.z - ZSTRIP) < 0.05:
        stripc += [tuple(v[rc]) for v in f.verts]; continue
    if not (0.3 < f.normal.z < 0.99): continue
    if s < L0 + L1 * u + 2.0: continue   # skip the scallop band
    az = azsu(f)
    tilec += [tuple(v[rc]) for v in f.verts]
    for k, (lo, hi) in cls.items():
        if lo <= az < hi:
            w = f.calc_area()
            for v in f.verts: pts[k].append((v.co.x, v.co.y, v.co.z, w)); break
PL = {}
for k, P in pts.items():
    P = np.array(P); X = np.c_[np.ones(len(P)), P[:, 0], P[:, 1]]; W = np.sqrt(P[:, 3])
    m = np.ones(len(P), bool)
    for it in range(4):   # trimmed least squares (drop |res| > 0.25 m and refit)
        coef, *_ = np.linalg.lstsq(X[m] * W[m, None], P[m, 2] * W[m], rcond=None)
        res = P[:, 2] - X @ coef; m = np.abs(res) < 0.25
    res = res[m]; PL[k] = coef; print(f'ch plane {k} inliers {m.sum()}/{len(m)}', flush=True)
    nrm = np.array([-coef[1], -coef[2], 1]); nrm /= np.linalg.norm(nrm)
    print(f'ch plane {k}: n {len(P)} pts, pitch {np.degrees(np.arccos(nrm[2])):.2f} deg, rms {res.std():.3f} m, max|res| {abs(res).max():.2f}', flush=True)
def env(x, y): return min(c[0] + c[1] * x + c[2] * y for c in PL.values())
SC = np.median(np.array(stripc), axis=0); TC = np.median(np.array(tilec), axis=0)
print('ch roofc strip', SC.round(3), 'tile', TC.round(3), flush=True)
# ---- remove the cg box (stucco faces + its top) and old vertical step faces
box = [f for f in bm.faces if f.material_index == MI_ST]
bverts = set(v for f in box for v in f.verts)
boxtop = [f for f in bm.faces if f.material_index == 0 and all(v in bverts for v in f.verts)]
vert = [f for f in bm.faces if f.material_index == 0 and f.normal.z < 0.3]
dl = list(set(box + boxtop + vert))
bmesh.ops.delete(bm, geom=dl, context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
print('ch deleted box', len(box), 'boxtop', len(boxtop), 'vertical', len(vert), flush=True)
# ---- reproject all verts of mat0 faces
def side0(x, y): s, u = su(x, y); return s - (L0 + L1 * u)
def side(x, y):   # <0 strip, >0 tile. South of the ridge, where the S plane is below the strip (by the RHD SE core), the tile runs on to the
    # deck notch and the strip starts at the S-plane 138.151 contour (straight crease), instead of a strip hanging above the eave.
    sd = side0(x, y); s, u = su(x, y)
    if sd < 0 and u < 22 and (PL['S'][0] + PL['S'][1] * x + PL['S'][2] * y) < ZSTRIP: return 1e-3 + 0 * sd
    return sd
m0v = set(v for f in bm.faces if f.material_index == 0 for v in f.verts)
dz_shared = 0.0; BAND = float(os.environ.get('BAND', '8.0')); TOUCH = set()
for v in m0v:
    sd0 = side(v.co.x, v.co.y)
    if any(f.material_index != 0 for f in v.link_faces): continue   # eave-attached verts keep their (straight, level) eave z
    if sd0 < 0: znew = ZSTRIP
    elif sd0 < BAND or abs(v.co.z - env(v.co.x, v.co.y)) < 0.5: znew = env(v.co.x, v.co.y)
    else: znew = v.co.z   # east hip part kept
    TOUCH.add(v)
    if any(f.material_index != 0 for f in v.link_faces): dz_shared = max(dz_shared, abs(znew - v.co.z))
    v.co.z = znew
r = bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.005)
bm.normal_update()
# fill small holes (cg wedge hole etc.)
hf = bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=80)
for f in hf['faces']: f.material_index = 0
def inreg(v): s_, u_ = su(v.co.x, v.co.y); return 1.9 < s_ < 12 and 1.0 < u_ < 14
rege = [e for e in bm.edges if e.is_boundary and inreg(e.verts[0]) and inreg(e.verts[1])]
hf2 = bmesh.ops.holes_fill(bm, edges=rege, sides=1000)
for f in hf2['faces']: f.material_index = 0
print('ch region boundary edges (cg wedge hole)', len(rege), 'filled faces', len(hf2['faces']), flush=True)
if hf2['faces']: bmesh.ops.triangulate(bm, faces=hf2['faces'])
print('ch holes filled', len(hf['faces']), 'max dz at eave-shared verts', round(dz_shared, 3), flush=True)
# ---- bisect along ridge/hip intersection lines and L
cuts = []
ks = list(PL)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        a = PL[ks[i]] - PL[ks[j]]; nn = Vector((a[1], a[2], 0)); ln = nn.length
        if ln < 1e-6: continue
        p0 = Vector((-a[0] * a[1] / ln**2, -a[0] * a[2] / ln**2, 0)); cuts.append((ks[i] + ks[j], p0, nn / ln))
a = PL['S'] - np.array([ZSTRIP, 0, 0]); nn = Vector((a[1], a[2], 0)); ln = nn.length
cuts.append(('S138', Vector((-a[0] * a[1] / ln**2, -a[0] * a[2] / ln**2, 0)), nn / ln))
x0, y0 = xy(L0, 0); x1, y1 = xy(L0 + L1 * 10, 10)
dL = Vector((x1 - x0, y1 - y0, 0)).normalized(); nL = Vector((dL.y, -dL.x, 0)); pL = Vector((x0, y0, 0))
for nm_, p0, nn in cuts:
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=p0, plane_no=nn)
bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=pL, plane_no=nL)
onL = lambda v: abs((v.co - pL).dot(nL)) < 2e-4
Ledges = [e for e in bm.edges if onL(e.verts[0]) and onL(e.verts[1]) and any(f.material_index == 0 for f in e.link_faces)]
bmesh.ops.split_edges(bm, edges=Ledges)
# reassign z per face side (L verts now belong to one side each)
for v in bm.verts:
    lf = [f for f in v.link_faces if f.material_index == 0]
    if not lf or len(lf) != len(v.link_faces): continue   # skip eave-attached verts
    if onL(v):
        sd = np.mean([side(f.calc_center_median().x, f.calc_center_median().y) for f in lf])
    else: sd = side(v.co.x, v.co.y)
    if sd < 0: v.co.z = ZSTRIP
    elif sd < BAND or abs(v.co.z - env(v.co.x, v.co.y)) < 0.5: v.co.z = env(v.co.x, v.co.y)
    v[rc] = tuple(SC) if sd < 0 else (tuple(TC) if abs(sd) < 3.0 or onL(v) else v[rc])
# bridge L: pair boundary edges on L by xy
key = lambda v: (round(v.co.x, 3), round(v.co.y, 3))
bL = [e for e in bm.edges if e.is_boundary and onL(e.verts[0]) and onL(e.verts[1])]
strip_e = {}; tile_e = []
for e in bL:
    if abs(e.verts[0].co.z - ZSTRIP) < 1e-4 and abs(e.verts[1].co.z - ZSTRIP) < 1e-4 and e.link_faces and side(*e.link_faces[0].calc_center_median().xy) < 0:
        strip_e[frozenset((key(e.verts[0]), key(e.verts[1])))] = e
    else: tile_e.append(e)
nb = 0; newf = []
for e in tile_e:
    k2 = frozenset((key(e.verts[0]), key(e.verts[1]))); se = strip_e.get(k2)
    if se is None: continue
    a0, a1 = e.verts; b0 = next(v for v in se.verts if key(v) == key(a0)); b1 = next(v for v in se.verts if key(v) == key(a1))
    if abs(a0.co.z - b0.co.z) < 1e-3 and abs(a1.co.z - b1.co.z) < 1e-3: continue
    try:
        f = bm.faces.new((a0, a1, b1, b0)); f.material_index = MI_ST; newf.append(f); nb += 1
    except ValueError: pass
bm.normal_update()
for f in newf:   # step faces face the lower side
    c = f.calc_center_median(); hi_tile = env(c.x, c.y) > ZSTRIP
    want = nL if hi_tile else -nL    # nL points toward +side (tile)? orient toward the lower side
    if side(c.x + nL.x, c.y + nL.y) < side(c.x, c.y): want = -want
    if f.normal.dot(-want if hi_tile else want) < 0: pass
# simpler robust orientation: normal must point to the side whose surface is lower
for f in newf:
    c = f.calc_center_median(); p = Vector((c.x, c.y, 0)) + f.normal.xy.to_3d() * 0.5
    zside = ZSTRIP if side(p.x, p.y) < 0 else env(p.x, p.y)
    if zside > c.z + 0.01 and abs(zside - c.z) > 0: f.normal_flip()
print('ch L bisect edges', len(Ledges), 'step faces', nb, 'of tile L edges', len(tile_e), flush=True)
# orient tile/membrane faces up
flip = 0
for f in bm.faces:
    if f.material_index == 0 and f.normal.z < 0: f.normal_flip(); flip += 1
# degenerate cleanup
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=1e-4)
bm.normal_update()
# ---- clean patch over the old cg wedge/box area by the SE core (the leftover hole there is not a closed loop): rectangle R in (s,u),
# bisected out of the mesh and rebuilt as exact polygons: strip piece (138.151; u > S-plane contour, s < L), tile piece (S plane), and a
# vertical stucco step along L between them.
RS0, RS1, RU0, RU1 = 1.80, 6.50, 4.50, 8.50
def sp(s_, u_): x_, y_ = xy(s_, u_); return PL['S'][0] + PL['S'][1] * x_ + PL['S'][2] * y_
def uc(s_):   # S-plane 138.151 contour at this s
    lo, hi = -5.0, 22.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if sp(s_, mid) < ZSTRIP: lo = mid
        else: hi = mid
    return (lo + hi) / 2
for sv in (RS1,):
    c_ = xy(sv, 0); co = Vector((c_[0], c_[1], 0)); bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=co, plane_no=Vector((n[0], n[1], 0)))
for uv in (RU0, RU1):
    c_ = xy(0, uv); co = Vector((c_[0], c_[1], 0)); bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=co, plane_no=Vector((d[0], d[1], 0)))
def inR(f): s_, u_ = su(*f.calc_center_median().xy); return RS0 - 0.5 < s_ < RS1 and RU0 < u_ < RU1
kill = [f for f in bm.faces if inR(f) and f.material_index in (0, MI_ST)]
bmesh.ops.delete(bm, geom=kill, context='FACES'); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
# contour/L meeting point
lo, hi = RU0, RU1
for _ in range(60):
    mid = (lo + hi) / 2
    if L0 + L1 * mid - 0 < 0: pass
    # f(mid) = side0 at (L-line point) ... solve s_L(u) where uc(s_L(u)) == u
    if uc(L0 + L1 * mid) > mid: lo = mid
    else: hi = mid
uq = (lo + hi) / 2; sq = L0 + L1 * uq; ua = uc(RS0)
def V3(s_, u_, z_): x_, y_ = xy(s_, u_); return bm.verts.new((x_, y_, z_))
tilepoly = [(RS0, RU0), (RS1, RU0), (RS1, RU1), (L0 + L1 * RU1, RU1), (sq, uq), (RS0, ua)]
strippoly = [(RS0, ua), (sq, uq), (L0 + L1 * RU1, RU1), (RS0, RU1)]
pf = []
tv = [V3(s_, u_, sp(s_, u_)) for s_, u_ in tilepoly]; ft = bm.faces.new(tv); ft.material_index = 0; pf.append(ft)
sv_ = [V3(s_, u_, ZSTRIP) for s_, u_ in strippoly]; fs = bm.faces.new(sv_); fs.material_index = 0; pf.append(fs)
for v in tv: v[rc] = tuple(TC)
for v in sv_: v[rc] = tuple(SC)
stp = bm.faces.new((tv[4], tv[3], sv_[2], sv_[1])); stp.material_index = MI_ST
bm.normal_update()
for f in pf:
    if f.normal.z < 0: f.normal_flip()
c_ = stp.calc_center_median()
if (c_ + stp.normal * 0.3 - c_).dot(Vector((n[0], n[1], 0))) > 0: stp.normal_flip()   # faces the strip (lower, -s side of L)
tri = bmesh.ops.triangulate(bm, faces=pf)
bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.002)
print('ch SE-core patch: killed', len(kill), 'contour u at s=1.8', round(ua, 2), 'L/contour meet s,u', round(sq, 2), round(uq, 2), flush=True)
# ---- drop the orphaned strip-eave pieces by the RHD SE core (eave tile/fascia faces at the old 137.3-138.15 strip eave, s<8, u<0.5):
# the tile now runs to the deck notch there at the S-plane eave (~134.1), so these stretched faces were the 'tile tooth' by the core.
orph = [f for f in bm.faces if f.material_index in (1, 2) and (lambda c: su(c.x, c.y))(f.calc_center_median())[0] < 8.0
        and su(*f.calc_center_median().xy)[1] < 0.5 and max(v.co.z for v in f.verts) > 135.0]
ORPH = os.environ.get('ORPH', '0') == '1'   # OFF: the 134.1-138.15 eave band is the S-facade eave everywhere (not an orphan; probe ch)
if ORPH: bmesh.ops.delete(bm, geom=orph, context='FACES'); bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
print('ch orphan strip-eave faces', len(orph), 'removed' if ORPH else 'kept', flush=True)
# ---- deck-side flashing upstand
de = [e for e in bm.edges if e.is_boundary and any(f.material_index == 0 for f in e.link_faces)
      and max(su(v.co.x, v.co.y)[0] for v in e.verts) < 2.3 and -3 < su(e.verts[0].co.x, e.verts[0].co.y)[1] < 60]
ret = bmesh.ops.extrude_edge_only(bm, edges=de)
for g in ret['geom']:
    if isinstance(g, bmesh.types.BMVert): g.co.z += UPST
    if isinstance(g, bmesh.types.BMFace): g.material_index = MI_ST
bm.normal_update()
rem = [e for e in bm.edges if e.is_boundary and inreg(e.verts[0]) and inreg(e.verts[1])]
print('ch region boundary edges left', len(rem), [tuple(round(x, 2) for x in su(*e.verts[0].co.xy)) + (round(e.verts[0].co.z, 2),) for e in rem[:12]], flush=True)
nonman = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
zt = [v.co.z for v in bm.verts if v[rc] is not None]
print('ch flips fixed', flip, 'upstand edges', len(de), 'nonmanifold edges', nonman, 'boundary edges', sum(1 for e in bm.edges if e.is_boundary), 'zmax', round(max(zt), 3), flush=True)
ridge = max(env(*xy(s_, u_)) for s_ in np.arange(10, 66, 0.5) for u_ in np.arange(0, 45, 0.5))
print('ch ridge (envelope max over footprint grid)', round(ridge, 3), 'eave S/N at plane z mins:', {k: None for k in PL}, flush=True)
# ---- 4a
z = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = z['tris']; ob = z['obj']; nm = z['names']; kp = np.array([not str(nm[i]).startswith('NT_') for i in ob]); T = T[kp]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
print('ch 4a roof overlap pairs', len(BVHTree.FromBMesh(bm).overlap(RB)), flush=True)
bm.transform(Mi); bm.to_mesh(ro.data); bm.free(); ro.data.update()
# ---- eave soffit/fascia + barrel eave course by the RHD SE core followed the old LiDAR strip eave at ~138 m, 4 m above the S wall
# top (133.93 MEASURED from the walls mesh): lower those pieces (s<13, u<1.5, z>ref+1.5) by the offset to the normal S eave (ref =
# median z of the same object's verts at u<0.5, 15<s<30), so the eave line is straight and level along the whole S facade.
for nm2 in ['Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course']:
    o = bpy.data.objects[nm2]; me = o.data; Mw = o.matrix_world
    W = [(v, Mw @ v.co) for v in me.vertices]
    ref = [w.z for v, w in W if su(w.x, w.y)[1] < 0.5 and 15 < su(w.x, w.y)[0] < 30]
    if not ref: print('ch eave fix: no ref for', nm2[:30]); continue
    zr = float(np.median(ref))
    fl = [(v, w) for v, w in W if su(w.x, w.y)[0] < 13 and su(w.x, w.y)[1] < 1.5 and w.z > zr + 1.5]
    if fl:
        dz = float(np.median([w.z for v, w in fl])) - zr
        for v, w in fl: v.co = Mw.inverted() @ Vector((w.x, w.y, w.z - dz))
        me.update(); print('ch eave fix', nm2[:30], 'ref z', round(zr, 3), 'lowered', len(fl), 'verts by', round(dz, 3), flush=True)
for nm2 in ['Alexander Kasser Theater walls', 'Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course']:
    o = bpy.data.objects[nm2]; b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('ch 4a', nm2[:40], 'overlap pairs', len(BVHTree.FromBMesh(b2).overlap(RB)), flush=True); b2.free()
ro['ch_planar_roof'] = 'planes ' + '; '.join(f'{k}: z={c[0]:.3f}{c[1]:+.5f}x{c[2]:+.5f}y' for k, c in PL.items()) + f'; strip {ZSTRIP}; L s={L0}+{L1}u; upstand {UPST}'
if 'cg_roof_step' in ro.keys(): ro['cg_roof_step'] = 'REPLACED by ch planar roof (box removed)'
if SAVE: bpy.ops.wm.save_mainfile(); print('ch main: SAVED', flush=True)
