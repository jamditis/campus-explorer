"""Session ci (Oct 19 ~7:30 PM ET). MAIN blend (Kasser's owner). NEW KASSER ENTRY POINT (supersedes the ch script as entry; SAVE=1 saves).
RUN ORDER: runs scripts/kasser_planar_roof_20261019ch.py first (SAVE forced 0; it runs cg -> cf trim from cf_orig_*), THEN adds, INTO the
roof object mesh 'Alexander Kasser Theater roof (LiDAR)' (so the north blend picks them up through its existing link, no north edit):
 1) ridge cap course: tapered half-round barrel caps (0.42 m pitch, r 0.13 -> 0.115 m, skirts buried 7 cm) along the straight S/N ridge
    (S∩N plane intersection), over the s-range where roof verts sit on both planes; material = the barrel eave course material.
 2) coping (precast tone, new material Kasser_coping_precast_ci) swept along the top of the deck-side 0.30 m stucco upstand (lateral
    -0.04..+0.20 m, 0.07 m thick) + a stucco back face so the upstand reads as a 0.16 m thick parapet; and a coping/verge trim along the
    upper edge of the strip/tile stucco step faces (lateral -0.05..+0.22, 0.06 m thick, 2 cm seated).
 0) (HIP=1, default) east hip end rebuilt as clean planes: trimmed least-squares fits of the E hip facets (normal az 10..25 deg in the
    deck frame, s > 40; faces the NNW-diagonal OSM wall) and SE hip facets (az -62..-45), envelope min(S, N, E, SE); tile verts east of
    s 34 within SNAP of the envelope (not eave-attached) are snapped, mesh bisected along every plane-pair line so hips are straight.
    Hip caps (same barrel caps) laid along every S/N/E/SE crease found on the mesh.
Idempotent (each run starts from the ch state). 4a BVH printed for every Kasser object (cf npz, trees excluded)."""
import bpy, bmesh, os, re, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_planar_roof_20261019ch.py', run_name='__main__')
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
def su(x, y): p = np.array([x, y]) - A; return float(p @ n), float(p @ d)
def xy(s, u): p = A + n * s + d * u; return float(p[0]), float(p[1])
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']
PL = {}
for k, a, b, c in re.findall(r'(\w+): z=(-?[\d.]+)([+-][\d.]+)x([+-][\d.]+)y', ro['ch_planar_roof']): PL[k] = (float(a), float(b), float(c))
def zp(k, x, y): a, b, c = PL[k]; return a + b * x + c * y
print('ci planes', PL, flush=True)
# ---- materials
me = ro.data; mats = [m.name if m else '' for m in me.materials]
MI_ST = mats.index('Wall_stucco_mission')
eo = bpy.data.objects['Alexander Kasser Theater barrel tile eave course']
tm = eo.active_material
print('ci eave course mat', tm.name if tm else None, [nd.type for nd in tm.node_tree.nodes] if tm and tm.use_nodes else None, flush=True)
cm = bpy.data.materials.get('Kasser_coping_precast_ci')
if cm is None:
    cm = bpy.data.materials.new('Kasser_coping_precast_ci'); cm.use_nodes = True
    nt = cm.node_tree; bs = nt.nodes['Principled BSDF']
    bs.inputs['Base Color'].default_value = (0.56, 0.54, 0.50, 1); bs.inputs['Roughness'].default_value = 0.62
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40.0; nz.inputs['Detail'].default_value = 6.0
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.06
    nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], bs.inputs['Normal'])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.inputs['A'].default_value = (0.50, 0.48, 0.45, 1); mx.inputs['B'].default_value = (0.60, 0.58, 0.54, 1)
    nt.links.new(nz.outputs['Fac'], mx.inputs['Factor']); nt.links.new(mx.outputs['Result'], bs.inputs['Base Color'])
for m in (tm, cm):
    if m.name not in [x.name for x in me.materials if x]: me.materials.append(m)
mats = [m.name if m else '' for m in me.materials]
MI_RC = mats.index(tm.name); MI_CP = mats.index(cm.name)
M = ro.matrix_world.copy(); Mi = M.inverted()
bm = bmesh.new(); bm.from_mesh(me); bm.transform(M); bm.normal_update()
HIP = os.environ.get('HIP', '1') == '1'; SNAP = float(os.environ.get('SNAP', '2.4')); FEND = float(os.environ.get('FEND', '2.5'))   # ci tests: SNAP 0.6 / feather 0.3-1.0 left LiDAR dents at the SE + NE footprint jogs; full snap is clean
def azsu(f):
    ns = f.normal.x * n[0] + f.normal.y * n[1]; nu = f.normal.x * d[0] + f.normal.y * d[1]; return math.degrees(math.atan2(nu, ns))
if HIP:
    cls = {'E': (10, 25), 'SE': (-62, -45)}; pts = {k: [] for k in cls}
    for f in bm.faces:
        if f.material_index != 0 or not (0.3 < f.normal.z < 0.99): continue
        c = f.calc_center_median()
        if su(c.x, c.y)[0] < 40: continue
        az = azsu(f)
        for k, (lo, hi) in cls.items():
            if lo <= az < hi:
                w = f.calc_area(); pts[k] += [(v.co.x, v.co.y, v.co.z, w) for v in f.verts]
    for k, P in pts.items():
        P = np.array(P); X = np.c_[np.ones(len(P)), P[:, 0], P[:, 1]]; W = np.sqrt(P[:, 3]); m = np.ones(len(P), bool)
        for it in range(5):
            coef, *_ = np.linalg.lstsq(X[m] * W[m, None], P[m, 2] * W[m], rcond=None); res = P[:, 2] - X @ coef; m = np.abs(res) < 0.25
        PL[k] = tuple(coef); nr = np.array([-coef[1], -coef[2], 1]); nr /= np.linalg.norm(nr)
        print(f'ci hip plane {k}: inliers {m.sum()}/{len(m)}, pitch {np.degrees(np.arccos(nr[2])):.2f} deg, rms {res[m].std():.3f} m', flush=True)
    def env4(x, y): return min(zp(k, x, y) for k in PL)
    def east_faces(): return [f for f in bm.faces if f.material_index == 0 and su(*f.calc_center_median().xy)[0] > 34 and f.normal.z > 0.3]
    def eaveatt(v): return any(f.material_index != 0 for f in v.link_faces)
    nb = 0
    for i, j in [('S', 'N'), ('S', 'SE'), ('SE', 'E'), ('E', 'N'), ('S', 'E'), ('SE', 'N')]:
        a = np.array(PL[i]) - np.array(PL[j]); nn = Vector((a[1], a[2], 0)); L = nn.length
        if L < 1e-9: continue
        co = Vector((-a[0] * a[1] / L**2, -a[0] * a[2] / L**2, 0))
        ef = east_faces(); geom = list(set([e for f in ef for e in f.edges] + ef + [v for f in ef for v in f.verts]))
        r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=nn / L, dist=0.002); nb += len([g for g in r['geom_cut'] if isinstance(g, bmesh.types.BMEdge)])
    mv = []; far = 0; nfe = 0
    for v in set(v for f in east_faces() for v in f.verts):
        if eaveatt(v): continue
        ze = env4(v.co.x, v.co.y); dz = ze - v.co.z
        if abs(dz) < FEND:   # full snap below SNAP, linear feather to 0 at FEND (keeps the LiDAR jog corners continuous)
            w = 1.0 if abs(dz) <= SNAP else (FEND - abs(dz)) / (FEND - SNAP); v.co.z += dz * w; mv.append(abs(dz))
            if w < 1: nfe += 1
        else:
            far += 1
            if os.environ.get('DBG'): print('ci far', [round(x, 2) for x in su(v.co.x, v.co.y)], round(v.co.z, 2), 'dz', round(dz, 2), flush=True)
    bm.normal_update()
    print('ci hip: bisect cut edges', nb, 'snapped', len(mv), 'max|dz|', round(max(mv), 3) if mv else 0, 'median', round(float(np.median(mv)), 3) if mv else 0, 'feathered', nfe, 'left (> FEND)', far, flush=True)
# ---- 1) ridge + hip caps along every plane-pair crease present on the mesh
NSEG = 10; PITCH = 0.42; ncap = 0; CAPS = []
def creases():
    out = []
    ks = list(PL)
    for ii in range(len(ks)):
        for jj in range(ii + 1, len(ks)):
            i, j = ks[ii], ks[jj]
            vv = [v for v in bm.verts if any(f.material_index == 0 for f in v.link_faces) and all(f.material_index == 0 for f in v.link_faces)
                  and abs(v.co.z - zp(i, v.co.x, v.co.y)) < 0.03 and abs(v.co.z - zp(j, v.co.x, v.co.y)) < 0.03
                  and all(zp(k, v.co.x, v.co.y) > v.co.z - 0.03 for k in ks)]
            if len(vv) < 3: continue
            P = np.array([v.co[:] for v in vv]); c0 = P.mean(0); U, S_, Vt = np.linalg.svd(P[:, :2] - c0[:2]); dr = Vt[0]
            t = (P[:, :2] - c0[:2]) @ dr; o = np.argsort(t); t = t[o]; P = P[o]
            cut = np.nonzero(np.diff(t) > 1.5)[0] + 1   # split into runs where the crease is really on the mesh (gaps = unsnapped LiDAR)
            for r_ in np.split(np.arange(len(t)), cut):
                if len(r_) < 3 or t[r_[-1]] - t[r_[0]] < 1.0: continue
                out.append((i + '/' + j, Vector(P[r_[0]]), Vector(P[r_[-1]]), len(r_)))
    return out
for name, q0, q1, nv in creases():
    ax = (q1 - q0); Lr = ax.length; ax.normalize()
    lat = Vector((-ax.y, ax.x, 0)).normalized()
    up = ax.cross(lat).normalized()
    if up.z < 0: up = -up
    t = 0.0; k0 = ncap
    while t < Lr - 0.05:
        t1 = min(t + PITCH + 0.03, Lr)
        secs = []
        for tt, r in ((t, 0.130), (t1, 0.115)):
            c = q0 + ax * tt - up * 0.035
            ring = [c + lat * r - up * 0.07] + [c + lat * (r * math.cos(math.pi * i / NSEG)) + up * (r * math.sin(math.pi * i / NSEG)) for i in range(NSEG + 1)] + [c - lat * r - up * 0.07]
            secs.append([bm.verts.new(p) for p in ring])
        a_, b_ = secs
        for i in range(len(a_) - 1):
            f = bm.faces.new((a_[i], a_[i + 1], b_[i + 1], b_[i])); f.material_index = MI_RC; f.smooth = True
        for ring in (a_, b_):
            f = bm.faces.new(ring if ring is b_ else list(reversed(ring))); f.material_index = MI_RC
        CAPS.append((q0.copy(), ax.copy(), t)); ncap += 1; t += PITCH
    print(f'ci cap crease {name}: {nv} verts, length {Lr:.2f} m, z {q0.z:.2f}->{q1.z:.2f}, su {[round(x,1) for x in su(q0.x,q0.y)]}->{[round(x,1) for x in su(q1.x,q1.y)]}, caps {ncap - k0}', flush=True)
# ---- 2) coping sweeps
def chains(segs):
    adj = {}
    for i, (a, b, q) in enumerate(segs): adj.setdefault(a, []).append(i); adj.setdefault(b, []).append(i)
    used = set(); out = []
    starts = [v for v, l in adj.items() if len(l) != 2] + list(adj)
    for v0 in starts:
        for si in adj[v0]:
            if si in used: continue
            ch = [v0]; qs = []; v = v0; s_ = si
            while s_ is not None and s_ not in used:
                used.add(s_); a, b, q = segs[s_]; w = b if a == v else a; ch.append(w); qs.append(q); v = w
                nx = [x for x in adj[v] if x not in used] if len(adj[v]) == 2 else []
                s_ = nx[0] if nx else None
            out.append((ch, qs))
    return out
def sweep(ch, qs, a, b, z0, z1, mi):
    P = [v.co.copy() for v in ch]; secs = []
    for i, p in enumerate(P):
        qa = qs[max(0, i - 1)]; qb = qs[min(len(qs) - 1, i)]; q = (qa + qb); q.z = 0
        if q.length < 1e-6: q = qb.copy()
        q.normalize(); cosh = max(0.5, q.dot(qb)); q = q / cosh
        secs.append([bm.verts.new(p + q * l + Vector((0, 0, z))) for l, z in ((a, z0), (b, z0), (b, z1), (a, z1))])
    nf = 0
    for i in range(len(secs) - 1):
        for j in range(4):
            try: f = bm.faces.new((secs[i][j], secs[i][(j + 1) % 4], secs[i + 1][(j + 1) % 4], secs[i + 1][j])); f.material_index = mi; nf += 1
            except ValueError: pass
    for k, s4 in ((0, secs[0]), (1, secs[-1])):
        f = bm.faces.new(s4 if k else list(reversed(s4))); f.material_index = mi
    return nf
def hz(v): v = v.copy(); v.z = 0; return v.normalized() if v.length > 1e-6 else v
# upstand top edges: boundary edges of vertical stucco faces near the deck side (s < 2.6)
up = []
for e in bm.edges:
    if not e.is_boundary: continue
    f = e.link_faces[0]
    if f.material_index != MI_ST or abs(f.normal.z) > 0.2: continue
    if max(su(v.co.x, v.co.y)[0] for v in e.verts) > 2.6: continue
    zf = [v.co.z for v in f.verts]
    if min(v.co.z for v in e.verts) < max(zf) - 0.02: continue
    bot = [g for ed in f.edges if ed is not e for g in ed.link_faces if g is not f and g.material_index == 0]
    if not bot: continue
    mid = (e.verts[0].co + e.verts[1].co) / 2; q = hz(bot[0].calc_center_median() - mid)
    if q.length < 0.5: continue
    up.append((e.verts[0], e.verts[1], q))
# step top edges: higher edge of vertical stucco step faces away from the deck edge (s > 2.6), height > 5 cm
st = []
for f in bm.faces:
    if f.material_index != MI_ST or abs(f.normal.z) > 0.2: continue
    if min(su(v.co.x, v.co.y)[0] for v in f.verts) < 2.6: continue
    zs = sorted(v.co.z for v in f.verts)
    if zs[-1] - zs[0] < 0.05: continue
    te = max(f.edges, key=lambda ed: min(v.co.z for v in ed.verts))
    if min(v.co.z for v in te.verts) < zs[-1] - 0.5 * (zs[-1] - zs[0]): continue
    oth = [g for g in te.link_faces if g is not f]
    if not oth: continue
    mid = (te.verts[0].co + te.verts[1].co) / 2; q = hz(oth[0].calc_center_median() - mid)
    if q.length < 0.5: continue
    st.append((te.verts[0], te.verts[1], q))
cu = chains(up); cs = chains(st)
nfu = sum(sweep(c, q, -0.04, 0.20, 0.0, 0.07, MI_CP) for c, q in cu)
nfb = sum(sweep(c, q, 0.005, 0.16, -0.45, 0.0, MI_ST) for c, q in cu)
nfs = sum(sweep(c, q, -0.05, 0.22, -0.02, 0.06, MI_CP) for c, q in cs)
print('ci upstand top edges', len(up), 'chains', len(cu), 'coping faces', nfu, 'parapet back faces', nfb, flush=True)
print('ci step top edges', len(st), 'chains', len(cs), 'verge coping faces', nfs, flush=True)
bm.normal_update()
# ---- 4a
z = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = z['tris']; ob = z['obj']; nm = z['names']; kp = np.array([not str(nm[i]).startswith('NT_') for i in ob]); T = T[kp]
RB = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3*i, 3*i+1, 3*i+2) for i in range(len(T))])
print('ci 4a roof (+ridge cap + coping) overlap pairs', len(BVHTree.FromBMesh(bm).overlap(RB)), flush=True)
bm.transform(Mi); bm.to_mesh(me); bm.free(); me.update()
# ridge cap colour: the eave-course shader reads FACE attribute 'tcol' (median MEASURED from the eave course, per-cap jitter like its spread)
at = me.attributes.get('tcol') or me.attributes.new('tcol', 'FLOAT_COLOR', 'FACE')
rng = np.random.default_rng(19)
jit = rng.normal(0, 1, (ncap + 2, 3)) * np.array([0.05, 0.02, 0.007]); MED = np.array([0.416, 0.129, 0.069])
ctr = np.zeros(len(me.polygons) * 3); me.polygons.foreach_get('center', ctr); ctr = ctr.reshape(-1, 3)
mi = np.zeros(len(me.polygons), int); me.polygons.foreach_get('material_index', mi)
col = np.zeros((len(me.polygons), 4)); Mw = np.array(M)
cw = ctr @ Mw[:3, :3].T + Mw[:3, 3]
sel = mi == MI_RC
ci_ = np.zeros(len(mi), int)
CQ = np.array([q[:] for q, a, t in CAPS]); CA = np.array([a[:] for q, a, t in CAPS]); CT = np.array([t for q, a, t in CAPS])
CC = CQ + CA * (CT[:, None] + PITCH / 2)
for fi in np.nonzero(sel)[0]: ci_[fi] = int(np.argmin(((CC - cw[fi]) ** 2).sum(1)))
col[sel, :3] = np.clip(MED + jit[ci_[sel]], 0, 1); col[:, 3] = 1
at.data.foreach_set('color', col.ravel().astype(np.float32)); me.update()
print('ci tcol set on ridge cap faces', int(sel.sum()), flush=True)
for nm2 in ['Alexander Kasser Theater walls', 'Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course']:
    o = bpy.data.objects[nm2]; b2 = bmesh.new(); b2.from_mesh(o.data); b2.transform(o.matrix_world)
    print('ci 4a', nm2[:40], 'overlap pairs', len(BVHTree.FromBMesh(b2).overlap(RB)), flush=True); b2.free()
ro['ci_ridge_coping'] = f'ridge+hip caps {ncap}; upstand coping {len(up)} edges; step verge coping {len(st)} edges; hip planes ' + ('; '.join(f'{k}: z={c[0]:.3f}{c[1]:+.5f}x{c[2]:+.5f}y' for k, c in PL.items()) if HIP else 'off')
if SAVE: bpy.ops.wm.save_mainfile(); print('ci main: SAVED', flush=True)
